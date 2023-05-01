import re
import subprocess

# Run the 'top' command and capture its output
top_output = subprocess.check_output(
    ['top', '-m', 'io', '-o', 'write', '-n', '25'])

# Split the output into lines
lines = top_output.decode().split('\n')

# Extract the header row
header_row = lines[7]

# Extract the data rows
data_rows = lines[8:]

# Define a regular expression to extract the fields from each data row
row_pattern = re.compile(
    r'^\s*(\d+)\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(.*)$')

# Loop through the data rows and extract the fields
for row in data_rows:
    # Match the row pattern
    match = row_pattern.match(row)
    if match:
        # Extract the fields from the match object
        pid = match.group(1)
        username = match.group(2)
        vcs = match.group(3)
        ivcs = match.group(4)
        read = match.group(5)
        write = match.group(6)
        fault = match.group(7)
        total = match.group(8)
        percent = match.group(9)
        command = match.group(10)

        # Print the fields
        print(f'PID: {pid}')
        print(f'Username: {username}')
        print(f'VCSW: {vcs}')
        print(f'IVCSW: {ivcs}')
        print(f'READ: {read}')
        print(f'WRITE: {write}')
        print(f'FAULT: {fault}')
        print(f'TOTAL: {total}')
        print(f'PERCENT: {percent}')
        print(f'COMMAND: {command}')
