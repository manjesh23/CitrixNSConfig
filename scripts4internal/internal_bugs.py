import requests
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

# List of Internal bugs which are created by Manjesh N
manjeshn_reported_bugs = ["NSUI-19176", "NSUI-19185", "NSUI-19186", "NSUI-19187", "NSUI-19188", "NSUI-19190", "NSAUTH-13672", "NSUI-19215", "NSUI-19214", "NSUI-19892", "NSLINUX-7296", "NSLINUX-7297", "NSLINUX-7298", "NSADM-111975", "NSLINUX-7299", 
                          "NSLINUX-7300", "NSLINUX-7301", "NSADM-111979", "NSLINUX-7303", "NSLINUX-7304", "NSLINUX-7305", "NSADM-112040", "NSLINUX-7306", "NSLINUX-7307", "NSADM-112298", "NSLINUX-7338", "NSLINUX-7345", "NSLINUX-7346", "NSADM-112541"]

# Required URL struct
jira_url = 'https://issues.citrite.net/rest/api/2/issue/'

# Authorization tokens
headers = {"Authorization": "Bearer MzAxNTE5MjE5MzU0OtUTcabB1CEMVwUGotGeibLeghra"}

# Create a workbook and select active sheet
wb = Workbook()
ws = wb.active

# Write headers
header_row = ["JIRA ID", "Summary", "Status", "Resolution", "Jira Owner", "Created Date", "Reporter"]
ws.append(header_row)

# Highlight header row
for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="00CCFF", end_color="00CCFF", fill_type="solid")

# Fetch data for each bug
for bug in manjeshn_reported_bugs:
    bug_url = f'{jira_url}{bug}'
    response = requests.get(bug_url, headers=headers)
    if response.status_code == 200:
        jsonData = response.json()
        jira_id = jsonData['key']
        summary = jsonData['fields']['summary']
        status = jsonData['fields']['status']['name']
        resolution = jsonData['fields']['resolution']['name'] if jsonData['fields'].get('resolution') is not None and 'name' in jsonData['fields']['resolution'] else 'Unresolved'
        assignee_name = jsonData['fields']['assignee']['displayName']
        created_date = datetime.strptime(jsonData['fields']['created'], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d-%b-%Y")
        reporter = jsonData['fields']['reporter']['displayName']
        
        # Append the data to the worksheet
        row = [jira_id, summary, status, resolution, assignee_name, created_date, reporter]
        ws.append(row)
        
        # Change the cell background color based on status
        status_cell = ws.cell(row=ws.max_row, column=3)
        if status == "Done":
            status_cell.fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")  # Green
        elif status == "Canceled":
            status_cell.fill = PatternFill(start_color="F83C3C", end_color="F83C3C", fill_type="solid")  # Red
        elif status == "In Progress":
            status_cell.fill = PatternFill(start_color="1AC2F3", end_color="1AC2F3", fill_type="solid")  # Blue
        elif status == "Backlog":
            status_cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow
        elif status == "Ready For Test":
            status_cell.fill = PatternFill(start_color="F88C3C", end_color="F88C3C", fill_type="solid")  # Orange

# Auto-adjust column width
for column in ws.columns:
    max_length = 0
    column_letter = get_column_letter(column[0].column)
    for cell in column:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(cell.value)
        except:
            pass
    adjusted_width = (max_length + 2)
    ws.column_dimensions[column_letter].width = adjusted_width

# Save the workbook
ws.title = "Internal_Bugs"
wb.save(r"G:\My Drive\bug_report.xlsx")
