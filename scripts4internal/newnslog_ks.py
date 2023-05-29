import os
import subprocess as sp
import gzip
from concurrent.futures import ThreadPoolExecutor
import re
import time
from datetime import datetime, timedelta
from urllib import request, parse

# Hard coded components
version = "0.1 Alpha"
username = os.popen("whoami").read().strip()
url = 'https://tooltrack.deva.citrite.net/use/conFetch'

# Set correct support bundle path
try:
    if (os.popen("pwd").read().index("collector") >= 0):
        os.chdir(re.search('.*\/collecto.*_[0-9]{2}', os.popen("pwd").read()).group(0))
except AttributeError as e:
    print("Collector Bundle not in Correct Naming Convention")
    os.chdir(re.search('.*\/collecto.*_[0-9|_|\-|a-zA-Z|\.]{1,30}', os.popen("pwd").read()).group(0))
except FileNotFoundError as e:
    print("Collector Bundle not in Correct Naming Convention")
    os.chdir(re.search('.*\/collecto.*_[0-9|_|\-|a-z|\.]{1,30}', os.popen("pwd").read()).group(0))
except ValueError:
    print("\nPlease navigate to correct support bundle path")
    print("Available directories with support bundle names: \n\n".join(re.findall("collect.*", "\n".join(next(os.walk('.'))[1]))))
    quit()

# Retrieve all_newnslog
linux_command_to_list_only_newnslog = '''for i in $(ls -lah var/nslog/ | awk '/newnslog\./&&!/tar|gz/{print "var/nslog/"$NF}END{print "var/nslog/newnlog"}'); do echo $i; done'''
all_newnslog = sp.run(linux_command_to_list_only_newnslog, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.split('\n')
all_newnslog = list(filter(lambda x: x.strip() != '', all_newnslog))

# Timestamp conversion
box_time = str(sp.run("awk -F'GMT' '/Timezone:/&&/GMT/{print substr($2,1,6)}' shell/showcmds.txt | awk 'BEGIN { found = 0 } { output = $0; found = 1 } END { if (found) print output; else print \"00:00\" }'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip())
box_time_mins = (int(re.match(r"([-+]?)(\d+):(\d+)", box_time).group(2)) * 60) + int(re.match(r"([-+]?)(\d+):(\d+)", box_time).group(3)); box_time_mins *= -1 if re.match(r"([-+]?)(\d+):(\d+)", box_time).group(1) == "-" else 1

# Function to convert GMT to box time
def gmt_to_boxtime(input_string):
    pattern = r'(\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \d{4})'
    matches = re.findall(pattern, input_string)
    for match in matches:
        timestamp = datetime.strptime(match, '%a %b %d %H:%M:%S %Y')
        new_timestamp = timestamp + timedelta(minutes=box_time_mins)
        new_timestamp_str = new_timestamp.strftime('%a %b %d %H:%M:%S %Y')
        input_string = input_string.replace(match, new_timestamp_str)
    return input_string

# Function to remove 1st and 2nd column
def remove_columns(input_text):
    lines = input_text.split('\n')
    output_lines = []
    for line in lines:
        columns = line.split()
        # Remove the first two columns
        remaining_columns = columns[2:]
        output_line = ' '.join(remaining_columns)
        output_lines.append(output_line)
    output_text = '\n'.join(output_lines)
    return output_text

# Check if the conFetch directory exists
directory_name = "conFetch/newnslog_raw"
if not os.path.exists(directory_name):
    os.makedirs(directory_name)
    print("conFetch directory is created.")
else:
    print("conFetch directory exists.")

# Process newnslog and write sorted output to file
def newnslog_current(newnslog):
    newnslog_current_cmd = "nsconmsg -K " + newnslog + " -d current -s disptime=1 | awk '/./&&!/Displaying|NetScaler|reltime|Index/ {if (NR!=1) print $0}'"
    output = sp.run(newnslog_current_cmd, shell=True, capture_output=True, text=True).stdout
    output = remove_columns(output)
    output = gmt_to_boxtime(output)
    # Split lines and sort the output
    lines = output.split('\n')
    sorted_lines = sorted(lines)
    # Join the sorted lines back into a single string
    sorted_output = '\n'.join(sorted_lines)
    file_path = os.path.join(directory_name, "d.current_file.txt.gz")
    with gzip.open(file_path, "at") as file:
        file.write(sorted_output)

# Process all newnslog files
def process_all_d_flags():
    with ThreadPoolExecutor() as executor:
        futures = []
        for newnslog in all_newnslog:
            future = executor.submit(newnslog_current, newnslog)
            futures.append(future)
        # Wait for all tasks to complete
        for future in futures:
            future.result()
        print("newnslog d_flags are processed and output written to d.current_file.txt.gz")

# Execute the main function
try:
    print("newnslog d_flags are getting processed")
    process_all_d_flags()
finally:
    payload = {"version": version, "user": username, "action": "newnslog_wrapper --> " + os.getcwd() + " --> " + str(int(time.time())), "runtime": 0, "result": "Partial", "format": "string", "sr": os.getcwd().split("/")[3]}
    resp = request.urlopen(request.Request(url, data=parse.urlencode(payload).encode()))
