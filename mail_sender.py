"""
==============================================================
  Internship Application Auto-Mailer
  Author : Dev Shukla
  Purpose: Send internship application emails with resume
           to a list of recipients automatically.
==============================================================

SETUP INSTRUCTIONS:
  1. Install dependency  :  pip install secure-smtplib  (usually built-in)
  2. Enable App Password  :  Gmail > Google Account > Security >
                             2-Step Verification > App Passwords
                             (Search "App Passwords" in your Google Account)
  3. Fill in CONFIG below :  YOUR_EMAIL, APP_PASSWORD, RESUME_PATH
  4. Add recipient emails :  Edit the RECIPIENT_EMAILS list
  5. Run                  :  python mail_sender.py
"""

import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ─────────────────────────────────────────────
#   ✏️  CONFIGURATION  — EDIT THIS SECTION
# ─────────────────────────────────────────────

CONFIG = {
    "YOUR_EMAIL"    : "devs44236@gmail.com",   # Your sender email
    "APP_PASSWORD"  : "xxzo qazt zmvd uqft",        # Gmail App Password (NOT your login password)
    "SMTP_SERVER"   : "smtp.gmail.com",
    "SMTP_PORT"     : 587,
    "RESUME_PATH"   : r"C:\Users\Dev Shukla\Videos\RustDesk\Dev_Shukla_Resume.pdf",
    "DELAY_SECONDS" : 35,  # Delay between each email — 60s recommended to avoid spam filters
}

# ─────────────────────────────────────────────
#   📋  RECIPIENT EMAIL LIST  — ADD EMAILS HERE
# ─────────────────────────────────────────────

RECIPIENT_EMAILS = [
    # "cybercell@police.gov.in",
    # "ssp.cybercrime@up.gov.in",
    # Add as many emails as needed — one per line, inside quotes, followed by a comma
    # Example:
    # "hr@example.com",
    # "recruiter@company.com",
    "byteviper28@gmail.com",
    "byteviper4@gmail.com",
    "testsher123456@gmail.com"
]

# ─────────────────────────────────────────────
#   📧  EMAIL CONTENT  — Subject & Body
# ─────────────────────────────────────────────

SUBJECT = "Application for Cybersecurity Internship – June–July 2026 | Dev Shukla"

# Plain-text version (for email clients that don't render HTML)
BODY_PLAIN = """\
Dear Sir/Madam,

I am writing to express my strong interest in joining the Cyber Cell as an intern (June–July 2026). I am a B.Tech Cybersecurity student (8.44 CPI) with real-world experience in vulnerability assessment, threat intelligence, and digital forensics.

Why I’d be a strong addition to your team:
- Proven Experience: Penetration Testing Intern at ShadowFox & Cyber Security Consultant at The Angaar Batch. I actively find and patch critical vulnerabilities.
- Hands-On Builder: Developed Hack!tUp (a secure CTF platform with 875+ users) and PhishReconn (a dynamic phishing detection system).
- Certified Expert: Hold active certifications in Network Security, Blue Teaming, and Web App Pentesting (SecOps Group & Sturtles Security).
- Tool Arsenal: Highly proficient with Burp Suite, Wireshark, Metasploit, Autopsy, Splunk, and Ghidra.

I am eager to bring my offensive security and investigative skills to the Cyber Cell and learn from real-world law enforcement operations. My resume is attached for your review.

I would welcome the opportunity to discuss how I can contribute to your investigations and security initiatives.

Thank you for your time.

Yours sincerely,
Dev Shukla
+91-7607859041
devs44236@gmail.com
"""

# HTML version (renders nicely in most email clients)
BODY_HTML = """\
<html>
<body style="font-family: Arial, sans-serif; font-size: 15px; color: #1a1a1a; line-height: 1.8; max-width: 720px; margin: auto;">

<p>Dear Sir/Madam,</p>

<p>
I am writing to express my strong interest in joining the <strong>Cyber Cell as an intern (June–July 2026)</strong>.
I am a <strong>B.Tech Cybersecurity student (8.44 CPI)</strong> with real-world experience in vulnerability assessment, threat intelligence, and digital forensics.
</p>

<p><strong>Why I’d be a strong addition to your team:</strong></p>
<ul style="margin-top: 0;">
  <li style="margin-bottom: 8px;"><strong>Proven Experience:</strong> Penetration Testing Intern at ShadowFox &amp; Cyber Security Consultant at The Angaar Batch. I actively find and patch critical vulnerabilities.</li>
  <li style="margin-bottom: 8px;"><strong>Hands-On Builder:</strong> Developed <strong>Hack!tUp</strong> (a secure CTF platform with 875+ users) and <strong>PhishReconn</strong> (a dynamic phishing detection system).</li>
  <li style="margin-bottom: 8px;"><strong>Certified Expert:</strong> Hold active certifications in Network Security, Blue Teaming, and Web App Pentesting (SecOps Group &amp; Sturtles Security).</li>
  <li style="margin-bottom: 8px;"><strong>Tool Arsenal:</strong> Highly proficient with Burp Suite, Wireshark, Metasploit, Autopsy, Splunk, and Ghidra.</li>
</ul>

<p>
I am eager to bring my offensive security and investigative skills to the Cyber Cell and learn from real-world law enforcement operations. My resume is attached for your review.
</p>

<p>I would welcome the opportunity to discuss how I can contribute to your investigations and security initiatives.</p>

<p>Thank you for your time.</p>

<p>
Yours sincerely,<br>
<strong>Dev Shukla</strong><br>
📞 +91-7607859041<br>
✉️ <a href="mailto:devs44236@gmail.com" style="color: #0056b3; text-decoration: none;">devs44236@gmail.com</a>
</p>

</body>
</html>
"""

# ─────────────────────────────────────────────
#   🔧  CORE FUNCTIONS
# ─────────────────────────────────────────────

def build_email(sender: str, recipient: str, resume_path: str) -> MIMEMultipart:
    """Construct the MIME email with plain text, HTML, and resume attachment."""
    msg = MIMEMultipart("alternative")
    msg["From"]    = sender
    msg["To"]      = recipient
    msg["Subject"] = SUBJECT

    # Attach both plain-text and HTML parts (HTML takes priority in modern clients)
    msg.attach(MIMEText(BODY_PLAIN, "plain"))
    msg.attach(MIMEText(BODY_HTML,  "html"))

    # Attach the resume file
    try:
        with open(resume_path, "rb") as resume_file:
            attachment = MIMEBase("application", "octet-stream")
            attachment.set_payload(resume_file.read())
        encoders.encode_base64(attachment)
        filename = os.path.basename(resume_path)
        attachment.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(attachment)
        print(f"  📎 Resume attached: {filename}")
    except FileNotFoundError:
        print(f"  ⚠️  WARNING: Resume not found at '{resume_path}'. Sending without attachment.")

    return msg


def send_emails():
    """Main function — connects to SMTP and sends to all recipients."""

    # ── Preflight checks ───────────────────────────────────────────────
    if not RECIPIENT_EMAILS:
        print("❌ RECIPIENT_EMAILS list is empty. Add email addresses and try again.")
        return

    if CONFIG["APP_PASSWORD"] == "your_app_password_here":
        print("❌ Please set your Gmail App Password in the CONFIG section.")
        return

    if not os.path.isfile(CONFIG["RESUME_PATH"]):
        print(f"⚠️  Resume not found at: {CONFIG['RESUME_PATH']}")
        ans = input("   Continue sending WITHOUT resume? (y/n): ").strip().lower()
        if ans != "y":
            print("Aborted. Fix the RESUME_PATH and try again.")
            return

    # ── Connect to SMTP ────────────────────────────────────────────────
    print("\n🔌 Connecting to SMTP server...")
    try:
        server = smtplib.SMTP(CONFIG["SMTP_SERVER"], CONFIG["SMTP_PORT"])
        server.ehlo()
        server.starttls()
        server.login(CONFIG["YOUR_EMAIL"], CONFIG["APP_PASSWORD"])
        print("✅ Logged in successfully.\n")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Check your App Password and email.")
        return
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    # ── Send loop ──────────────────────────────────────────────────────
    total     = len(RECIPIENT_EMAILS)
    success   = 0
    failed    = []

    for idx, recipient in enumerate(RECIPIENT_EMAILS, start=1):
        recipient = recipient.strip()
        if not recipient:
            continue

        print(f"📤 [{idx}/{total}] Sending to: {recipient}")
        try:
            msg = build_email(CONFIG["YOUR_EMAIL"], recipient, CONFIG["RESUME_PATH"])
            server.sendmail(CONFIG["YOUR_EMAIL"], recipient, msg.as_string())
            print(f"  ✅ Sent successfully!\n")
            success += 1
        except Exception as e:
            print(f"  ❌ Failed: {e}\n")
            failed.append(recipient)

        # Polite delay between sends (avoids spam flags)
        if idx < total:
            print(f"  ⏳ Waiting {CONFIG['DELAY_SECONDS']}s before next email...")
            time.sleep(CONFIG["DELAY_SECONDS"])

    server.quit()

    # ── Summary ────────────────────────────────────────────────────────
    print("=" * 50)
    print(f"📊 DONE! {success}/{total} emails sent successfully.")
    if failed:
        print(f"\n❌ Failed to send to {len(failed)} recipient(s):")
        for email in failed:
            print(f"   • {email}")
    print("=" * 50)


# ─────────────────────────────────────────────
#   🚀  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  📧  Internship Application Mailer  ")
    print("=" * 50)
    print(f"  Sender  : {CONFIG['YOUR_EMAIL']}")
    print(f"  Resume  : {CONFIG['RESUME_PATH']}")
    print(f"  Subject : {SUBJECT[:60]}...")
    print(f"  Total   : {len(RECIPIENT_EMAILS)} recipient(s)")
    print("=" * 50)

    confirm = input("\nReady to send? Type 'yes' to proceed: ").strip().lower()
    if confirm == "yes":
        send_emails()
    else:
        print("Cancelled. No emails were sent.")
