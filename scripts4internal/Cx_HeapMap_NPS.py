import pyodbc
import json
from datetime import datetime

# Define connection parameters
server = '10.164.64.28'
database = 'Salesforce'

# Initialize conn to None
conn = None

# Create a connection string for Windows Authentication
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'

# Function to convert datetime to string
def datetime_converter(o):
    if isinstance(o, datetime):
        return o.strftime('%b-%d/%Y %H:%M:%S')  # Example: 'Aug-12/2023 12:54:04'
    raise TypeError(f"Type {type(o)} not serializable")

# Establish the connection
try:
    conn = pyodbc.connect(conn_str)
    print("Connected to the SQL Server successfully!")
    
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Corrected query with table name "Case" enclosed in square brackets
    cursor.execute("""
        SELECT 
            c.CaseNumber,
            c.Age__c,
            c.Account_Name__c,
            c.Case_Owner__c,
            c.Subject,
            c.Description,
            c.Survey_Count__c,
            c.Case_Created_Date_Qual__c,
            c.First_Response_Time_Taken__c,
            c.Time_to_Close__c,
            c.Time_to_Escalate__c,
            c.Last_Comment_Date_and_Time__c,
            c.TS_Survey_Time__c,
            s.CS_Survey_Satisfaction__c,
            s.Survey_Comment__c
        FROM 
            [Salesforce].[dbo].[Case] c  -- Table name enclosed in brackets
        JOIN 
            [Salesforce].[dbo].[Survey__c] s
        ON 
            c.Id = s.Case__c
        WHERE 
            c.Product_Line_Name__c IN ('Citrix ADC', 'Citrix Networking feature service')
            AND c.ClosedDate >= DATEADD(month, -60, GETDATE());
    """)

    # Fetch all rows
    rows = cursor.fetchall()

    # Column names
    columns = [column[0] for column in cursor.description]

    # Convert the rows into a list of dictionaries
    results = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        
        # Convert datetime fields to string if necessary
        for key, value in row_dict.items():
            if isinstance(value, datetime):
                row_dict[key] = value.strftime('%b-%d/%Y %H:%M:%S')
        
        results.append(row_dict)

    # Convert the list of dictionaries to JSON format
    json_data = json.dumps(results, default=datetime_converter, indent=4)

    # Print the JSON data
    print(json_data)

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    if conn:
        conn.close()
