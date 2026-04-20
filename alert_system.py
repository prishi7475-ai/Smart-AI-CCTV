import smtplib
from email.message import EmailMessage
import os

# ==================================================
# EMAIL CONFIGURATION
# ==================================================
SENDER_EMAIL = "smartsurvilance7@gmail.com"
SENDER_PASSWORD = "kevy kzzg ddtp nyac"


# ==================================================
# SEND ALERT EMAIL FUNCTION
# ==================================================
def send_alert_email(receiver_email, image_path, timestamp, emotion):

    if not receiver_email:
        print("❌ No receiver email provided")
        return

    if not os.path.exists(image_path):
        print("❌ Image not found:", image_path)
        return

    msg = EmailMessage()
    msg['Subject'] = "🚨 THREAT ALERT - Smart AI CCTV"
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email

    msg.set_content(
        f"""
🚨 THREAT ALERT DETECTED 🚨

Emotion Detected : {emotion}
Date & Time      : {timestamp}

Please check the attached screenshot.

Smart AI CCTV Surveillance System
        """
    )

    # Attach screenshot
    with open(image_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(image_path)

    msg.add_attachment(
        file_data,
        maintype='image',
        subtype='jpeg',
        filename=file_name
    )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        print("✅ Threat Email Sent Successfully")

    except Exception as e:
        print("❌ Email Sending Failed:", e)