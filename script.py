import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from datetime import datetime

with open('sender_config.json') as f:
    sender_config = json.load(f)

with open('email_list.json') as f:
    email_list = json.load(f)

with open('email_template.txt') as f:
    template = f.read()

def ensure_sent_emails_file_exists():
    if not os.path.exists('sent_emails.txt'):
        with open('sent_emails.txt', 'w') as f:
            pass

def store_or_update_sent_email(recipient_email):
    ensure_sent_emails_file_exists()
    sent_emails = []
    email_found = False
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open('sent_emails.txt', 'r') as f:
        sent_emails = f.read().splitlines()

    with open('sent_emails.txt', 'w') as f:
        for line in sent_emails:
            if line.startswith(recipient_email):
                email_found = True
                parts = line.split(' | ')
                count = int(parts[2].split(': ')[1]) + 1 
                new_line = f"{recipient_email} | Last Sent: {current_time} | Count: {count}"
                f.write(new_line + '\n')
            else:
                f.write(line + '\n')

        if not email_found:
            new_line = f"{recipient_email} | Last Sent: {current_time} | Count: 1"
            f.write(new_line + '\n')

def email_already_sent(recipient_email):
    ensure_sent_emails_file_exists()
    with open('sent_emails.txt', 'r') as f:
        sent_emails = f.read().splitlines()
    for line in sent_emails:
        if line.startswith(recipient_email):
            return True
    return False

def send_birthday_email(sender_config, recipient_name, recipient_email):
    if sender_config.get("check_sent_mail", True) and email_already_sent(recipient_email):
        print(f"Email already sent to {recipient_email}. Skipping...")
        return
    
    email_body = template.replace("[Recipient's Name]", recipient_name).replace("[Your Name]", sender_config["sender_name"])
    message = MIMEMultipart()
    message['From'] = f"{sender_config['sender_name']} <{sender_config['sender_email']}>"
    message['To'] = f"{recipient_name} <{recipient_email}>"
    message['Subject'] = sender_config["subject"]
    message.attach(MIMEText(email_body, 'plain'))

    with smtplib.SMTP(sender_config["smtp_server"], sender_config["smtp_port"]) as server:
        server.starttls()
        server.login(sender_config["sender_email"], sender_config["smtp_password"])
        server.sendmail(sender_config["sender_email"], recipient_email, message.as_string())
        print(f"Email sent successfully to {recipient_email}")

    store_or_update_sent_email(recipient_email)

ensure_sent_emails_file_exists()

for recipient in email_list:
    for _ in range(sender_config["send_count"]):
        send_birthday_email(sender_config, recipient["name"], recipient["email"])

print("All birthday emails sent successfully!")
