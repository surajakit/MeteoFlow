import smtplib
import ssl
from email.message import EmailMessage

# -------------------------------
# Configuration Section
# -------------------------------

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "secfu178@gmail.com"  # Your Gmail address
SMTP_PASS = "msxkbpwmbaejksau"     # App Password with no spaces
FROM_EMAIL = "secfu178@gmail.com"

# Alert Configuration
alert_data = {
    "alert_type": "Flood",
    "location": "Miami",
    "timestamp": "2025-05-04 12:30 PM",
    "instructions": "Evacuate to the nearest shelter immediately."
}

# Email List
email_list = [
    {"email": "bhavyapandey22995@gmail.com", "region": "Dehradun"},
    {"email": "abeygoswami@gmail.com", "region": "Haldwani"},
    {"email": "surajgoswamiv1@gmail.com", "region": "uttarpradesh"}
]

# Email Template
email_template = """
Subject: Emergency Alert - {alert_type} in {location}

An emergency alert has been issued for your area.

Type: {alert_type}
Location: {location}
Time: {timestamp}
Instructions: {instructions}

Stay safe,
Emergency Services
"""

# -------------------------------
# Email Sending Logic
# -------------------------------

recipients = [entry["email"] for entry in email_list if entry["region"].lower() == alert_data["location"].lower()]

if not recipients:
    print("⚠️ No recipients found in the affected region.")
    exit()

subject = f"Emergency Alert - {alert_data['alert_type']} in {alert_data['location']}"
email_body = email_template.format(**alert_data)

context = ssl.create_default_context()
try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)

        for recipient in recipients:
            msg = EmailMessage()
            msg["From"] = FROM_EMAIL
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.set_content(email_body)

            try:
                server.send_message(msg)
                print(f"✔️ Alert sent to: {recipient}")
            except Exception as e:
                print(f"❌ Failed to send to {recipient}: {e}")
except Exception as e:
    print(f"🚫 Failed to connect to SMTP server: {e}")

