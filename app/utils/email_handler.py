import smtplib
from ..config.settings import settings as st
from email.mime.text import MIMEText

def send_otp_to_email(email:str, name:str, OTP:str):
    html = f"""
        <html>
        <head>
            <meta charset="UTF-8" />
            <title>OTP Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5; padding: 20px;">
            <p>Hello <strong>{name}</strong>,</p>

            <p>Your one-time password (OTP) is:</p>

            <p style="
                font-size: 24px; 
                font-weight: bold; 
                border: 1px black solid; 
                box-sizing: border-box; 
                padding: 7px 15px; 
                display: inline-block; 
                color: #2c3e50; 
                margin: 30px 0;">
            {OTP}
            </p>

            <p>This code will expire in <strong>3 minutes</strong>.</p>

            <p>If you did not request this code, please ignore this email.</p>

            <br />
            <p>Thank you,<br />Grex Team</p>
        </body>
        </html>
    """

    message = MIMEText(html, "html")
    message["Subject"] = "Your One-Time Password (OTP) Code"
    message["From"] = st.GREX_EMAIL
    message["To"] = email

    try:
        with smtplib.SMTP(st.GMAIL_HOST, port=st.GMAIL_PORT) as conn:
            conn.starttls()
            conn.login(user=st.GREX_EMAIL, password=st.GREX_PASSWORD)
            refused_recipients = conn.sendmail(
                from_addr=st.GREX_EMAIL,
                to_addrs=email,
                msg=message.as_string()
            )

            if not refused_recipients:
                return True
            else:
                return False

    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")