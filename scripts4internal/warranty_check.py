#!/usr/local/bin/python3.9

import subprocess as sp
from urllib import request
import json, os, time
import re
from datetime import datetime
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dateutil import tz
from dateutil.parser import parse

# About Author
scriptauthor = '''
___  ___            _           _       _____      _   _
|  \/  |           (_)         | |     /  ___|    | | | |
| .  . | __ _ _ __  _  ___  ___| |__   \ `--.  ___| |_| |_ _   _
| |\/| |/ _` | '_ \| |/ _ \/ __| '_ \   `--. \/ _ \ __| __| | | |
| |  | | (_| | | | | |  __/\__ \ | | | /\__/ /  __/ |_| |_| |_| |
\_|  |_/\__,_|_| |_| |\___||___/_| |_| \____/ \___|\__|\__|\__, |
                  _/ |                                      __/ |
                 |__/                                      |___/
#################################################################
##                                                             ##
##     Script credit: Manjesh Setty | manjesh.n@citrix.com     ##
##                                                             ##
#################################################################
'''

# tooltrack data
url = 'https://tooltrack.deva.citrite.net/use/warranty_check'
headers = {'Content-Type': 'application/json'}
version = "3.1"

# Tooltrack send data function (embeded with fail proof)
def send_request(version, username, fate_message, result):
    payload = {"version": version, "user": username, "action": f"{fate_message} -- {os.getcwd()}", "runtime": 0, "result": result, "format": "string", "sr": os.getcwd().split("/")[3]}
    try:
        data = json.dumps(payload).encode()
        req = request.Request(url, data=data, headers=headers)
        with request.urlopen(req, timeout=3) as response:
            response_text = response.read().decode()
    finally:
        return True

# About script
scriptabout = '''

  _____           _           _                                        _                 _               _    
 |  __ \         (_)         | |                                      | |               | |             | |   
 | |__) | __ ___  _  ___  ___| |_  __      ____ _ _ __ _ __ __ _ _ __ | |_ _   _     ___| |__   ___  ___| | __
 |  ___/ '__/ _ \| |/ _ \/ __| __| \ \ /\ / / _` | '__| '__/ _` | '_ \| __| | | |   / __| '_ \ / _ \/ __| |/ /
 | |   | | | (_) | |  __/ (__| |_   \ V  V / (_| | |  | | | (_| | | | | |_| |_| |  | (__| | | |  __/ (__|   < 
 |_|   |_|  \___/| |\___|\___|\__|   \_/\_/ \__,_|_|  |_|  \__,_|_| |_|\__|\__, |   \___|_| |_|\___|\___|_|\_\\
                _/ |                                                        __/ |_____                        
               |__/                                                        |___/______|                       
                                                   

######################################################################################################
##                                                                                                  ##
##   Note -- Please do not use this script if you are not sure of what you are doing.               ##
##   Product -- Only for NetScaler TAC Use.                                                         ##
##   Unauthorized usage of this script / sharing for personal use will be considered as offence.    ##
##   This script is designed to validate serial number entitlement from support bundle.             ##
##                                                                                                  ##
##                                                                                                  ##
##                                      Version:  ''' + version + '''                                               ##
##                   https://info.citrite.net/display/supp/Project+warranty_check                   ##
##                                                                                                  ##
##                                                                                                  ##
##                                                                                                  ##
##                                                                                                  ##
######################################################################################################
'''

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
        self.user = 'warranty_check@cloud.com'
        self.tasktype = 'Warranty Check Task'
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
                to_addresses = [self.receiver] + self.cc
                server.sendmail(self.sender, to_addresses, message.as_string())
            print("Email sent successfully! --> " + actual_data)
        except Exception as e:
            print("Error: Unable to send email.")
            print(e)

# Conver anytimezone to GMT
def convert_to_gmt(timestamp_str):
    # Parse the timestamp string
    timestamp = parse(timestamp_str)
    gmt_timestamp = timestamp.astimezone(tz.tzutc())
    return gmt_timestamp.strftime('%Y-%m-%d %H:%M:%S')

# Parser args
parser = argparse.ArgumentParser(description="NetScaler Support Bundle Warranty Check Script", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--sbpath', action="append", help="Input SJAnalysis NetScaler Support Bundle Path")
parser.add_argument('--about', action="store_true", help="About script details")
parser.add_argument('--author', action="store_true", help=argparse.SUPPRESS)
args = parser.parse_args()

# Getting right values assigned to variable
sbpath = ' '.join(args.sbpath) if args.sbpath else ""

# Set righ collector bundle root path
try:
    if "collector_" in sbpath:
        os.chdir(re.search('.*\/collecto.*_[0-9]{2}', sbpath).group(0))
except AttributeError as e:
    print(style.RED + "Collector Bundle not in Correct Naming Convention" + style.RESET)
    os.chdir(re.search('.*\/collecto.*_[0-9|_|\-|a-zA-Z|\.]{1,30}', sbpath).group(0))
except FileNotFoundError as e:
    print(style.RED + "Collector Bundle not in Correct Naming Convention" + style.RESET)
    os.chdir(re.search('.*\/collecto.*_[0-9|_|\-|a-z|\.]{1,30}', sbpath).group(0))
except ValueError:
    print("\nPlease navigate to correct support bundle path")
    quit()

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
    try:
        sfdc_outdata = {
            "feature": "selectcasequery",
            "parameters": [
                {"name": "salesforcelogintoken", "value": sfdctoken, "isbase64": "false"},
                {"name": "selectfields", "value": "Email, FederationIdentifier", "isbase64": "false"},
                {"name": "tablename", "value": "user", "isbase64": "false"},
                {"name": "selectcondition", "value": f"Id = '{Id}'", "isbase64": "false"}
            ]
        }
        jsondata = json.dumps(sfdc_outdata)
        jsondataasbytes = jsondata.encode('utf-8')
        response = request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore")
        finaldata = json.loads(response)['options'][0]['values'][0]
        finaldata = json.loads(finaldata)
        return str(finaldata.get("FederationIdentifier", ""))
    except (KeyError, TypeError, IndexError, ValueError) as e:
        # Case Owner might be TS Escalation Queue or it does not have an email ID
        return 'TS_Escalation_Queue@cloud.com'

# Run the command and capture the output
command = '''serial=$(awk '/netscaler.serial/{print $NF}' shell/sysctl-a.out); pwd=$(pwd); echo $serial, $pwd'''
platformserial_bundlepath = sp.run(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.decode('utf-8', 'replace')
serial = ''.join(platformserial_bundlepath.strip().split('\n'))
serial_string, bundle_path = serial.split(', ')
casenum = bundle_path.strip().split("/")[3]

current_date = datetime.today().date()
def get_entitlement_end_date_data(serial_string):
    # Engine to find and validate serial number
    case_info_dict = {}
    platformserial_json = {
        "feature": "selectcasequery",
        "parameters": [
            {"name": "salesforcelogintoken", "value": sfdctoken, "isbase64": "false"},
            {"name": "selectfields", "value": "Asset_ID__c,Maintenance_End_Date__c", "isbase64": "false"},
            {"name": "tablename", "value": "Asset_Component__c", "isbase64": "false"},
            {"name": "selectcondition", "value": "Name = '" + serial_string + "'", "isbase64": "false"}
        ]
    }
    pathformjsondata = json.dumps(platformserial_json).encode('utf-8')
    try:
        platformserial_Maintenance_End_Date__c = json.loads(request.urlopen(sfdcreq, pathformjsondata).read().decode("utf-8", "ignore"))['options']
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
                if platformserial_Maintenance_End_Date__c > current_date:
                    pass
                else:
                    platformserial_Maintenance_End_Date__c = str(platformserial_Maintenance_End_Date__c)
                    return {"serial": serial_string, "casenum": casenum, "bundle_path": bundle_path, "maintenance_end_date": platformserial_Maintenance_End_Date__c}
            except Exception as e:
                print("Error processing Maintenance End Date:", e)
                platformserial_Maintenance_End_Date__c = "Error"
        else:
            quit()
            check_SW_Support(casenum)
    except IndexError:
        platformserial_Maintenance_End_Date__c = "Not a HW Model"


# Salesforce case details
def SFDC_Case_Details(entitlement_end_date_details):
    if entitlement_end_date_details is not None:
        casenum = entitlement_end_date_details.get("casenum")
        if casenum is not None:
            casenum = entitlement_end_date_details["casenum"]
            case_data = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": "" + sfdctoken + "", "isbase64": "false"},
                                                                        {"name": "selectfields", "value": "Account_Name__c,Age__c,CaseNUmber,Case_Owner__c,CreatedDate,emailReferenceId__c,Manager__c,Offering_Level__c,OwnerId,Team_Lead__c,TECH_LastCommentBody__c",
                                                                        "isbase64": "false"},
                                                                        {"name": "tablename", "value": "Case", "isbase64": "false"},
                                                                        {"name": "selectcondition", "value": "CaseNumber = '" + casenum + "'", "isbase64": "false"}]}
            case_datajson = json.dumps(case_data).encode('utf-8')
            response_data = json.loads(request.urlopen(sfdcreq, case_datajson).read().decode("utf-8", "ignore"))
            if 'options' in response_data and response_data['options']:
                options = response_data['options']
                if 'values' in options[0] and options[0]['values']:
                    values = options[0]['values']
                    finaldata = json.loads(values[0])
                else:
                    print("Error: No values in the response.")
            else:
                print("Error: No options in the response.")
            Account_Name__c = str(finaldata["Account_Name__c"])
            Age__c = str(finaldata["Age__c"])
            Case_Owner__c = str(finaldata["Case_Owner__c"])
            CreatedDate = convert_to_gmt(str(finaldata["CreatedDate"]))
            emailReferenceId__c = re.findall(r'\[.*00D30.*\]', str(finaldata["emailReferenceId__c"]))[0] if re.findall(r'\[.*00D30.*\]', str(finaldata["emailReferenceId__c"])) else None
            try:
                Team_Lead__c = str(sdfc_to_email(str(finaldata.get("Team_Lead__c", finaldata.get("Manager__c")))))
            except:
                Team_Lead__c = str(sdfc_to_email(str(finaldata["Manager__c"])))
            Manager__c = str(sdfc_to_email(str(finaldata["Manager__c"])))
            Offering_Level__c = str(finaldata["Offering_Level__c"])
            OwnerId = str(sdfc_to_email(str(finaldata["OwnerId"])))
            email_subject = f"Action Required: Expired Entitlements HW | {casenum} | {Account_Name__c} | {Case_Owner__c} | {emailReferenceId__c}"
            if emailReferenceId__c is None:
                cc = [Manager__c, Team_Lead__c, 'manjesh.n@cloud.com']
                email_body = (
                f"Hello {Case_Owner__c},<br><br>"
                f"We are writing to inform you that case number {casenum} has a collector bundle uploaded on the SJAnalysis server containing an expired entitlement serial number. To ensure a seamless resolution, we kindly request you to review the provided information and adhere to the entitlement guidelines.<br><br>"
                f"{entitlement_end_date_details['serial']} -- {entitlement_end_date_details['casenum']} -- {entitlement_end_date_details['bundle_path']} -- <font color=\"red\"> {entitlement_end_date_details['maintenance_end_date']} </font> <br><br>"
                f"To expedite the process, please engage with the sales/accounts team promptly to initiate the renewal process. It is crucial to verify the hardware serial number within the collector bundle before proceeding with any further support.<br><br>"
                f"Unable to update case with this email as case does not have Email RefId<br><br>"
                f"Kindly note that this is an auto-generated email, and we request that you refrain from replying directly to this message."
                f'<p style="color: #ff0000; text-align: center;">&#x25AC; Strictly Internal | Don\'t Forward the same email to Customer &#x25AC;</p><br><br>'
            )
            else:
                cc = [Manager__c, Team_Lead__c, 'technicalsupport@citrix.com', 'manjesh.n@cloud.com']
                email_body = (
                f"Hello {Case_Owner__c},<br><br>"
                f"We are writing to inform you that case number {casenum} has a collector bundle uploaded on the SJAnalysis server containing an expired entitlement serial number. To ensure a seamless resolution, we kindly request you to review the provided information and adhere to the entitlement guidelines.<br><br>"
                f"{entitlement_end_date_details['serial']} -- {entitlement_end_date_details['casenum']} -- {entitlement_end_date_details['bundle_path']} -- <font color=\"red\"> {entitlement_end_date_details['maintenance_end_date']} </font> <br><br>"
                f"To expedite the process, please engage with the sales/accounts team promptly to initiate the renewal process. It is crucial to verify the hardware serial number within the collector bundle before proceeding with any further support.<br><br>"
                f"Kindly note that this is an auto-generated email, and we request that you refrain from replying directly to this message."
                f'<p style="color: #ff0000; text-align: center;">&#x25AC; Strictly Internal | Don\'t Forward the same email to Customer &#x25AC;</p><br><br>'
            )
            actual_data = f"{entitlement_end_date_details['serial']} -- {entitlement_end_date_details['casenum']} -- {entitlement_end_date_details['bundle_path']} -- {entitlement_end_date_details['maintenance_end_date']}"
            receiver = OwnerId
            EmailSender(cc, receiver).send_email(email_subject, email_body, actual_data)
            # Tooltrack
            try:
                fate_message = entitlement_end_date_details['serial'] + " -- " + Offering_Level__c + " -- " + Case_Owner__c + " -- " + Manager__c + " -- " + Age__c + " -- " + CreatedDate; send_request(version, Account_Name__c, fate_message, entitlement_end_date_details['maintenance_end_date'])
            finally:
                quit()

# Check SW Support via entitlement ID
def check_SW_Support(casenum):
    caseEntitlement_data = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": "" + sfdctoken + "", "isbase64": "false"},
                                                                        {"name": "selectfields", "value": "Account_Name__c,Age__c,CaseNUmber,Case_Owner__c,CreatedDate,EntitlementId,Entitlement_Level__c,emailReferenceId__c,Manager__c,OwnerId,Team_Lead__c,TECH_LastCommentBody__c",
                                                                        "isbase64": "false"},
                                                                        {"name": "tablename", "value": "Case", "isbase64": "false"},
                                                                        {"name": "selectcondition", "value": "CaseNumber = '" + casenum + "'", "isbase64": "false"}]}
    case_datajson = json.dumps(caseEntitlement_data).encode('utf-8')
    response_data = json.loads(request.urlopen(sfdcreq, case_datajson).read().decode("utf-8", "ignore"))
    if 'options' in response_data and response_data['options']:
        options = response_data['options']
        if 'values' in options[0] and options[0]['values']:
            values = options[0]['values']
            finaldata = json.loads(values[0])
        else:
            print("Error: No values in the response.")
    else:
        print("Error: No options in the response.")
    EntitlementId = str(finaldata["EntitlementId"])
    Entitlement_Level__c = str(finaldata["Entitlement_Level__c"])
    Account_Name__c = str(finaldata["Account_Name__c"])
    Age__c = str(finaldata["Age__c"])
    Case_Owner__c = str(finaldata["Case_Owner__c"])
    CreatedDate = convert_to_gmt(str(finaldata["CreatedDate"]))
    emailReferenceId__c = re.findall(r'\[.*00D30.*\]', str(finaldata["emailReferenceId__c"]))[0] if re.findall(r'\[.*00D30.*\]', str(finaldata["emailReferenceId__c"])) else None
    try:
        Team_Lead__c = str(sdfc_to_email(str(finaldata.get("Team_Lead__c", finaldata.get("Manager__c")))))
    except:
        Team_Lead__c = str(sdfc_to_email(str(finaldata["Manager__c"])))
    Manager__c = str(sdfc_to_email(str(finaldata["Manager__c"])))
    OwnerId = str(sdfc_to_email(str(finaldata["OwnerId"])))
    caseEntitlement_details = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": "" + sfdctoken + "", "isbase64": "false"},
                                                                        {"name": "selectfields", "value": "EndDate, Name",
                                                                        "isbase64": "false"},
                                                                        {"name": "tablename", "value": "Entitlement", "isbase64": "false"},
                                                                        {"name": "selectcondition", "value": "Id = '" + EntitlementId + "'", "isbase64": "false"}]}
    case_datajson = json.dumps(caseEntitlement_details).encode('utf-8')
    response_data = json.loads(request.urlopen(sfdcreq, case_datajson).read().decode("utf-8", "ignore"))
    if 'options' in response_data and response_data['options']:
        options = response_data['options']
        if 'values' in options[0] and options[0]['values']:
            values = options[0]['values']
            finaldata = json.loads(values[0])
        else:
            print("Error: No values in the response.")
    else:
        print("Error: No options in the response.")
    EndDate = str(finaldata["EndDate"])
    Name = str(finaldata["Name"])
    SWEndDate_Data = None
    try:
        SWEndDate = datetime.strptime(EndDate, "%Y-%m-%d").date()
        if SWEndDate > current_date:
            pass
        else:
            SWEndDate = str(SWEndDate)
            SWEndDate_Data = {"casenum": casenum, "EntitlementId": EntitlementId, "maintenance_end_date": SWEndDate, "Name": Name, "serial": "SW Entitlement"}
    except Exception as e:
        print("Error processing Maintenance End Date:", e)
    if SWEndDate_Data is not None:
        email_subject = f"Action Required: Expired Entitlements SW | {casenum} | {Account_Name__c} | {Case_Owner__c} | {emailReferenceId__c}"
        if emailReferenceId__c is None:
            cc = [Manager__c, Team_Lead__c, 'manjesh.n@cloud.com']
            email_body = (
            f"Hello {Case_Owner__c},<br><br>"
            f"We are writing to inform you that case number {casenum} has an expired entitlement configured. If the customer has renewed or purchased a new entitlement, please update the new entitlement ID on this ticket before we proceed with further technical assistance. To ensure a seamless resolution, we kindly request that you review the provided information and adhere to the entitlement guidelines.<br><br>"
            f"SW Entitlement Check -- {SWEndDate_Data['casenum']} -- {SWEndDate_Data['Name']} -- <font color=\"red\"> {SWEndDate_Data['maintenance_end_date']} </font> <br><br>"
            f"To expedite the process, please engage with the sales/accounts team promptly to initiate the renewal process. It is crucial to verify the hardware serial number within the collector bundle before proceeding with any further support.<br><br>"
            f"Unable to update case with this email as case does not have Email RefId<br><br>"
            f"Kindly note that this is an auto-generated email, and we request that you refrain from replying directly to this message."
            f'<p style="color: #ff0000; text-align: center;">&#x25AC; Strictly Internal | Don\'t Forward the same email to Customer &#x25AC;</p><br><br>'
        )
        else:
            cc = [Manager__c, Team_Lead__c, 'technicalsupport@citrix.com', 'manjesh.n@cloud.com']
            email_body = (
            f"Hello {Case_Owner__c},<br><br>"
            f"We are writing to inform you that case number {casenum} has an expired entitlement configured. If the customer has renewed or purchased a new entitlement, please update the new entitlement ID on this ticket before we proceed with further technical assistance. To ensure a seamless resolution, we kindly request that you review the provided information and adhere to the entitlement guidelines.<br><br>"
            f"SW Entitlement Check -- {SWEndDate_Data['casenum']} -- {SWEndDate_Data['Name']}  -- <font color=\"red\"> {SWEndDate_Data['maintenance_end_date']} </font> <br><br>"
            f"To expedite the process, please engage with the sales/accounts team promptly to initiate the renewal process. It is crucial to verify the hardware serial number within the collector bundle before proceeding with any further support.<br><br>"
            f"Kindly note that this is an auto-generated email, and we request that you refrain from replying directly to this message."
            f'<p style="color: #ff0000; text-align: center;">&#x25AC; Strictly Internal | Don\'t Forward the same email to Customer &#x25AC;</p><br><br>'
        )
        actual_data = f"{SWEndDate_Data['casenum']} -- {SWEndDate_Data['Name']} -- {SWEndDate_Data['maintenance_end_date']}"
        receiver = OwnerId
        EmailSender(cc, receiver).send_email(email_subject, email_body, actual_data)
        # Tooltrack
        try:
            fate_message = SWEndDate_Data['serial'] + " -- " + Case_Owner__c + " -- " + Manager__c + " -- " + Age__c + " -- " + CreatedDate; send_request(version, Account_Name__c, fate_message, SWEndDate_Data['maintenance_end_date'])
            print(fate_message)
        finally:
            quit()

if args.sbpath:
    if serial is not None:
        print("Checking case# " + casenum + " | " + str(args.sbpath))
        output_entitlement_end_date = get_entitlement_end_date_data(serial_string)
        if output_entitlement_end_date is not None:
            SFDC_Case_Details(output_entitlement_end_date)
        else:
            pass

elif args.author:
    print(sp.run(["lolcat"], input=scriptauthor, capture_output=True, text=True).stdout)

elif args.about:
    print(sp.run(["lolcat"], input=scriptabout, capture_output=True, text=True).stdout)

else:
    print(style.RED + 'Invalid Switch, please use --help' + style.RESET)
    quit()