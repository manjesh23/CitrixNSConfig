from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


class EmailSender:
    def __init__(self, cc, receiver):
        self.sender = 'vignesh.kumar@citrix.com'
        self.receiver = receiver
        self.cc = cc
        self.user = 'tejesh.doddikoppad@citrix.com'
        self.tasktype = 'Task'
        self.smtp_server = 'mail.citrix.com'
        self.smtp_port = 25

    def send_email(self, subject, body, actual_data):
        try:
            # Create the MIME object
            message = MIMEMultipart()
            message['From'] = self.sender
            message['To'] = self.receiver
            message['Cc'] = ', '.join(self.cc)
            message['Subject'] = subject
            message.attach(MIMEText(body, 'html'))
            # Connect to the SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                #server.set_debuglevel(1) # Debug message for SSL
                to_addresses = [self.receiver] + self.cc
                server.sendmail(self.sender, to_addresses, message.as_string())
            print("Email sent successfully! --> " + actual_data)
        except Exception as e:
            print("Error: Unable to send email.")
            print(e)

cc=[]
receiver = "tejesh.doddikoppad@citrix.com"

email_subject = "Hi"
email_body = "Hello"
actual_data = "Hello again"

EmailSender(cc, receiver).send_email(email_subject, email_body, actual_data)