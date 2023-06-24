import os
import subprocess as sp
import gzip
from concurrent.futures import ThreadPoolExecutor
import re
import time
from urllib import request, parse
from datetime import datetime, timedelta

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
    payload = {"version": version, "user": username, "action": "newnslog_wrapper --> " + os.getcwd() + " --> " + str(int(time.time())), "runtime": 0, "result": "Partial", "format": "string", "sr": os.getcwd().split("/")[3]}
    resp = request.urlopen(request.Request(url, data=parse.urlencode(payload).encode()))
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

# Check if the conFetch directory exists
directory_name = "conFetch/newnslog_raw"
if not os.path.exists(directory_name):
    os.makedirs(directory_name)
    print("conFetch directory is created.")
else:
    print("conFetch directory exists.")

# Process newnslog with d_flag as current and write sorted output to file
def newnslog_current(newnslog):
    newnslog_current_cmd = "nsconmsg -K " + newnslog + " -d current -s disptime=1 | awk '/./&&!/Displaying|NetScaler|reltime|Index/{if (NR!=1) print $0}'"
    current_output = sp.run(newnslog_current_cmd, shell=True, capture_output=True, text=True).stdout
    current_output_boxtime = gmt_to_boxtime(current_output)
    file_path = os.path.join(directory_name, "d.current_file.txt.gz")
    with gzip.open(file_path, "at") as file:
        file.write(current_output_boxtime)

# Process newnslog with d_flag as event and write sorted output to file
def newnslog_event(newnslog):
    newnslog_event_cmd = "nsconmsg -K " + newnslog + " -d event -s disptime=1 | awk '/./&&!/Displaying|NetScaler|rtime|Done./{if (NR!=1) print $0}'"
    event_output = sp.run(newnslog_event_cmd, shell=True, capture_output=True, text=True).stdout
    event_output_boxtime = gmt_to_boxtime(event_output)
    file_path = os.path.join(directory_name, "d.event_file.txt.gz")
    with gzip.open(file_path, "at") as file:
        file.write(event_output_boxtime)

# Process newnslog with d_flag as setime (overall) and write sorted output to file
def newnslog_setime():
    newnslog_setime_cmd = '''echo $(nsconmsg -K $(find ./ -type d -name "newnslog.*" | sort |  sed 's/ .\//\n.\//g' | awk -F/ '{print "var/nslog/"$NF}' | sed -n '1p') -d setime | awk '/start/&&!/Displaying/{$1=$2=""; printf }'; printf " --> "; nsconmsg -K var/nslog/newnslog -d setime | awk '/end/&&!/Displaying/{$1=$2=""; print}')'''
    print(newnslog_setime_cmd)
    setime_output = sp.run(newnslog_setime_cmd, shell=True, capture_output=True, text=True).stdout
    setime_output_boxtime = gmt_to_boxtime(setime_output)
    print(f"This is setime {setime_output}")
    print(f"This is setime in localtime {setime_output_boxtime}")
    file_path = os.path.join(directory_name, "d.setime_file.txt.gz")
    with gzip.open(file_path, "at") as file:
        file.write(setime_output_boxtime)

# Process all newnslog files
def process_all_d_flags():
    with ThreadPoolExecutor() as executor:
        futures = []
        for newnslog in all_newnslog:
            futures.append(executor.submit(newnslog_current, newnslog))
            futures.append(executor.submit(newnslog_event, newnslog))
            futures.append(executor.submit(newnslog_setime, newnslog))
        
        # Wait for all futures to complete
        for future in futures:
            future.result()

# Execute the main function
try:
    print("newnslog d_flags are getting processed")
    process_all_d_flags()
    print("newnslog d_flags are processed and output written under conFetch/newnslog_raw")
finally:
    pass