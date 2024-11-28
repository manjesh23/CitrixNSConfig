import psycopg2
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import ssl

# Disable SSL certificate validation globally
ssl._create_default_https_context = ssl._create_unverified_context

today = datetime.now().strftime("%b-%d-%Y")

# Connect to your PostgreSQL database
def connect_to_database():
    try:
        connection = psycopg2.connect(
            user="manjeshn",
            password="ThisisManjeshN",
            host="10.14.18.27",
            port="5432",
            database="tooltrack"
        )
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None

# Function to execute the query and write results to Excel file
def execute_query_and_write_to_xlsx(connection):
    try:
        cursor = connection.cursor()
        query = """
        SELECT timestamp, user_name, sr_number, action, result 
        FROM "ToolTrack_tooltrack" 
        WHERE tool_name_id = 'warranty_check' AND timestamp >= NOW() - INTERVAL '1 week'
        ORDER BY timestamp DESC;
        """
        cursor.execute(query)
        records = cursor.fetchall()
        # Create a DataFrame to hold the records
        df = pd.DataFrame(records, columns=['Timestamp', 'User_Name', 'SR_Number', 'Action', 'Result'])
        # Convert timestamp to timezone-unaware datetime objects
        df['Timestamp'] = df['Timestamp'].apply(lambda x: x.replace(tzinfo=None))
        # Split Bundle_Path to get Account Name and SerialNumber
        df['Bundle_Path'] = df['Action'].apply(lambda x: x.split(' -- ')[-1])
        df['SerialNumber'] = df['Action'].apply(lambda x: x.split(' -- ')[0])
        df['Account_Name'] = df['User_Name']
        df['Offering_Level'] = df['Action'].apply(lambda x: x.split(' -- ')[1])
        df['Case_Owner'] = df['Action'].apply(lambda x: x.split(' -- ')[2])
        df['Manager_Email'] = df['Action'].apply(lambda x: x.split(' -- ')[3])
        df['Case_Age'] = df['Action'].apply(lambda x: int(round(float(x.split(' -- ')[4]))))
        df['Date_Time_Opened (GMT)'] = pd.to_datetime(df['Action'].apply(lambda x: x.split(' -- ')[5]))
        # Rename columns
        df.rename(columns={'Timestamp': 'Email_Sent_Date (GMT)', 'Result': 'Expired_On'}, inplace=True)
        # Reorder columns
        df = df[['SR_Number', 'Account_Name', 'Offering_Level', 'Case_Age', 'Date_Time_Opened (GMT)', 'Case_Owner', 'Manager_Email', 'SerialNumber', 'Expired_On']].drop_duplicates(subset='SR_Number', keep='first')
        # Write DataFrame to Excel file
        excel_filename = f"{today}_warranty_check.xlsx"
        writer = pd.ExcelWriter(excel_filename, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Details')
        workbook = writer.book
        worksheet = writer.sheets['Details']
        # adjust the column widths based on the content
        for i, col in enumerate(df.columns):
            width = max(df[col].apply(lambda x: len(str(x))).max(), len(col))
            worksheet.set_column(i, i, width)
        writer.close()
        return excel_filename
    except (Exception, psycopg2.Error) as error:
        print("Error while executing query:", error)
        return None

# Function to send email with attached Excel file
def send_email_with_attachment(filename):
    # Email configurations
    from_email = "manjesh.n@cloud.com"
    to_email = "pradeep.bhambi@cloud.com, manjesh.n@cloud.com"
    cc_email = "bhagyaraj.isaiahm@cloud.com, anand.sathya@cloud.com, manjesh.n@cloud.com"
    subject = f"Consolidated Weekly Report for Project warranty_check for the Week {today}"
    
    # HTML version of the email body
    body = """
    <html>
      <body>
        Hello Pradeep,<br><br>
        Automated email: Weekly report for expired entitlements raised by our customers with technical support. Please find the attached Excel file containing the full details.
      </body>
    </html>
    """

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Cc"] = cc_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    # Open Excel file in binary mode and attach
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        message.attach(part)

    # Compile all recipients for sending
    all_recipients = to_email.split(", ") + cc_email.split(", ")

    # Send email using Gmail's SMTP server with SSL
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(from_email, "wqtk rnvq rpby hqhv")  # Use app password here
            smtp_server.sendmail(from_email, all_recipients, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    connection = connect_to_database()
    if connection:
        filename = execute_query_and_write_to_xlsx(connection)
        if filename:
            send_email_with_attachment(filename)
            # Delete the Excel file
            os.remove(filename)
        connection.close()

if __name__ == "__main__":
    main()
