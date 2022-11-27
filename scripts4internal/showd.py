#!/usr/local/bin/python3.9
from asyncio import subprocess
from asyncore import read
import os
import subprocess as sp
import logging
import argparse
from glob import glob
import re
from os.path import exists as file_exists
from urllib import request, parse
import json
import ast
import time

# Preparing Required color codes


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


# About script
showscriptabout = '''

  ____            _           _                     _____    _       _     
 |  _ \ _ __ ___ (_) ___  ___| |_    ___ ___  _ __ |  ___|__| |_ ___| |__  
 | |_) | '__/ _ \| |/ _ \/ __| __|  / __/ _ \| '_ \| |_ / _ \ __/ __| '_ \ 
 |  __/| | | (_) | |  __/ (__| |_  | (_| (_) | | | |  _|  __/ || (__| | | |
 |_|   |_|  \___// |\___|\___|\__|  \___\___/|_| |_|_|  \___|\__\___|_| |_|
               |__/                                                        
               
######################################################################################################
##                                                                                                  ##
##   Note -- Please do not use this script if you are not sure of what you are doing.               ##
##   Product -- Only for Citrix NetScaler TAC Use.                                                  ##
##   Unauthorized usage of this script / sharing for personal use will be considered as offence.    ##
##   This script is designed to extract data from support bundle -- "script based troubleshooting". ##
##                                                                                                  ##
######################################################################################################
'''

# About Author
showscriptauthor = '''
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
url = 'https://tooltrack.deva.citrite.net/use/conFetch'
headers = {'Content-Type': 'application/json'}
version = "2.7.0"

# Parser args
parser = argparse.ArgumentParser(
    description="Citrix Support Bundle Show Script")
parser.add_argument('--author', action="store_true",
                    help=argparse.SUPPRESS)
parser.add_argument('-i', action="store_true",
                    help="ADC Basic Information")
parser.add_argument('-n', action="store_true",
                    help="ADC Networking Information")
parser.add_argument('-p', action="store_true",
                    help="ADC Process Related Information")
parser.add_argument('-E', action="store_true",
                    help="Match well known error with KB articles")
parser.add_argument('-fu', action="store_true",
                    help="Display Latest RTM Firmware Code")
parser.add_argument('-gz', action="store_true",
                    help="Unzip *.gz files under /var/log and vsr/nslog")
parser.add_argument('-im', action="store_true",
                    help="Indexing timestamp of ns.log")
parser.add_argument('-imall', action="store_true",
                    help="Indexing timestamp of logs including ns, auth, bash, nitro, notice, nsvpn, sh")
parser.add_argument('-error', metavar="", help="Highlights known errors")
parser.add_argument('-show', metavar="", help="Selected Show Commands")
parser.add_argument('-stat', metavar="", help="Selected Stat Commands")
parser.add_argument('-vip', action="store_true", help="Get VIP Basic Details")
parser.add_argument('-case', action="store_true",
                    help=argparse.SUPPRESS)
parser.add_argument('-ha', action="store_true",
                    help=argparse.SUPPRESS)
parser.add_argument('--about', action="store_true",
                    help="About Show Script")
parser.add_argument('-G', action="append",
                    choices={"cpu", "ha"}, help="Generate HTML Graph for all newnslog(s)")
args = parser.parse_args()

# Logme the user
username = os.popen("whoami").read().strip()
userfile = "/home/CITRITE/manjeshn/manscript/showdata/"+username+".log"
logging.basicConfig(filename=userfile,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Set correct support bundle path
try:
    if (os.popen("pwd").read().index("collector") >= 0):
        os.chdir(
            re.search('.*\/collecto.*_[0-9]{2}', os.popen("pwd").read()).group(0))
except ValueError:
    print("\nPlease navigate to correct support bundle path")
    print("Available directories with support bundle names: \n\n" + style.CYAN +
          "\n".join(re.findall("collect.*", "\n".join(next(os.walk('.'))[1]))) + style.RESET)
    payload = {"version": version, "user": username, "action": "Out of Support Bundle --> " + os.getcwd() + " --> " + str(int(time.time())),
               "runtime": 0, "result": "Partial", "format": "string", "sr": os.getcwd().split("/")[3]}
    resp = request.urlopen(request.Request(
        url, data=parse.urlencode(payload).encode()))
    quit()

# Assign correct files and its path to variables
try:
    nsconf = "nsconfig/ns.conf"
    showcmd = "shell/showcmds.txt"
    statcmd = "shell/statcmds.txt"
    sysctl = "shell/sysctl-a.out"
    uptime = "shell/uptime.out"
    df = "shell/df-akin.out"
    dmesgboot = "var/nslog/dmesg.boot"
    allrequiredfiles = [nsconf] + [showcmd] + \
        [statcmd] + [sysctl] + [uptime] + [df] + [dmesgboot]
    for i in allrequiredfiles:
        if file_exists(i):
            pass
        else:
            print(style.RED +
                  "File " + i + " is missing from collector pack and script might not work fully !!" + style.RESET)
finally:
    pass

if args.i:
    try:
        logger.info(os.getcwd() + " - show -i")
        # Printing system essential details
        print(style.YELLOW + '{:-^87}'.format('ADC Show Configuration'))
        print(style.RESET)
        adchostname = sp.run("awk '{print $2}' shell/uname-a.out",
                             shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        adcha = sp.run(
            "sed -n -e \"/show ns version/I,/Done/p\" shell/showcmds.txt | grep Node | awk -F':' '{print $2}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        adcfirmware = sp.run("cat shell/ns_running_config.conf | grep \"#NS\" | cut -c 2-",
                             shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        firmwarehistory = sp.run(
            "awk -F'NetScaler' 'BEGIN{nores=1;}/upgrade from NetScaler/{if ($0 ~ \"build\") history=$2; nores=0} END {if (nores) print \"None found recently\"; else print history}' shell/dmesg-a.out", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsinstall = sp.run(
            "awk '/VERSION/||/_TIME/{$1=\"\"; printf \"%s -->\", $0}' var/nsinstall/installns_state | sed -E 's/^\s|[0-9]{9,15}.|-->$//g'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        platformserial = sp.run(
            "sed -n '/^exec: show ns hardware/,/Done/p' shell/showcmds.txt | awk '/Serial/{print $NF}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        platformmodel = sp.run(
            "sed -n '/^exec: show ns hardware/,/Done/p' shell/showcmds.txt | awk '/Platform/{print $1=\"\"; print}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        licmodel = sp.run("awk '/Users/{print}' var/log/license.log | awk -F: '{print $1}' | awk '{printf \"%s | \", $NF}' | sed 's/..$//'",
                          shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        hwplatform = sp.run("egrep \"netscaler.descr\" shell/sysctl-a.out | awk -F':' '{print $2}'",
                            shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        vmplatform = sp.run("egrep \"platform\" var/nslog/dmesg.boot | head -2 | tail -1 | awk -F':' '{if ($2 ~ \"bios\") print \"No Hypervisor found\"; else print $2}'",
                            shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        licensetype = sp.run("awk '/License Type/{$1=$2=\"\"; print}' shell/showcmds.txt",
                             shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        licensemode = sp.run(
            "awk '/Licensing mode/{$1=$2=\"\"; print}' shell/showcmds.txt", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsip = sp.run(
            "sed -n '/ns config/,/Done/p' shell/showcmds.txt | grep \"NetScaler IP\" | egrep -o \"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\" | grep -v 255", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsipsubnet = sp.run(
            "sed -n '/ns config/,/Done/p' shell/showcmds.txt | grep \"NetScaler IP\" | egrep -o \"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\" | grep 255", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsfeatures = sp.run("awk '/ns feature/{$1=$2=$3=\"\";print $0}' nsconfig/ns.conf",
                            shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsmode = sp.run("awk '/ns mode/{$1=$2=$3=\"\";print $0}' nsconfig/ns.conf",
                        shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsboottime = sp.run(
            "egrep \"nsstart\" var/nslog/ns.log | tail -1 | awk '{$1=$NF=$(NF-1)=\"\"; print}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        collectorpacktime = sp.run(
            "cat shell/date.out", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        deviceuptime = sp.run("sed 's/^.*up //' shell/uptime.out | sed 's/,...user.*//'",
                              shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        cpuinfo = sp.run("awk '/hw.model/{$1=\"\"; print}' shell/sysctl-a.out",
                         shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        loadaverage = sp.run("awk '/load average/{printf \"%s %s %s\", \"1 min: \"$6, \"5 min: \"$7, \"15 min: \"$8}' shell/top-b.out",
                             shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        memoryinfo = sp.run(
            "awk '(/real memory/ && ORS=\" ,\") || (/avail memory/ && ORS=RS)' var/nslog/dmesg.boot | head -n1 | awk '{printf \"%s | %s\", \"Total Memory: \"$5$6, \"Available Memory: \"$11$12}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        varsize = sp.run(
            "awk '/\/var$/{printf \"%s -> %s | %s | %s | %s\", $1,\"Total: \"$2,\"Used: \"$3, \"Free: \"$4, \"Capacity Used: \"substr($5, 1, length($5)-1)}' shell/df-akin.out | awk '{if ($NF > 75){printf \"%s\", substr($0, 1, length($0)-2)\"\033[0;31m\"$NF\"%\033[0m\"}else{printf \"%s\", substr($0, 1, length($0)-2)\"\033\[0;32m\"$NF\"%\033[0m\"}}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        sslcards = sp.run(
            "awk '/SSL cards UP/{printf \"%s%s - \",\"[UP: \" $NF,\"]\"}/SSL cards present/{printf \"%s%s\\n\", \"[Present: \"$NF,\"]\";exit}' shell/statcmds.txt", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsppe = sp.run("awk '/NSPPE/{c++}END{print c}' shell/nsp.out",
                       shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nstimes = sp.run(
            "sed -n -e \"/exec: show ns version/I,/Done/ p\" shell/showcmds.txt | grep Time | awk '{$1=$1};1'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        if len(memoryinfo.stdout) > 0:
            memoryinfototal = int(memoryinfo.stdout.split()[2][:-3][1:])
            memoryinfoavail = int(memoryinfo.stdout.split()[6][:-3][1:])
            memfreepercent = (memoryinfoavail / memoryinfototal)*100
            memfreepercent = round(memfreepercent, 2)
        else:
            pass
    except IOError as io:
        print(io)
    finally:
        print("Support file location: " + os.popen("pwd").read().strip())
        print("")
        print(nstimes.stdout.strip())
        print("Collector pack generated @ " + collectorpacktime.stdout.strip())
        print("")
        print("ADC Hostname: " + adchostname.stdout.strip())
        print("ADC HA State: " + adcha.stdout.strip())
        print("ADC Firmware version: " + adcfirmware.stdout.strip())
        print("Firmware history: " + firmwarehistory.stdout.strip())
        print("Last Upgrade Stats: " + nsinstall.stdout.strip())
        print("")
        print("Platform Serial: " + platformserial.stdout.strip())
        print("Platform Model: " + platformmodel.stdout.strip())
        print("HW Platform: " + hwplatform.stdout.strip())
        print("VM Platform: " + vmplatform.stdout.strip())
        print("")
        print("License Type: " + licensetype.stdout.strip())
        print("Licensing Mode: " + licensemode.stdout.strip())
        print("License Model: " + licmodel.stdout.strip())
        print("")
        print("NSIP Address: " + nsip.stdout.strip() +
              " | " + nsipsubnet.stdout.strip())
        print("NS Enabled Feature: " + nsfeatures.stdout.strip())
        print("NS Enabled Mode: " + nsmode.stdout.strip())
        print("NS Last Boot Time: " + nsboottime.stdout.strip())
        print("Device uptime: " + deviceuptime.stdout.strip())
        print("")
        print("CPU Info: " + cpuinfo.stdout.strip())
        print("Load Average: " + loadaverage.stdout.strip())
        try:
            if memfreepercent > 40:
                print("Memory Info: " + memoryinfo.stdout.strip() +
                      " Free Percent: " + style.GREEN + str(memfreepercent) + "%" + style.RESET)
            else:
                print("Memory Info: " + memoryinfo.stdout.strip() +
                      " Free Percent: " + style.RED + str(memfreepercent) + "%" + style.RESET)
        except NameError:
            pass
        print("var Size: " + varsize.stdout.strip())
        print("SSL Cards: " + sslcards.stdout.strip())
        print("NSPPE Count: " + nsppe.stdout.strip() + "\n")
        # Tooltrack
        payload = {"version": version, "user": username, "action": "show -i --> " + os.getcwd() + " --> " + str(int(time.time())),
                   "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.n:
    try:
        logger.info(os.getcwd() + " - show -n")
        # Prining Network related information on ADC
        print(style.YELLOW +
              '{:-^87}'.format('ADC Network Information') + style.RESET+"\n")
        adcnetinfo = sp.run(
            "awk '/exec: show ns ip$/{flag=1;next}/Done/{flag=0}flag' shell/showcmds.txt", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        adcroute = sp.run(
            "awk '/exec: show route$/{flag=1;next}/Done/{flag=0}flag' shell/showcmds.txt", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        adcarp = sp.run(
            "awk '/exec: show arp$/{flag=1;next}/Done/{flag=0}flag' shell/showcmds.txt", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
    finally:
        if adcnetinfo.returncode == 0:
            print(style.YELLOW +
                  '{:-^87}\n'.format('Network Interface') + style.RESET + adcnetinfo.stdout)
        else:
            print(
                style.RED + '{:-^87}\n'.format('Unable to read Network Interface') + style.RESET)
        if adcroute.returncode == 0:
            print(style.YELLOW +
                  '{:-^87}\n'.format('v4 Routes') + style.RESET + adcroute.stdout)
        else:
            print(
                style.RED + '{:-^87}\n'.format('Unable to read v4 Routes') + style.RESET)
        if adcarp.returncode == 0:
            print(style.YELLOW +
                  '{:-^87}\n'.format('ARP Table') + style.RESET + adcarp.stdout)
        else:
            print(
                style.RED + '{:-^87}\n'.format('Unable to read ARP Table') + style.RESET)
        payload = {"version": version, "user": username, "action": "show -n --> " + os.getcwd() + " --> " + str(
            int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.p:
    try:
        logger.info(os.getcwd() + " - show -p")
        vcpu = sp.run("awk '/System Detected/{print $(NF-1), $NF;exit}' var/nslog/dmesg.boot",
                      shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsppenum = sp.run("awk '/NSPPE/{print}' shell/nsp.out | wc -l | sed \"s/^[ \t]*//\"",
                          shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsppepid = sp.run("awk '/NSPPE/{print}' shell/nsp.out | sed \"s/^[ \t]*//\"",
                          shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        core = sp.run("awk '/NSPPE-/&&!/gz/{printf \"[%s-%s/%s --> %s --> %s]\\n\",  $6, $7, $8, $NF, $5}' shell/ls_lRtrp_var.out | sed \"s/^[ \t]*//\"",
                      shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
    finally:
        print(style.YELLOW + '{:-^87}'.format('ADC Process Information'))
        print(style.RESET)
        print("Number of vCPU: " + vcpu.stdout.strip())
        print("NSPPE Details: " + nsppenum.stdout + "\n" + nsppepid.stdout)
        print("Core files: " + "\n" + core.stdout.strip())
        print("")
    payload = {"version": version, "user": username, "action": "show -p --> " + os.getcwd() + " --> " + str(
        int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
    resp = request.urlopen(request.Request(
        url, data=parse.urlencode(payload).encode()))
elif args.E:
    try:
        print(style.YELLOW +
              '{:-^87}'.format('Errors and Matched KB Articles') + style.RESET+"\n")
        print(os.popen(
            "for i in $(ls -lah var/log/ | awk '/ns.lo*/{print $NF}'); do awk 'BEGIN{c=0}/\"ERROR: Operation not permitted - no FIPS card present in the system\"/{c++}END {if(c > 0){printf \"%s\\t%s\\t%s\\t%s\\n\", ARGV[1], c, \"ERROR: Operation not permitted - no FIPS card present in the system\", \"https://support.citrix.com/article/CTX330685\"}}' var/log/$i; done").read().strip())
        print("\n")
    finally:
        payload = {"version": version, "user": username, "action": "show -E --> " + os.getcwd() + " --> " + str(
            int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.fu:
    try:
        logger.info(os.getcwd() + " - show -fu")
        adcfirmwareRTM = sp.run(
            "curl -s 'https://www.citrix.com/downloads/citrix-adc/' | egrep -C2 \"<a href=\\\"\/downloads\/citrix-adc.*\" | awk '/citrix-adc|\/p/{print}' | paste - - | sed -E 's/<\/.|<a href=|\\\"|NEW/ /g' | awk -F'>' '{printf \"%s|%s\\n\", $3, $2}' | awk '{$1=$1};1' | sed -E 's-\| \|- \|-g' | column -t -s'|' | sort -k4n -k2M -k3n", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip().replace('\n\n', '\n')
        admadcfirmwareRTM = sp.run(
            "curl -s 'https://www.citrix.com/downloads/citrix-application-management/' | egrep -C2 \"<a href=\\\"\/downloads\/citrix-application-management.*\" | awk '/citrix-application-management|\/p/{print}' | paste - - | sed -E 's/<\/.|<a href=|\\\"|NEW/ /g' | awk -F'>' '{printf \"%s|%s\\n\", $3, $2}' | awk '{$1=$1};1' | sed -E 's-\| \|- \|-g' | column -t -s'|' | sort -k4n -k2M -k3n", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.strip().replace('\n\n', '\n')
    finally:
        # ADC Release
        print(style.YELLOW +
              '{:-^87}'.format('ADC Released RTM Code Version and Date') + style.RESET+"\n")
        print(style.YELLOW +
              '{:-^87}'.format('ADC Release Feature Phase Code Details') + style.RESET+"\n")
        for adcrelease in adcfirmwareRTM.splitlines():
            if "ADC Release" in adcrelease and "Feature Phase" in adcrelease:
                print(style.LIGHTGREEN + adcrelease + style.RESET)
        print("\n")
        print(style.YELLOW +
              '{:-^87}'.format('ADC Release Maintenance Phase Code Details') + style.RESET+"\n")
        for adcrelease in adcfirmwareRTM.splitlines():
            if "ADC Release" in adcrelease and "Maintenance Phase" in adcrelease:
                print(style.LIGHTRED + adcrelease + style.RESET)
        print("\n")
        # ADM Release
        print(style.YELLOW +
              '{:-^87}'.format('ADM Released RTM Code Version and Date') + style.RESET+"\n")
        print(style.YELLOW +
              '{:-^87}'.format('ADM Release Feature Phase Code Details') + style.RESET+"\n")
        for admrelease in admadcfirmwareRTM.splitlines():
            if "ADM Release" in admrelease and "Feature Phase" in admrelease:
                print(style.LIGHTGREEN + admrelease + style.RESET)
        print("\n")
        print(style.YELLOW +
              '{:-^87}'.format('ADM Release Maintenance Phase Code Details') + style.RESET+"\n")
        for admrelease in admadcfirmwareRTM.splitlines():
            if "ADM Release" in admrelease and "Maintenance Phase" in admrelease:
                print(style.LIGHTRED + admrelease + style.RESET)
        print("\n")
        # SDX Release
        print(style.YELLOW +
              '{:-^87}'.format('SDX Released RTM Code Version and Date') + style.RESET+"\n")
        print(style.YELLOW +
              '{:-^87}'.format('SDX Bundle Feature Phase Code Details') + style.RESET+"\n")
        for sdxrelease in adcfirmwareRTM.splitlines():
            if "SDX Bundle" in sdxrelease and "Feature Phase" in sdxrelease:
                print(style.LIGHTGREEN + sdxrelease + style.RESET)
        print("\n")
        print(style.YELLOW +
              '{:-^87}'.format('SDX Bundle Maintenance Phase Code Details') + style.RESET+"\n")
        for sdxrelease in adcfirmwareRTM.splitlines():
            if "SDX Bundle" in sdxrelease and "Maintenance Phase" in sdxrelease:
                print(style.LIGHTRED + sdxrelease + style.RESET)
        payload = {"version": version, "user": username, "action": "show -fu --> " + os.getcwd() + " --> " + str(
            int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
elif args.gz:
    try:
        logger.info(os.getcwd() + " - show -gz")
        # Fix permission
        sp.run("fixperms ./",
               shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        # Unzip all gz files under ./var/log
        gunzipresult = sp.run("gunzip -v var/log/*.gz",
                              shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        # Unzip all gz files under ./var/nslog
        gunzipnewnsresult = sp.run(
            "for i in var/nslog/new*.tar.gz; do tar -xvf \"$i\" -C var/nslog/; done", shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    finally:
        if gunzipresult.returncode == 0:
            sp.run("fixperms ./",
                   shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            print(style.YELLOW +
                  '{:-^87}\n'.format('Gunzip all .gz files under /var/log') + style.RESET)
            print(style.YELLOW + str(gunzipresult.stderr.decode('utf-8')) + style.RESET)
            print(style.GREEN + "Extracted all files in var/log!!!" + style.RESET)
        else:
            print(style.RED + "Nothing to do here in var/log/" + style.RESET)
        if gunzipnewnsresult.returncode == 0:
            sp.run("fixperms ./",
                   shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            print(style.YELLOW +
                  '{:-^87}\n'.format('Gunzip all .gz files under /var/log') + style.RESET)
            print(style.YELLOW +
                  str(gunzipnewnsresult.stderr.decode('utf-8')) + style.RESET)
            print(style.GREEN + "Extracted all files var/nslog!!!" + style.RESET)
        else:
            print(style.RED + "Nothing to do here in var/nslog/" + style.RESET)
        payload = {"version": version, "user": username, "action": "show -gz --> " + os.getcwd() + " --> " + str(
            int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.im:
    try:
        logger.info(os.getcwd() + " - show -im")
        try:
            nslog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/ns.lo* | grep -v gz | grep -v tar); do awk 'NR == 2 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        finally:
            if nslog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC ns.log timestamp IndexMessages') + style.RESET + nslog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read ns.log') + style.RESET)
    finally:
        payload = {"version": version, "user": username, "action": "show -im --> " + os.getcwd() + " --> " + str(
            int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.imall:
    try:
        logger.info(os.getcwd() + " - show -imall")
        # Printing Index messages for ns.log, auth.log, bash.log, nitro.log, notice.log, nsvpn.log, sh.log
        try:
            nslog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/ns.lo* | grep -v gz | grep -v tar); do awk 'NR == 2 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            authlog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/auth.lo* | grep -v gz | grep -v tar); do awk 'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            bashlog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/bash.lo* | grep -v gz | grep -v tar); do awk 'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            nitrolog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/nitro.lo* | grep -v gz | grep -v tar); do awk 'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            noticelog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/notice.lo* | grep -v gz | grep -v tar); do awk 'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            nsvpnlog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/nsvpn.lo* | grep -v gz | grep -v tar); do awk 'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            shlog = sp.run(
                "awk 'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\n' var/log/sh.lo* | grep -v gz | grep -v tar); do awk 'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,substr(ARGV[1],9)}' $i; done", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            newnslog = sp.run(
                "awk 'BEGIN{printf \"%s\\t\\t | %s\\t\\t    | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}'; for i in $(printf '%s\\n' var/nslog/newnslo* | grep -v gz | grep -v tar); do nsconmsg -K $i -d setime | awk '!/Displaying|NetScaler|size|duration/{$1=$2=\"\"; printf \"%s\\t|\", $0}END{printf \"\\n\"}'; echo $i; done | sed 'N;s/\\n/ /' | awk '{$1=$1=\"\"}1' | sed 's/^ //' | sed -r '/^\\s*$/d' | awk '{printf  \"%s %s %02s %s %s %s %s %s %02s %s %s %s %s\\n\", $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        finally:
            if nslog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC ns.log timestamp IndexMessages') + style.RESET + nslog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read ns.log') + style.RESET)
            if authlog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC auth.log timestamp IndexMessages') + style.RESET + authlog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read auth.log') + style.RESET)
            if bashlog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC bash.log timestamp IndexMessages') + style.RESET + bashlog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read bash.log') + style.RESET)
            if nitrolog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC nitro.log timestamp IndexMessages') + style.RESET + nitrolog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read nitro.log') + style.RESET)
            if noticelog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC notice.log timestamp IndexMessages') + style.RESET + noticelog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read notice.log') + style.RESET)
            if nsvpnlog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC nsvpn.log timestamp IndexMessages') + style.RESET + nsvpnlog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read nsvpn.log') + style.RESET)
            if shlog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC sh.log timestamp IndexMessages') + style.RESET + shlog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read sh.log') + style.RESET)
            if newnslog.returncode == 0:
                print(style.YELLOW +
                      '{:-^87}\n'.format('ADC newnslog timestamp IndexMessages') + style.RESET + newnslog.stdout)
            else:
                print(
                    style.RED + '{:-^87}\n'.format('Unable to read newnslog') + style.RESET)
    finally:
        payload = {"version": version, "user": username, "action": "show -imall --> " + os.getcwd() + " --> " + str(
            int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.error:
    try:
        logger.info(os.getcwd() + " - show -error")
        # Highlight all the ERROR|err|down|disconnect|fail containing lines in input file.
        print(sp.run("if test -f var/log/" + args.error +
              "; then awk '/ERROR|err|Err|down|disconnect|fail/{print \"\033[1;31m\"$0\"\033[0m\";next}{print $0}' var/log/" + args.error + "; else echo \"File not found\"; fi", shell=True).stdout)
    finally:
        payload = {"version": version, "user": username, "action": "show -error --> " + args.error + " --> " + os.getcwd() + " --> " + str(
            int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.show:
    try:
        logger.info(os.getcwd() + " - show -show - " + args.show)
        # Prining show command output from file shell/showcmds.txt | Try without show
        showout = os.popen("sed -nr \"/^exec: show " + args.show +
                           "/,/Done/p\" shell/showcmds.txt").read().strip()
        if len(showout) < 1:
            print(
                style.RED + "Incorrect show command. Please use the below available match...\n" + style.RESET)
            showsuggest = os.popen("cat shell/showcmds.txt | grep exec | grep -i " + "\"" +
                                   args.show + "\"" + " | awk '{$1=$2=\"\"}1' | cut -c3-").read().strip()
            if len(showsuggest) < 1:
                print(style.RED + "No matching show command found." + style.RESET)
                payload = {"version": version, "user": username, "action": "show -show " + args.show + " --> " + os.getcwd() + " --> " + str(
                    int(time.time())), "runtime": 0, "result": "Failed", "format": "string", "sr": os.getcwd().split("/")[3]}
                resp = request.urlopen(request.Request(
                    url, data=parse.urlencode(payload).encode()))
            else:
                print(style.CYAN + os.popen("cat shell/showcmds.txt | grep exec | grep -i " + "\"" +
                                            args.show + "\"" + " | awk '{$1=$2=\"\"}1' | cut -c3-").read().strip() + style.RESET)
                payload = {"version": version, "user": username, "action": "show -show " + args.show + " --> " + os.getcwd() + " --> " + str(
                    int(time.time())), "runtime": 0, "result": "Partial", "format": "string", "sr": os.getcwd().split("/")[3]}
                resp = request.urlopen(request.Request(
                    url, data=parse.urlencode(payload).encode()))
        else:
            print(showout)
            payload = {"version": version, "user": username, "action": "show -show " + args.show + " --> " + os.getcwd() + " --> " + str(
                int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
            resp = request.urlopen(request.Request(
                url, data=parse.urlencode(payload).encode()))
    finally:
        quit()
elif args.stat:
    try:
        logger.info(os.getcwd() + " - show -stat - " + args.stat)
        # Prining stat command output from file shell/statcmds.txt | Try without stat
        statout = os.popen("sed -nr \"/^exec: stat " + args.stat +
                           "/,/Done/p\" shell/statcmds.txt").read().strip()
        if len(statout) < 1:
            print(
                style.RED + "Incorrect stat command. Please use the below available match...\n" + style.RESET)
            statsuggest = os.popen("cat shell/statcmds.txt | grep exec | grep -i " + "\"" +
                                   args.stat + "\"" + " | awk '{$1=$2=\"\"}1' | cut -c3-").read().strip()
            if len(statsuggest) < 1:
                print(style.RED + "No matching stat command found." + style.RESET)
                payload = {"version": version, "user": username, "action": "show -stat " + args.stat + " --> " + os.getcwd() + " --> " + str(
                    int(time.time())), "runtime": 0, "result": "Failed", "format": "string", "sr": os.getcwd().split("/")[3]}
                resp = request.urlopen(request.Request(
                    url, data=parse.urlencode(payload).encode()))
            else:
                print(style.CYAN + os.popen("cat shell/statcmds.txt | grep exec | grep -i " + "\"" +
                                            args.stat + "\"" + " | awk '{$1=$2=\"\"}1' | cut -c3-").read().strip() + style.RESET)
                payload = {"version": version, "user": username, "action": "show -stat " + args.stat + " --> " + os.getcwd() + " --> " + str(
                    int(time.time())), "runtime": 0, "result": "Partial", "format": "string", "sr": os.getcwd().split("/")[3]}
                resp = request.urlopen(request.Request(
                    url, data=parse.urlencode(payload).encode()))
        else:
            print(statout)
            payload = {"version": version, "user": username, "action": "show -stat " + args.stat + " --> " + os.getcwd() + " --> " + str(
                int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
            resp = request.urlopen(request.Request(
                url, data=parse.urlencode(payload).encode()))
    finally:
        quit()
elif args.vip:
    try:
        logger.info(os.getcwd() + " - show -vip")
        # Prining formatted VIP output from file shell/ns_running_config.conf.txt
        lbvipout = os.popen(
            "awk '/^add lb/&&/vserver/{printf \"\033[0;92m%s\033[00m | %s | %s | %s | %s |\\n\", $2, $4, $5, $7, $6}' shell/ns_running_config.conf  | column -t -s'|'").read().strip()
        csvipout = os.popen(
            "awk '/^add cs/&&/vserver/{printf \"\033[0;96m%s\033[00m | %s | %s | %s | %s |\\n\", $2, $4, $7, $11, $8}' shell/ns_running_config.conf  | column -t -s'|'").read().strip()
        authvipout = os.popen(
            "awk '/^add authentication/&&/vserver/{printf \"\033[0;95m%s\033[00m | %s | %s | %s\\n\", $2, $4, $5, $6}' shell/ns_running_config.conf  | column -t -s'|'").read().strip()
        vpnvipout = os.popen(
            "awk '/^add vpn/&&/vserver/{printf \"\033[0;94m%s\033[00m | %s | %s | %s\\n\", $2, $4, $5, $6}' shell/ns_running_config.conf  | column -t -s'|'").read().strip()
    finally:
        if len(lbvipout) > 2:
            print(style.YELLOW +
                  '{:-^87}'.format('Load Balancing VIP Basic Info'))
            print(lbvipout + "\n")
        else:
            pass
        if len(csvipout) > 2:
            print(style.YELLOW +
                  '{:-^87}'.format('Content Switching VIP Basic Info'))
            print(csvipout + "\n")
        else:
            pass
        if len(authvipout) > 2:
            print(style.YELLOW +
                  '{:-^87}'.format('Authentication VIP Basic Info'))
            print(authvipout + "\n")
        else:
            pass
        if len(vpnvipout) > 2:
            print(style.YELLOW + '{:-^87}'.format('VPN VIP Basic Info'))
            print(vpnvipout + "\n")
        else:
            pass
        payload = {"version": version, "user": username, "action": "show -vip --> " + os.getcwd() + " --> " + str(int(time.time())),
                   "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
        resp = request.urlopen(request.Request(
            url, data=parse.urlencode(payload).encode()))
        quit()
elif args.case:
    # Get SFDC API Keys
    try:
        sfdcurl = "https://ftltoolswebapi.deva.citrite.net/sfaas/api/salesforce"
        tokenpayload = {"feature": "login", "parameters": [{"name": "tokenuri", "value": "https://login.salesforce.com/services/oauth2/token", "isbase64": "false"}]
                        }
        sfdcreq = request.Request(sfdcurl)
        sfdcreq.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(tokenpayload)
        jsondataasbytes = jsondata.encode('utf-8')
        sfdcreq.add_header('Content-Length', len(jsondataasbytes))
        sfdctoken = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode(
            "utf-8", "ignore"))['options'][0]['values'][0]
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
        data = {"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": ""+sfdctoken+"", "isbase64": "false"}, {"name": "selectfields", "value": "EntitlementId,Age__c", "isbase64": "false"}, {
            "name": "tablename", "value": "Case", "isbase64": "false"}, {"name": "selectcondition", "value": "CaseNumber = '"+casenum+"'", "isbase64": "false"}]}
        jsondata = json.dumps(data)
        jsondataasbytes = jsondata.encode('utf-8')
        finaldata = json.loads(request.urlopen(sfdcreq, jsondataasbytes).read().decode(
            "utf-8", "ignore"))['options'][0]['values'][0]
        EntitlementId = ast.literal_eval(finaldata)["EntitlementId"]
        CaseAge = str(ast.literal_eval(finaldata)["Age__c"])
        data = ({"feature": "selectcasequery", "parameters": [{"name": "salesforcelogintoken", "value": ""+sfdctoken+"", "isbase64": "false"}, {"name": "selectfields", "value": "EndDate", "isbase64": "false"}, {
                "name": "tablename", "value": "Entitlement", "isbase64": "false"}, {"name": "selectcondition", "value": "Id = '"+EntitlementId+"'", "isbase64": "false"}]})
        jsondata = json.dumps(data)
        jsondataasbytes = jsondata.encode('utf-8')
        Entitlement_EndDate = ast.literal_eval(json.loads(request.urlopen(
            sfdcreq, jsondataasbytes).read().decode("utf-8", "ignore"))['options'][0]['values'][0])["EndDate"]
    finally:
        print(Entitlement_EndDate + CaseAge)
elif args.author:
    logger.info(os.getcwd() + " - author")
    print(showscriptauthor)
    payload = {"version": version, "user": username, "action": "show --author --> " + os.getcwd() + " --> " + str(
        int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
    resp = request.urlopen(request.Request(
        url, data=parse.urlencode(payload).encode()))
elif args.about:
    logger.info(os.getcwd() + " - about")
    print(showscriptabout)
    payload = {"version": version, "user": username, "action": "show --about --> " + os.getcwd() + " --> " + str(
        int(time.time())), "runtime": 0, "result": "Success", "format": "string", "sr": os.getcwd().split("/")[3]}
    resp = request.urlopen(request.Request(
        url, data=parse.urlencode(payload).encode()))
elif args.G:
    try:
        path = "conFetch"
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
        else:
            pass
        if "cpu" in args.G:
            try:
                for newnslog_file in glob('var/nslog/newnslo*[!z]'):
                    adchostname = sp.run("awk '{print $2}' shell/uname-a.out",
                                         shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
                    collector_bundle_name = sp.run(
                        "pwd", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.split("/")[4]
                    time_range = sp.run(
                        "nsconmsg -K "+newnslog_file+" -d setime | awk '!/Displaying|NetScaler|size|duration/{$1=$2=\"\"; printf $0}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
                    master_cpu_use = sp.run(
                        "nsconmsg -K "+newnslog_file+" -d current -g master_cpu_use -s disptime=1 | awk 'BEGIN{q=\"\\047\"; printf \"[\"q\"Time\"q\",\"q\"CPU\"q\"],\"}/master/{q=\"\\047\"; printf \"[\"q$10q\",\" $3/10\"],\"}' | sed 's/,$//'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
                    cc_cpu_use = sp.run(
                        "nsconmsg -K "+newnslog_file+" -d current -g cc_cpu_use -s disptime=1 | awk '/cc_cpu/{print $11, $3/10, $7}' | awk 'BEGIN {;OFS = \", \";};!seen[$1]++ {;times[++numTimes] = $1;};!seen[$3]++ {;cpus[++numCpus] = $3;};{;vals[$1,$3] = $2;};END {;printf \"[\\047%s\\047%s\", \"Time\", OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];printf \"\\047%s\\047%s\", cpu, (cpuNr<numCpus ? OFS : \"]\");};for ( timeNr=1; timeNr<=numTimes; timeNr++ ) {;time = times[timeNr];printf \",%s[\\047%s\\047%s\", ORS, time, OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];val = ( (time,cpu) in vals ? vals[time,cpu] : prev_vals[cpu] );printf \"%s%s\", val, (cpuNr<numCpus ? OFS : \"]\");prev_vals[cpu] = val;};};print \"\";}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
                    if True:
                        file = open(path+"/"+newnslog_file.split("/")
                                    [2]+"_cpu_Usage.html", "w")
                        file.write('''<html><head><script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script><script src="https://cdn.jsdelivr.net/gh/manjesh23/CitrixNSConfig/scripts4internal/conFetch.js"></script><script type="text/javascript">google.charts.load('current', {'packages':['corechart']});
                                google.charts.setOnLoadCallback(master_cpu_use);
                                google.charts.setOnLoadCallback(cc_cpu_use);
                                function master_cpu_use()
                                {var data = google.visualization.arrayToDataTable(['''+master_cpu_use.stdout+''']);
                                var options = {title: 'master_cpu_use',curveType: 'function',legend: { position: 'bottom' }};
                                var chart = new google.visualization.LineChart(document.getElementById('master_cpu_use_curve_chart'));
                                chart.draw(data, options);}
                                function cc_cpu_use()
                                {var data = google.visualization.arrayToDataTable(['''+cc_cpu_use.stdout+''']);
                                var options = {title: 'cc_cpu_use',curveType: 'function',legend: { position: 'bottom' }};
                                var chart = new google.visualization.LineChart(document.getElementById('cc_cpu_use_curve_chart'));
                                chart.draw(data, options);}
                                </script><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous"><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script></head><body>
                                <h1 class="text-primary d-flex justify-content-center">conFetch CPU Graph</h1>
                                <h6>'''+collector_bundle_name+" of " + adchostname + '''</h6><h6 class="text-muted">''' + newnslog_file.split("/")[2]+":" + time_range+'''</h6>
                                <hr>
                                <div id="master_cpu_use_curve_chart" class="w-auto" style="height:450px"></div>
                                <div id="cc_cpu_use_curve_chart" class="w-auto" style="height:450px"></div>
                                </body></html>''')
                        file.close()
                        print("Processed "+newnslog_file)
            finally:
                pass
        elif "ha" in args.G:
            try:
                for newnslog_file in glob('var/nslog/newnslo*[!z]'):
                    adchostname = sp.run("awk '{print $2}' shell/uname-a.out",
                                         shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
                    collector_bundle_name = sp.run(
                        "pwd", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout.split("/")[4]
                    time_range = sp.run(
                        "nsconmsg -K "+newnslog_file+" -d setime | awk '!/Displaying|NetScaler|size|duration/{$1=$2=\"\"; printf $0}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
                    ha_tot_pkt_rx_tx = sp.run(
                        "nsconmsg -K "+newnslog_file+" -d current -s disptime=1 -g ha_tot_pkt_rx -g ha_tot_pkt_tx | awk '/ha_tot/{print $10, $4, $6}' | awk 'BEGIN {;OFS = \", \";};!seen[$1]++ {;times[++numTimes] = $1;};!seen[$3]++ {;cpus[++numCpus] = $3;};{;vals[$1,$3] = $2;};END {;printf \"[\\047%s\\047%s\", \"Time\", OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];printf \"\\047%s\\047%s\", cpu, (cpuNr<numCpus ? OFS : \"]\");};for ( timeNr=1; timeNr<=numTimes; timeNr++ ) {;time = times[timeNr];printf \",%s[\\047%s\\047%s\", ORS, time, OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];val = ( (time,cpu) in vals ? vals[time,cpu] : prev_vals[cpu] );printf \"%s%s\", val, (cpuNr<numCpus ? OFS : \"]\");prev_vals[cpu] = val;};};print \"\";}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
                    ha_err_heartbeat = sp.run(
                        "nsconmsg -K "+newnslog_file+" -d current -s disptime=1 -g ha_err_heartbeat | awk '/ha_/{print $10, $4, $6}' | awk 'BEGIN {;OFS = \", \";};!seen[$1]++ {;times[++numTimes] = $1;};!seen[$3]++ {;cpus[++numCpus] = $3;};{;vals[$1,$3] = $2;};END {;printf \"[\\047%s\\047%s\", \"Time\", OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];printf \"\\047%s\\047%s\", cpu, (cpuNr<numCpus ? OFS : \"]\");};for ( timeNr=1; timeNr<=numTimes; timeNr++ ) {;time = times[timeNr];printf \",%s[\\047%s\\047%s\", ORS, time, OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];val = ( (time,cpu) in vals ? vals[time,cpu] : prev_vals[cpu] );printf \"%s%s\", val, (cpuNr<numCpus ? OFS : \"]\");prev_vals[cpu] = val;};};print \"\";}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
                    ha_tot_macresolve_requests = sp.run(
                        "nsconmsg -K "+newnslog_file+" -d current -s disptime=1 -g ha_tot_macresolve_requests | awk '/ha_/{print $10, $4, $6}' | awk 'BEGIN {;OFS = \", \";};!seen[$1]++ {;times[++numTimes] = $1;};!seen[$3]++ {;cpus[++numCpus] = $3;};{;vals[$1,$3] = $2;};END {;printf \"[\\047%s\\047%s\", \"Time\", OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];printf \"\\047%s\\047%s\", cpu, (cpuNr<numCpus ? OFS : \"]\");};for ( timeNr=1; timeNr<=numTimes; timeNr++ ) {;time = times[timeNr];printf \",%s[\\047%s\\047%s\", ORS, time, OFS;for ( cpuNr=1; cpuNr<=numCpus; cpuNr++ ) {;cpu = cpus[cpuNr];val = ( (time,cpu) in vals ? vals[time,cpu] : prev_vals[cpu] );printf \"%s%s\", val, (cpuNr<numCpus ? OFS : \"]\");prev_vals[cpu] = val;};};print \"\";}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
                    if True:
                        file = open(path+"/"+newnslog_file.split("/")
                                    [2]+"_HA.html", "w")
                        file.write('''<html><head><script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script><script src="https://cdn.jsdelivr.net/gh/manjesh23/CitrixNSConfig/scripts4internal/conFetch.js"></script><script type="text/javascript">google.charts.load('current', {'packages':['corechart']});
                                google.charts.setOnLoadCallback(ha_tot_pkt_rx_tx);
                                google.charts.setOnLoadCallback(ha_err_heartbeat);
                                google.charts.setOnLoadCallback(ha_tot_macresolve_requests);
                                function ha_tot_pkt_rx_tx()
                                {var data = google.visualization.arrayToDataTable(['''+ha_tot_pkt_rx_tx.stdout+''']);
                                var options = {title: 'ha_tot_pkt_rx_tx',curveType: 'function',legend: { position: 'bottom' }};
                                var chart = new google.visualization.LineChart(document.getElementById('ha_tot_pkt_rx_tx_curve_chart'));
                                chart.draw(data, options);}
                                function ha_err_heartbeat()
                                {var data = google.visualization.arrayToDataTable(['''+ha_err_heartbeat.stdout+''']);
                                var options = {title: 'ha_err_heartbeat',curveType: 'function',legend: { position: 'bottom' }};
                                var chart = new google.visualization.LineChart(document.getElementById('ha_err_heartbeat_curve_chart'));
                                chart.draw(data, options);}
                                function ha_tot_macresolve_requests()
                                {var data = google.visualization.arrayToDataTable(['''+ha_tot_macresolve_requests.stdout+''']);
                                var options = {title: 'ha_tot_macresolve_requests',curveType: 'function',legend: { position: 'bottom' }};
                                var chart = new google.visualization.LineChart(document.getElementById('ha_tot_macresolve_requests_curve_chart'));
                                chart.draw(data, options);}
                                </script><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous"><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script></head><body>
                                <h1 class="text-primary d-flex justify-content-center">conFetch HA Graph</h1>
                                <h6>'''+collector_bundle_name+" of " + adchostname + '''</h6><h6 class="text-muted">''' + newnslog_file.split("/")[2]+":" + time_range+'''</h6>
                                <hr>
                                <div id="ha_tot_pkt_rx_tx_curve_chart" class="w-auto" style="height:450px"></div>
                                <div id="ha_err_heartbeat_curve_chart" class="w-auto" style="height:450px"></div>
                                <div id="ha_tot_macresolve_requests_curve_chart" class="w-auto" style="height:450px"></div>
                                </body></html>''')
                        file.close()
                        print("Processed "+newnslog_file)
            finally:
                pass
    finally:
        pass
else:
    print("Please use -h for help")
    logger.error(os.getcwd() + " - No switch")
    payload = {"version": version, "user": username, "action": "No Switch Used " + os.getcwd() + " --> " + str(
        int(time.time())), "runtime": 0, "result": "Error", "format": "string", "sr": os.getcwd().split("/")[3]}
    resp = request.urlopen(request.Request(
        url, data=parse.urlencode(payload).encode()))
