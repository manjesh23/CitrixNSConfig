#!/usr/local/bin/python3.9

import subprocess as sp
from urllib import request
import json
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'

class EmailSender:
    def __init__(self, cc, receiver):
        self.sender = 'warranty_check@citrix.com'
        self.receiver = receiver
        self.cc = cc
        self.bcc = ['manjesh.n@cloud.com']
        self.user = 'warranty_check@cloud.com'
        self.tasktype = 'Warranty Check Task'
        self.smtp_server = 'mail.citrix.com'
        self.smtp_port = 25

    def send_email(self, subject, body):
        try:
            # Create the MIME object
            message = MIMEMultipart()
            message['From'] = self.sender
            message['To'] = self.receiver
            message['Cc'] = ', '.join(self.cc)
            message['Bcc'] = ', '.join(self.bcc)
            message['Subject'] = subject
            message.attach(MIMEText(body, 'html'))
            # Connect to the SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                to_addresses = [self.receiver] + self.cc + self.bcc
                server.sendmail(self.sender, to_addresses, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print("Error: Unable to send email.")
            print(e)

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

# Pull user email from Salesforce func
def sdfc_to_email(Id):
    sfdc_outdata = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": "" + sfdctoken + "", "isbase64": "false"},
                                                                  {"name": "selectfields", "value": "Email, FederationIdentifier", "isbase64": "false"},
                                                                  {"name": "tablename", "value": "user", "isbase64": "false"},
                                                                  {"name": "selectcondition", "value": "Id = '" + Id + "'", "isbase64": "false"}]}
    jsondata = json.dumps(sfdc_outdata)
    jsondataasbytes = jsondata.encode('utf-8')
    finaldata = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0]
    finaldata = json.loads(finaldata)
    return str(finaldata["FederationIdentifier"])

# Run the command and capture the output
command = '''find /upload/ftp/8217975* -type d -name 'collector_*' -prune -exec sh -c 'file_path="{}"; sysctl_file="$file_path/shell/sysctl-a.out"; if [ -f "$sysctl_file" ]; then pattern_value=$(awk "/netscaler.serial/{print \$NF}" "$sysctl_file"); [ -n "$pattern_value" ] && [ $(echo "$pattern_value" | awk "{print length}") -le 10 ] && echo "$pattern_value, \\"$file_path\\""; fi' \;'''
platformserial_bundlepath = sp.run(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.decode('utf-8', 'replace')

# Split the output into lines
lines = platformserial_bundlepath.strip().split('\n')

# Dictionary for each case number's information
case_info_dict = {}

# Iterate through lines and extract values
for line in lines:
    values = line.split(', ')
    if len(values) == 2:
        platformserial, bundle_path = values
        casenum = bundle_path.strip().split("/")[3]
        print("Checking case# " + casenum)

        # Engine to find and validate serial number
        platformserial_json = {
            "feature": "selectcasequery",
            "parameters": [
                {"name": "salesforcelogintoken", "value": sfdctoken, "isbase64": "false"},
                {"name": "selectfields", "value": "Asset_ID__c,Maintenance_End_Date__c", "isbase64": "false"},
                {"name": "tablename", "value": "Asset_Component__c", "isbase64": "false"},
                {"name": "selectcondition", "value": "Name = '" + platformserial + "'", "isbase64": "false"}
            ]
        }
        jsondata = json.dumps(platformserial_json)
        jsondataasbytes = jsondata.encode('utf-8')
        try:
            platformserial_Maintenance_End_Date__c = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options']
            end_dates = []
            if platformserial_Maintenance_End_Date__c:
                for entry in platformserial_Maintenance_End_Date__c:
                    values = entry['values']
                    if values:
                        json_data = json.loads(values[0])
                        end_date = json_data.get('Maintenance_End_Date__c')
                        if end_date:
                            end_dates.append(end_date)
                try:
                    # Find the latest date
                    platformserial_Maintenance_End_Date__c = max(end_dates)
                    platformserial_Maintenance_End_Date__c = datetime.strptime(platformserial_Maintenance_End_Date__c, "%Y-%m-%d").date()
                    current_date = datetime.today().date()
                    if platformserial_Maintenance_End_Date__c > current_date:
                        continue
                    else:
                        platformserial_Maintenance_End_Date__c = str(platformserial_Maintenance_End_Date__c)
                except Exception as e:
                    print("Error processing Maintenance End Date:", e)
                    platformserial_Maintenance_End_Date__c = "Error"
            else:
                continue
        except IndexError:
            platformserial_Maintenance_End_Date__c = "Not a HW Model"

        if casenum in case_info_dict:
            case_info_dict[casenum].append(platformserial + " -- " + bundle_path + " -- <font color=\"red\">" + platformserial_Maintenance_End_Date__c + "</font>")
        else:
            case_info_dict[casenum] = [platformserial + " -- " + bundle_path + " -- <font color=\"red\">" + platformserial_Maintenance_End_Date__c + "</font>"]

# Salesforce case details
try:
    for casenum, info_list in case_info_dict.items():
        case_data = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": "" + sfdctoken + "", "isbase64": "false"},
                                                                    {"name": "selectfields", "value": "Account_Name__c,CaseNUmber,Case_Owner__c,emailReferenceId__c,Manager__c,OwnerId,Team_Lead__c,TECH_LastCommentBody__c",
                                                                    "isbase64": "false"},
                                                                    {"name": "tablename", "value": "Case", "isbase64": "false"},
                                                                    {"name": "selectcondition", "value": "CaseNumber = '" + casenum + "'", "isbase64": "false"}]}
        jsondata = json.dumps(case_data)
        jsondataasbytes = jsondata.encode('utf-8')
        response_data = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))
        if 'options' in response_data and response_data['options']:
            options = response_data['options']
            if 'values' in options[0] and options[0]['values']:
                values = options[0]['values']
                finaldata = json.loads(values[0])
                # Now you can continue with processing finaldata
            else:
                print("Error: No values in the response.")
        else:
            print("Error: No options in the response.")
        Account_Name__c = str(finaldata["Account_Name__c"])
        Case_Owner__c = str(finaldata["Case_Owner__c"])
        emailReferenceId__c = re.findall(r'\[.*00D30.*\]', str(finaldata["emailReferenceId__c"]))[0] if re.findall(r'\[.*00D30.*\]', str(finaldata["emailReferenceId__c"])) else None
        try:
            Team_Lead__c = str(sdfc_to_email(str(finaldata.get("Team_Lead__c", finaldata.get("Manager__c")))))
        except:
            Team_Lead__c = str(sdfc_to_email(str(finaldata["Manager__c"])))
        TECH_LastCommentBody__c = re.findall(r'\[.*00D30.*\]', str(finaldata["TECH_LastCommentBody__c"]))[0] if re.findall(r'\[.*00D30.*\]', str(finaldata["TECH_LastCommentBody__c"])) else None
        Manager__c = str(sdfc_to_email(str(finaldata["Manager__c"])))
        OwnerId = str(sdfc_to_email(str(finaldata["OwnerId"])))
        email_subject = f"Action Required: Expired Entitlements | {casenum} | {Account_Name__c} | {Case_Owner__c} | {emailReferenceId__c}"
        email_body = (
            f"Hello {Case_Owner__c},<br><br>"
            f"We are writing to inform you that case number {casenum} has a collector bundle uploaded on the SJAnalysis server containing an expired entitlement serial number. To ensure a seamless resolution, we kindly request you to review the provided information and adhere to the entitlement guidelines.<br><br>"
            f"{('<br>'.join(info_list))}<br>"
            f"<br><br>To expedite the process, please engage with the sales/accounts team promptly to initiate the renewal process. It is crucial to verify the hardware serial number within the collector bundle before proceeding with any further support.<br><br>"
            f"Kindly note that this is an auto-generated email, and we request that you refrain from replying directly to this message."
        )
        cc = [Manager__c, Team_Lead__c, 'technicalsupport@citrix.com']
        receiver = OwnerId
        EmailSender(cc, receiver).send_email(email_subject, email_body)
finally:
    pass