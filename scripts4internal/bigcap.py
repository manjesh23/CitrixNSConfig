#!/usr/local/bin/python3.7
#!/usr/local/bin/tshark

import sys
from os.path import exists as file_exists
import os
from os import path
import subprocess as sp


# Preparing Required color codes
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


# Get args stored locally and validate
collector_pack = sys.argv[1]
capture_file = sys.argv[2]

# Check if pcap exists or not
try:
    if file_exists(capture_file):
        pass
    else:
        print(style.RED + "Unable to find Capture file: " +
              capture_file + style.RESET)
finally:
    pass

# Check if collector bundle exist and has ns_running_config.conf file
try:
    if path.isdir(collector_pack):
        nsRunning_Config = collector_pack+"/shell/ns_running_config.conf"
        allrequiredfiles = [nsRunning_Config]
        for i in allrequiredfiles:
            if file_exists(i):
                pass
            else:
                print(style.RED +
                      "File " + i + " is missing from collector pack and script might not work fully !!" + style.RESET)
    else:
        print(style.RED + "Unable to find the Support bundle: " +
              collector_pack + style.RESET)
        quit()
finally:
    pass

# Read pcap file and its custom data along with collector data
cap_ip_count = sp.run(
    "tshark -r " + capture_file + " -q -z ip_hosts,tree | sort | uniq | egrep '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | awk '{printf \"%s %s\\n\", $2,$1}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()
#matched_pkt_timerange = sp.run("tshark -r " + capture_file + " -Tfields -e frame.time -Y \"ip.addr eq 10.110.158.192\" | sort | awk 'NR == 1 {print} END {print}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()
lbvserver = os.popen(
    "awk '/^add lb vserver/{{ if ($6!=\"0.0.0.0\") print $4, $5, $6, $7}}' "+collector_pack+"/shell/ns_running_config.conf").read()

# Basic capture file details.

# Basic VIP Details
print(style.YELLOW + '{:-^87}'.format('LB VIP Details') + style.RESET+"\n")
for cap_ip_count_ip in cap_ip_count.splitlines():
    for lbvserver_line in lbvserver.splitlines():
        if (cap_ip_count_ip.split()[1] == lbvserver_line.split()[2]):
            lbService = sp.run("awk '/^bind lb vserver/&&/"+lbvserver_line.split()[
                0]+"/{print $5}' "+collector_pack+"/shell/ns_running_config.conf", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()
            print(lbService)
            lbService_Details = sp.run("awk '/^add service/&&/"+lbService + "/{print $4, $5, $6}' "+collector_pack +
                                       "/shell/ns_running_config.conf", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()
            lbServer = sp.run("awk '/^add server " + str(lbService_Details.split()[
                              0]) + " /{print $4}' "+collector_pack+"/shell/ns_running_config.conf", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip()

            print("LB VServer --> " + str(lbvserver_line) +
                  " --> " + str(cap_ip_count_ip.split()[0]))
            print(" \t   --> LB Service --> " + lbService +
                  "( " + lbService_Details + " )")
            print(" \t   --> LB Server --> " + lbServer)
        else:
            pass
