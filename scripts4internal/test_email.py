import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_team_email(teamname, email_body):
    # Email configurations
    sender = "manjesh.n@cloud.com"  # replace with actual sender's email
    recipients = "manjesh.n@cloud.com"
    cc_list = ["manjesh.n@cloud.com"]
    subject = "Test Email"

    # Create the email body as HTML
    body = MIMEText(email_body, 'html')
    msg = MIMEMultipart()
    msg.attach(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    msg['Cc'] = ', '.join(cc_list)
    
    # Compile all recipients for sending
    all_recipients = [recipients] + cc_list

    # Send email using Gmail's SMTP server
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, "wqtk rnvq rpby hqhv")  # use an app password for Gmail if possible
            smtp_server.sendmail(sender, all_recipients, msg.as_string())
        print(f"Team {teamname} untouched cases email sent - Success")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
email_body = """
<html>
  <body>
    <p>Hello Team,</p>
    <p>This is a test email.</p>
  </body>
</html>
"""

send_team_email("Support Team", email_body)
