import psycopg2
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email_with_attachment():
    # Email configurations
    from_email = "tejesh.doddikoppad@citrix.com"
    to_email = "samjose.ns@cloud.com"
    cc_email = "manjesh.n@cloud.com, tejesh.doddikoppad@cloud.com"
    subject = f"Hey Sam Jose, Its me Tejesh D"
    # HTML version of the email body
    body = """
    <html>
        <body>
            <h1>Hello Sam,</h1>
            <p>Got my mail !!!</p>
            <p>Best regards,</p>
            <p>Tejesh</p>
        </body>
    </html>
    """

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Cc"] = cc_email
    message["Subject"] = subject
    # Attach HTML body to email
    message.attach(MIMEText(body, "html"))
    text = message.as_string()
    # Send email
    with smtplib.SMTP("mail.citrix.com", 25) as server:
        server.starttls()
        server.sendmail(from_email, to_email.split(", ") + cc_email.split(", "), text)
    print("Email sent successfully!")

send_email_with_attachment()
