# This python script will create a excel file by crawling through the sjanalysis server to check every case support bundles where we see vCPU vs Mem discrepency.
# Condition: For every vCPU, we should have 4 GB memory

import os
import subprocess as sp
from openpyxl import Workbook

# Function to execute shell commands and return the output
def run_command(command):
    result = sp.run(command, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
    return result.stdout.strip()

# Function to check vCPU and memory in a given directory
def check_vcpu_memory(directory):
    if not os.path.isdir(directory):
        return None
    
    os.chdir(directory)
    
    total_core = run_command('''awk '/System Detected/{print $(NF-1);exit}' var/nslog/dmesg.boot''')
    if total_core.isdigit():
        total_core = int(total_core)
        required_mem = total_core * 4  # in GB
    
        configured_mem = run_command('''awk '/hw.realmem/{print $2/1073741824}' shell/sysctl-a.out''')
        if configured_mem:
            configured_mem = float(configured_mem)
            discrepancy = configured_mem < required_mem
            return total_core, required_mem, configured_mem, discrepancy
    return None

# Create an Excel workbook and sheet
wb = Workbook()
ws = wb.active
ws.title = "vCPU vs Memory Discrepancies"

# Define the headers
headers = ["Directory", "Total vCPUs", "Required Memory (GB)", "Configured Memory (GB)", "Discrepancy"]
ws.append(headers)

# Command to find all collector_* directories under /upload/ftp/8*
find_command = 'find /upload/ftp/8* -name "collector_*" -type d'

# Execute the find command and process each directory found
find_process = sp.run(find_command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
for line in find_process.stdout:
    try:
        directory = line.strip()
        result = check_vcpu_memory(directory)
        print(f"Checking {directory} --> {result}")
        # Write the result to the Excel file immediately
        if result:
            ws.append([directory] + list(result))
        else:
            ws.append([directory, "N/A", "N/A", "N/A", "N/A"])
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")

# Get the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Save the workbook in the script directory
output_file = os.path.join(script_dir, "vCPU_vs_Memory_Discrepancies.xlsx")

# Save the workbook
wb.save(output_file)

print(f"Excel file created successfully: {output_file}")