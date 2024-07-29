from urllib import request
import json, os
import openpyxl

# Get SFDC API keys
try:
    sfdcurl = "https://ftltoolswebapi.deva.citrite.net/sfaas/api/salesforce"
    tokenpayload = {"feature": "login", "parameters": [{"name": "tokenuri", "value": "https://login.salesforce.com/services/oauth2/token", "isbase64": "false"}]}
    sfdcreq = request.Request(sfdcurl)
    sfdcreq.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(tokenpayload)
    jsondataasbytes = jsondata.encode('utf-8')
    sfdcreq.add_header('Content-Length', len(jsondataasbytes))
    sfdctoken = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0]
except Exception as e:
    print("Unable to get SFDC Token")
    print(e)

# function to check if bundle present or not
def find_collector_file(directory):
    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"Directory does not exist: {directory}")
        return None
    # Iterate over the files in the directory
    for filename in os.listdir(directory):
        if filename.startswith("collector_"):
            full_path = os.path.join(directory, filename)
            if os.path.exists(full_path):
                print(f"Full path: {full_path}")
                return full_path
    print("No collector file found")
    return None

# Main engine
def accountID_to_bundle_path(each_accountID, ws):
    finaldata = None
    try:
        case_number = {
            "feature": "selectcasequery",
            "parameters": [
                {"name": "salesforcelogintoken", "value": sfdctoken, "isbase64": "false"},
                {"name": "selectfields", "value": "Account_Name__c,Account_Org_ID__c,CaseNumber,IsClosed", "isbase64": "false"},
                {"name": "tablename", "value": "Case", "isbase64": "false"},
                # {"name": "selectcondition", "value": "Account_Org_ID__c = '{}' AND IsClosed = false".format(each_accountID), "isbase64": "false"} IsClosed = false
                {"name": "selectcondition", "value": "Account_Org_ID__c = '{}'".format(each_accountID), "isbase64": "false"}
            ]
        }
        jsondata = json.dumps(case_number)
        jsondataasbytes = jsondata.encode('utf-8')
        response = request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore")
        options = json.loads(response).get('options', [])
        if options and 'values' in options[0]:
            finaldata = json.loads(options[0]['values'][0])
    except Exception as e:
        print(f"Error processing account ID {each_accountID}: {e}")
    finally:
        if finaldata:
            Account_Name__c = str(finaldata["Account_Name__c"])
            Account_Org_ID__c = str(finaldata["Account_Org_ID__c"])
            CaseNumber = str(finaldata["CaseNumber"])
            Bundle_Path = find_collector_file(f'/upload/ftp/{CaseNumber}')
            if Bundle_Path:
                print(Bundle_Path)
            # Add data to the Excel sheet
            ws.append([Account_Name__c, Account_Org_ID__c, CaseNumber, Bundle_Path])

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
