import os, re, json
from urllib import request, parse
import subprocess as sp
import pandas as pd

def grabber(caseNum):
    pattern = re.compile(r'collector_.*')
    base_path = f'/home/CITRITE/manjeshn/manscript/{caseNum}/'    
    try:
        all_directories = [os.path.join(base_path, d) for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        sorted_directories = sorted(all_directories, key=lambda x: os.path.basename(x))
        matching_directories = [d for d in sorted_directories if pattern.match(os.path.basename(d))]
        if matching_directories:
            directory_name = matching_directories[-1]
            return f"{directory_name}/shell/ns_running_config.conf"
        else:
            return None
    except FileNotFoundError:
        pass

def left_align_numbers(x):
    if isinstance(x, (int, float)):
        return f'{x:<10}'  # Adjust the width as needed
    else:
        return str(x)

excel_file_path = '/home/CITRITE/manjeshn/manscript/Archive_NS_Citrix.xlsx'
if os.path.exists(excel_file_path):
    os.remove(excel_file_path)

# Create an empty list to store DataFrames for each case
results_df_list = []

sfdcurl = "https://ftltoolswebapi.deva.citrite.net/sfaas/api/salesforce"
tokenpayload = {"feature": "login", "parameters": [{"name": "tokenuri", "value": "https://login.salesforce.com/services/oauth2/token", "isbase64": "false"}] }
sfdcreq = request.Request(sfdcurl)
sfdcreq.add_header('Content-Type', 'application/json; charset=utf-8')
jsondata = json.dumps(tokenpayload)
jsondataasbytes = jsondata.encode('utf-8')
sfdcreq.add_header('Content-Length', len(jsondataasbytes))
sfdctoken = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0]

with open('/home/CITRITE/manjeshn/manscript/caseList.txt', 'r') as caseList:
    for idx, case in enumerate(caseList, start=1):
        lb_vserver_count = 0
        cs_vserver_count = 0
        auth_vserver_count = 0
        ica_vpn_count = 0
        all_vpn_count = 0
        non_ica_vpn_vserver_count = 0
        case = case.strip()
        caseDir = grabber(case)
        if caseDir:
            try:
                os.chdir(caseDir)
            except:
                pass
            finally:
                os.chdir('/home/CITRITE/manjeshn/manscript/')
            print(f'Processing {idx}: {caseDir}')
            lb_vserver_count = sp.run('''awk '/add lb vserver/{count++} END{print count+0}' ''' + caseDir, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            cs_vserver_count = sp.run('''awk '/add cs vserver/{count++} END{print count+0}' ''' + caseDir, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            gslb_vserver_count = sp.run('''awk '/add gslb vserver/{count++} END{print count+0}' ''' + caseDir, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            auth_vserver_count = sp.run('''awk '/add authentication vserver/{count++} END{print count+0}' ''' + caseDir, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            waf_count = sp.run('''awk '/bind appfw profile/{print $4 | "sort | uniq | wc -l"; found=1} END {if (!found) print 0}' ''' + caseDir + ''' | sed "s/^[ \t]*//"''', shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            ica_vpn_count = sp.run('''awk '/bind vpn vserver/ && /staServer/ {print $4} END{print count+0}' ''' + caseDir + ''' | sort | uniq | wc -l''', shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            all_vpn_count = sp.run('''awk '/bind vpn vserver/{print $4} END{print count+0}' ''' + caseDir + ''' | sort | uniq | wc -l''', shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            try:
                non_ica_vpn_vserver_count = int(all_vpn_count) - int(ica_vpn_count)
            except:
                non_ica_vpn_vserver_count = 'NA'
            
            # OrgID from case number (Salesforce)
            data = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": ""+sfdctoken+"", "isbase64": "false"}, {"name": "selectfields", "value": "Account_Name__c,Account_Org_ID__c,Offering_Level__c", "isbase64": "false"}, {"name": "tablename", "value": "Case", "isbase64": "false"}, {"name": "selectcondition", "value": "CaseNumber = '"+case+"'", "isbase64": "false"}]}
            jsondata = json.dumps(data)
            jsondataasbytes = jsondata.encode('utf-8')
            finaldata = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0]
            finaldata = json.loads(finaldata)
            Account_Name__c = str(finaldata["Account_Name__c"])
            Account_Org_ID__c = str(finaldata["Account_Org_ID__c"])
            Offering_Level__c = str(finaldata["Offering_Level__c"])
            # Create a DataFrame for each case and append it to the list
            case_results_df = pd.DataFrame({'Case_Number': [case], 'Account_Org_ID': [Account_Org_ID__c], 'Account_Name': [Account_Name__c], 'Offering_Level': [Offering_Level__c], 'LB_vServer': [lb_vserver_count], 'CS_vServer': [cs_vserver_count], 'GSLB_vServer': [gslb_vserver_count], 'Auth_vServer': [auth_vserver_count], 'WAF_Count': [waf_count], 'ICA_VPN_vServer': [ica_vpn_count], 'Total_VPN_vServer': [all_vpn_count], 'Non_ICA_VPN_vServer': [non_ica_vpn_vserver_count]})
            print(case_results_df)
            results_df_list.append(case_results_df)
            os.chdir('/home/CITRITE/manjeshn/manscript/')
        else:
            os.chdir('/home/CITRITE/manjeshn/manscript/')
            print(f"No matching Support bundle found for case {case}")

# Concatenate all DataFrames in the list
results_df = pd.concat(results_df_list, ignore_index=True)

with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
    results_df.to_excel(writer, sheet_name='All_Cases', index=False)
    
    # Get the xlsxwriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['All_Cases']

    # Auto-expand all columns
    for i, col in enumerate(results_df.columns):
        column_len = max(results_df[col].astype(str).str.len().max(), len(col))
        worksheet.set_column(i, i, column_len + 2)