#!/usr/local/bin/python3.9

from urllib import request
import json
import os

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    LIGHTRED = '\033[0;91m'
    GREEN = '\033[32m'
    LIGHTGREEN = '\033[0;92m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


# Get SFDC API Keys
try:
    sfdcurl = "https://ftltoolswebapi.deva.citrite.net/sfaas/api/salesforce"
    tokenpayload = {"feature": "login", "parameters": [{"name": "tokenuri", "value": "https://login.salesforce.com/services/oauth2/token", "isbase64": "false"}] }
    sfdcreq = request.Request(sfdcurl)
    sfdcreq.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(tokenpayload)
    jsondataasbytes = jsondata.encode('utf-8')
    sfdcreq.add_header('Content-Length', len(jsondataasbytes))
    sfdctoken = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0]
except:
    print(style.RED + "Unable to get SFDC Token" + style.RESET)

# Get case number from path
try:
    casenum = os.popen("pwd").read().split("/")[3]
except IndexError:
    print(style.RED + "Unable to get case number from your current working directory" + style.RESET)
# Get CaseAge and Entitlement Details
try:
    headers = {'Content-Type': 'application/json'}
    data = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": ""+sfdctoken+"", "isbase64": "false"}, {"name": "selectfields", "value": "EntitlementId,Age__c,Account_Name__c,Account_Org_ID__c,Case_Created_Date_Qual__c,Case_Owner__c,Case_Review_Flag__c,Case_Status__c,Case_Team__c,CaseReopened__c,Contact_Email__c,ContactCountry__c,ContactMobile,ContactPhone,Dev_Engineer__c,End_of_Support__c,Eng_Status__c,EngCase_SubmittedDate__c,Escalated_By__c,EscalatedDate__c,First_Response_Severity__c,First_Response_Time_Taken__c,Fixed_Known_Issue_ID__c,Frontline_to_Escalation_Severity__c,Frontline_to_Escalation_Violated__c,Highest_Severity__c,Initial_Severity__c,IsEscalated,IsEscalatedtoEng__c,IsPartner__c,KT_Applied__c,Last_Customer_Contact_Timestamp__c,Manager_Name__c,Number_of_Audits__c,Offering_Level__c,Product_Line_Name__c,Record_GEO__c,Serial_Number__c,ServiceProduct_Name__c,Target_GEO__c", "isbase64": "false"}, {"name": "tablename", "value": "Case", "isbase64": "false"}, {"name": "selectcondition", "value": "CaseNumber = '"+casenum+"'", "isbase64": "false"}]}
    jsondata = json.dumps(data)
    jsondataasbytes = jsondata.encode('utf-8')
    finaldata = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0]
    finaldata = json.loads(finaldata)
    EntitlementId = str(finaldata["EntitlementId"])
    Age__c = str(finaldata["Age__c"])
    Account_Name__c = str(finaldata["Account_Name__c"])
    Account_Org_ID__c = str(finaldata["Account_Org_ID__c"])