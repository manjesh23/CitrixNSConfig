from urllib import request
import json
import os
import openpyxl
import tarfile
import subprocess
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz

# Set timezone (for example, 'UTC', you might need to adjust this based on your requirements)
timezone = pytz.timezone('UTC')

# Calculate the current datetime and the datetime 2 months ago with timezone awareness
now = datetime.now(timezone)
two_months_ago = now - relativedelta(months=2)

# Get SFDC API keys
try:
    sfdcurl = "https://ftltoolswebapi.deva.citrite.net/sfaas/api/salesforce"
    tokenpayload = {
        "feature": "login",
        "parameters": [
            {"name": "tokenuri", "value": "https://login.salesforce.com/services/oauth2/token", "isbase64": "false"}
        ]
    }
    sfdcreq = request.Request(sfdcurl)
    sfdcreq.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(tokenpayload)
    jsondataasbytes = jsondata.encode('utf-8')
    sfdcreq.add_header('Content-Length', len(jsondataasbytes))
    sfdctoken = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0]
except Exception as e:
    print("Unable to get SFDC Token")
    print(e)

# Function to check if bundle present or not
def find_collector_file(directory):
    try:
        # Ensure the directory exists
        if not os.path.isdir(directory):
            return None
        # Iterate over the files in the directory
        for filename in os.listdir(directory):
            if filename.startswith("collector_"):
                full_path = os.path.join(directory, filename)
                if os.path.exists(full_path):
                    return full_path
    except Exception as e:
        print(f"Error in find_collector_file: {e}")
    return None

# Function to check upload archive
def check_archive(caseNumber):
    find_command = f"find /upload/archive -maxdepth 2 -type f -regex '.*/[1-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/{caseNumber}.tar.gz' -print -quit 2>/dev/null"
    result = subprocess.run(find_command, shell=True, capture_output=True, text=True)
    archive_file = result.stdout.strip()
    if archive_file:
        archive_dir = os.path.dirname(archive_file)        
        try:
            with tarfile.open(archive_file, "r:gz") as tar:
                for member in tar.getmembers():
                    if "collector_" in member.name and "ns_runn" in member.name:
                        full_path = os.path.join(archive_dir, member.name)
                        return full_path
        except (tarfile.TarError, FileNotFoundError) as e:
            print(f"Error opening the tar file: {e}")
    return None

# Main engine
def accountID_to_bundle_path(each_accountID, ws):
    try:
        # Define the case_number dictionary
        case_number = {
            "feature": "selectcasequery",
            "parameters": [
                {"name": "salesforcelogintoken", "value": sfdctoken, "isbase64": "false"},
                {"name": "selectfields", "value": "Account_Name__c,Account_Org_ID__c,CaseNumber,ClosedDate,IsClosed", "isbase64": "false"},
                {"name": "tablename", "value": "Case", "isbase64": "false"},
                {"name": "selectcondition", "value": f"Account_Org_ID__c = '{each_accountID}'", "isbase64": "false"}
            ]
        }
        # Convert to JSON and encode
        jsondata = json.dumps(case_number)
        jsondataasbytes = jsondata.encode('utf-8')
        # Send the request and decode the response
        response = request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore")
        # Parse JSON response
        options = json.loads(response).get('options', [])
        for option in options:
            values = option.get('values', [])
            for value in values:
                try:
                    # Convert the value to a Python dictionary
                    finaldata = json.loads(value)
                    if finaldata:
                        Account_Name__c = finaldata.get("Account_Name__c", "")
                        Account_Org_ID__c = finaldata.get("Account_Org_ID__c", "")
                        CaseNumber = finaldata.get("CaseNumber", "")
                        IsClosed = finaldata.get("IsClosed", False)
                        ClosedDate = finaldata.get("ClosedDate", None)
                        #Bundle_Path = check_archive(CaseNumber)
                        Bundle_Path = find_collector_file(f'/upload/ftp/{CaseNumber}')
                        """ if ClosedDate:
                            ClosedDate = parser.isoparse(ClosedDate).astimezone(timezone)
                        Bundle_Path = None
                        if IsClosed:
                            Bundle_Path = find_collector_file(f'/upload/ftp/{CaseNumber}')
                        elif not IsClosed:
                            Bundle_Path = check_archive(CaseNumber) """
                        ws.append([Account_Name__c, Account_Org_ID__c, CaseNumber, Bundle_Path])
                    else:
                        print(f"No data found for account ID {each_accountID}.")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON value: {e}")
                except Exception as e:
                    print(f"Error processing value: {e}")
    except Exception as e:
        print(f"Error processing account ID {each_accountID}: {e}")

# Create Excel workbook and sheet
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Account Data"
ws.append(["Account_Name", "Account_Org_ID", "CaseNumber", "Bundle_Path"])

# Get each account ID from accountID.txt file
accountID_file_Path = 'accountID.txt'
with open(accountID_file_Path) as f:
    accountID = f.readlines()
    for each_accountID in accountID:
        accountID_to_bundle_path(each_accountID.strip(), ws)

# Save the Excel workbook
excel_file_path = 'account_data.xlsx'
wb.save(excel_file_path)
print(f"Data saved to {excel_file_path}")
