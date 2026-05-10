import os
import time
import smtplib
import pandas as pd
from flask import Flask, render_template, request, Response, jsonify
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading
import queue

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

# Queue for SSE messages
messages_queue = queue.Queue()

# Store background task state
task_state = {
    'is_running': False
}

def send_sse_message(msg_type, content):
    messages_queue.put(f"event: {msg_type}\ndata: {content}\n\n")

def build_email(sender, recipient, subject, body_html, body_plain, resume_data, resume_filename):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Dev Shukla <{sender}>"
    msg["To"] = recipient
    msg["Subject"] = subject

    # Ensure valid string encoding
    msg.attach(MIMEText(body_plain, "plain", "utf-8"))
    msg.attach(MIMEText(body_html,  "html", "utf-8"))

    if resume_data and resume_filename:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(resume_data)
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", f'attachment; filename="{resume_filename}"')
        msg.attach(attachment)

    return msg

def email_worker(sender, password, emails, subject, body_html, delay, resume_data, resume_filename):
    task_state['is_running'] = True
    send_sse_message('info', 'Connecting to SMTP server...')
    
    import re
    # Create a plain text fallback from the HTML
    body_plain = body_html.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    body_plain = body_plain.replace('</p>', '\n\n').replace('</li>', '\n')
    body_plain = re.sub(r'<[^>]+>', '', body_plain)
    # Collapse 3+ newlines into exactly 2 newlines (standard paragraph gap)
    body_plain = re.sub(r'\n{3,}', '\n\n', body_plain).strip()

    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        send_sse_message('info', '✅ Logged in successfully.')
    except Exception as e:
        send_sse_message('error', f'❌ Authentication failed: {str(e)}')
        task_state['is_running'] = False
        send_sse_message('done', 'Finished with errors')
        return

    total = len(emails)
    success = 0

    for idx, recipient in enumerate(emails, start=1):
        if not task_state['is_running']:
            send_sse_message('error', 'Campaign terminated by user 🛑')
            break

        recipient = recipient.strip()
        if not recipient:
            continue
            
        send_sse_message('info', f'[{idx}/{total}] Sending to: {recipient}...')
        
        try:
            msg = build_email(sender, recipient, subject, body_html, body_plain, resume_data, resume_filename)
            server.sendmail(sender, recipient, msg.as_string())
            success += 1
            send_sse_message('success', f'✅ Successfully sent to {recipient}')
        except Exception as e:
            send_sse_message('error', f'❌ Failed to send to {recipient}: {str(e)}')
            
        if idx < total:
            for sec in range(delay, 0, -1):
                if not task_state['is_running']:
                    break
                send_sse_message('countdown', f'⏳ Cooldown: {sec}s remaining...')
                time.sleep(1)

    server.quit()
    send_sse_message('info', f'📊 DONE! {success}/{total} emails sent successfully.')
    send_sse_message('done', 'Campaign complete')
    task_state['is_running'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/terminate', methods=['POST'])
def terminate():
    task_state['is_running'] = False
    return jsonify({'message': 'Termination signal sent.'})

@app.route('/api/extract-emails', methods=['POST'])
def extract_emails():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        emails = []
        for col in df.columns:
            if 'email' in col.lower():
                emails.extend(df[col].dropna().astype(str).tolist())
        
        if not emails:
            import re
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            for col in df.columns:
                for val in df[col].dropna().astype(str):
                    matches = re.findall(email_pattern, val)
                    emails.extend(matches)
                    
        emails = list(set(emails)) # deduplicate
        return jsonify({'emails': emails})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send', methods=['POST'])
def start_sending():
    if task_state['is_running']:
        return jsonify({'error': 'A campaign is already running'}), 400

    sender = request.form.get('sender_email')
    password = request.form.get('app_password')
    delay = int(request.form.get('delay', 35))
    emails_str = request.form.get('emails', '')
    subject = request.form.get('subject', '')
    body_html = request.form.get('body_html', '')
    
    emails = [e.strip() for e in emails_str.replace(',', '\n').split('\n') if e.strip()]
    
    if not sender or not password or not emails:
        return jsonify({'error': 'Missing required fields (sender, password, or emails)'}), 400

    resume_data = None
    resume_filename = None
    if 'resume' in request.files and request.files['resume'].filename:
        resume_file = request.files['resume']
        resume_data = resume_file.read()
        resume_filename = resume_file.filename

    # Clear queue
    while not messages_queue.empty():
        messages_queue.get()

    threading.Thread(target=email_worker, args=(sender, password, emails, subject, body_html, delay, resume_data, resume_filename)).start()
    return jsonify({'message': 'Campaign started'})

@app.route('/api/stream')
def stream():
    def event_stream():
        while True:
            try:
                msg = messages_queue.get(timeout=10) # 10s keepalive to avoid disconnects
                yield msg
                if "event: done" in msg:
                    break
            except queue.Empty:
                yield "event: ping\ndata: {}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
