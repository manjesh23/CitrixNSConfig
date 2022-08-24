#!/usr/local/bin/python
from asyncio import subprocess
import os
import subprocess as sp
import logging
import argparse
from operator import itemgetter
import re
from os.path import exists as file_exists


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


# About script
showscriptabout = '''
Note -- Please do not use this script if you are not sure of what you are doing.
Product -- Only for Citrix TAC Use.
Unauthorized usage of this script / sharing for personal use will be considered as offence.
This script is designed to extract data from support bundle -- "script based troubleshooting".
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

# Citrix Analyzer
citrixanalyzer = '''                                                                                                                                 
             ,,                   ,,                                                      ,,                                     
  .g8"""bgd  db   mm              db                       db                           `7MM                                     
.dP'     `M       MM                                      ;MM:                            MM                                     
dM'       ``7MM mmMMmm `7Mb,od8 `7MM  `7M'   `MF'        ,V^MM.    `7MMpMMMb.   ,6"Yb.    MM `7M'   `MF',pP"Ybd  .gP"Ya `7Mb,od8 
MM           MM   MM     MM' "'   MM    `VA ,V'         ,M  `MM      MM    MM  8)   MM    MM   VA   ,V  8I   `" ,M'   Yb  MM' "' 
MM.          MM   MM     MM       MM      XMX           AbmmmqMA     MM    MM   ,pm9MM    MM    VA ,V   `YMMMa. 8M""""""  MM     
`Mb.     ,'  MM   MM     MM       MM    ,V' VA.        A'     VML    MM    MM  8M   MM    MM     VVV    L.   I8 YM.    ,  MM     
  `"bmmmd' .JMML. `Mbmo.JMML.   .JMML..AM.   .MA.    .AMA.   .AMMA..JMML  JMML.`Moo9^Yo..JMML.   ,V     M9mmmP'  `Mbmmd'.JMML.   
                                                                                                ,V                               
                                                                                             OOb"                                '''

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
parser.add_argument('-gz', action="store_true",
                    help="Unzip *.gz files under /var/log and vsr/nslog")
parser.add_argument('-im', action="store_true",
                    help="Indexing timestamp of ns.log")
parser.add_argument('-imall', action="store_true",
                    help="Indexing timestamp of logs including ns, auth, bash, nitro, notice, nsvpn, sh")
parser.add_argument('-error', metavar="", help="Highlights known errors")
parser.add_argument('-show', metavar="", help="Selected Show Commands")
parser.add_argument('-stat', metavar="", help="Selected Stat Commands")
parser.add_argument('--about', action="store_true",
                    help="About Show Script")
args = parser.parse_args()

# Logme the user
username = os.popen("whoami").read().strip()
userfile = "/home/CITRITE/manjeshn/manscript/showdata/"+username+".log"
logging.basicConfig(filename=userfile,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Set correct support bundle path
# try:
#     os.chdir("/"+"/".join(itemgetter(1, 2, 3, 4)(os.getcwd().split("/"))))
# except IndexError:
#     print("\nPlease navigate to correct support bundle path")
#     print("Available directories with support bundle names: \n\n" + style.CYAN +
#           "\n".join(re.findall("collect.*", "\n".join(next(os.walk('.'))[1]))) + style.RESET)
#     quit()

try:
    if (os.popen("pwd").read().index("collector") >= 0):
        os.chdir(
            re.search('.*\/collecto.*_[0-9]{2}', os.popen("pwd").read()).group(0))
except ValueError:
    print("\nPlease navigate to correct support bundle path")
    print("Available directories with support bundle names: \n\n" + style.CYAN +
          "\n".join(re.findall("collect.*", "\n".join(next(os.walk('.'))[1]))) + style.RESET)
    quit()

    # Assign correct files and its path to variables
try:
    nsconf = "nsconfig/ns.conf"
    showcmd = "shell/showcmds.txt"
    statcmd = "shell/statcmds.txt"
    sysctl = "shell/sysctl-a.out"
    uptime = "shell/uptime.out"
    df = "shell/df-akin.out"
    allrequiredfiles = [nsconf] + [showcmd] + \
        [statcmd] + [sysctl] + [uptime] + [df]
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
        platformserial = sp.run(
            "sed -n '/^exec: show ns hardware/,/Done/p' shell/showcmds.txt | awk '/Serial/{print $NF}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        platformmodel = sp.run(
            "sed -n '/^exec: show ns hardware/,/Done/p' shell/showcmds.txt | awk '/Platform/{print $1=\"\"; print}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        licmodel = sp.run("awk '/Users/{print}' var/log/license.log | awk -F: '{print $1}' | awk '{printf \"%s | \", $NF}' | sed 's/..$//'",
                          shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        hwplatform = sp.run("awk '/platform/{$1=\"\"; print}' shell/sysctl-a.out | awk -F',' '/manufactured/{print $1}' | head -n1",
                            shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        vmplatform = sp.run("awk '/^platform.* on/{$1=\"\"; print}' shell/sysctl-a.out | head -n1",
                            shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        licensetype = sp.run("awk '/License Type/{$1=$2=\"\"; print}' shell/showcmds.txt",
                             shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        licensemode = sp.run(
            "awk '/Licensing mode/{$1=$2=\"\"; print}' shell/showcmds.txt", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        #nsipsub = sp.run("sed -n -e \"/exec: show ns version/I,/Done/ p\" shell/showcmds.txt | grep mask | awk -FIP: '{print $2}'", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsip = sp.run(
            "sed -n '/ns config/,/Done/p' shell/showcmds.txt | grep \"NetScaler IP\" | egrep -o \"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\" | grep -v 255", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsipsubnet = sp.run(
            "sed -n '/ns config/,/Done/p' shell/showcmds.txt | grep \"NetScaler IP\" | egrep -o \"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\" | grep 255", shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsfeatures = sp.run("awk '/ns feature/{$1=$2=$3=\"\";print $0}' nsconfig/ns.conf",
                            shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
        nsmode = sp.run("awk '/ns mode/{$1=$2=$3=\"\";print $0}' nsconfig/ns.conf",
                        shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
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
        quit()
elif args.p:
    try:
        logger.info(os.getcwd() + " - show -p")
        vcpu = sp.run("awk '/System Detected/{print $(NF-1), $NF;exit}' var/nslog/dmesg.boot",
                      shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
    finally:
        print(style.YELLOW + '{:-^87}'.format('ADC Process Information'))
        print(style.RESET)
        print("Number of vCPU: " + vcpu.stdout)
elif args.E:
    try:
        print(style.YELLOW +
              '{:-^87}'.format('Errors and Matched KB Articles') + style.RESET+"\n")
        print(os.popen(
            "for i in $(ls -lah var/log/ | awk '/ns.lo*/{print $NF}'); do awk 'BEGIN{c=0}/\"ERROR: Operation not permitted - no FIPS card present in the system\"/{c++}END {if(c > 0){printf \"%s\\t%s\\t%s\\t%s\\n\", ARGV[1], c, \"ERROR: Operation not permitted - no FIPS card present in the system\", \"https://support.citrix.com/article/CTX330685\"}}' var/log/$i; done").read().strip())
        print("\n")
    finally:
        quit()
elif args.gz:
    try:
        logger.info(os.getcwd() + " - show -gz")
        # Unzip all gz files under ./var/log
        gunzipresult = sp.run("gunzip -v var/log/*.gz",
                              shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        # Unzip all gz files under ./var/nslog
        gunzipnewnsresult = sp.run(
            "for i in var/nslog/new*.tar.gz; do tar -xvf \"$i\" -C var/nslog/; done", shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    finally:
        if gunzipresult.returncode == 0:
            print(style.YELLOW +
                  '{:-^87}\n'.format('Gunzip all .gz files under /var/log') + style.RESET)
            print(style.YELLOW + str(gunzipresult.stderr.decode('utf-8')) + style.RESET)
            print(style.GREEN + "Extracted all files in var/log!!!" + style.RESET)
        else:
            print(style.RED + "Nothing to do here in var/log/" + style.RESET)
        if gunzipnewnsresult.returncode == 0:
            print(style.YELLOW +
                  '{:-^87}\n'.format('Gunzip all .gz files under /var/log') + style.RESET)
            print(style.YELLOW +
                  str(gunzipnewnsresult.stderr.decode('utf-8')) + style.RESET)
            print(style.GREEN + "Extracted all files var/nslog!!!" + style.RESET)
        else:
            print(style.RED + "Nothing to do here in var/nslog/" + style.RESET)
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
        quit()
elif args.error:
    try:
        logger.info(os.getcwd() + " - show -error")
        # Highlight all the ERROR|err|down|disconnect|fail containing lines in input file.
        print(sp.run("if test -f var/log/" + args.error +
              "; then awk '/ERROR|err|Err|down|disconnect|fail/{print \"\033[1;31m\"$0\"\033[0m\";next}{print $0}' var/log/" + args.error + "; else echo \"File not found\"; fi", shell=True).stdout)
    finally:
        quit()
elif args.show:
    try:
        logger.info(os.getcwd() + " - show -show - " + args.show)
        # Prining show command output from file shell/statcmd.txt | Try without show
        print(os.popen("sed -nr \"/^exec: show " + args.show +
              "/,/Done/p\" shell/showcmds.txt").read().strip())
    finally:
        quit()
elif args.stat:
    try:
        logger.info(os.getcwd() + " - show -stat - " + args.stat)
        # Prining stat command output from file shell/showcmd.txt | Try without show
        print(os.popen("sed -nr \"/^exec: stat " + args.stat +
              "/,/Done/p\" shell/statcmds.txt").read().strip())
    finally:
        quit()
elif args.author:
    logger.info(os.getcwd() + " - author")
    print(showscriptauthor)
elif args.about:
    logger.info(os.getcwd() + " - about")
    print(showscriptabout)
else:
    print("Please use -h for help")
    logger.error(os.getcwd() + " - No switch")
