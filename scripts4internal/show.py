#!/usr/local/bin/python
import os
import sys
import argparse

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
##############################################################
##                                                          ##
##    Script credit Manjesh Setty | manjesh.n@citrix.com    ##
##                                                          ##
##############################################################
'''

parser = argparse.ArgumentParser(
    description="Citrix Support Bundle Show Script")
parser.add_argument('--author', action="store_true",
                    help=argparse.SUPPRESS)
parser.add_argument('-i', action="store_true",
                    help="ADC Basic Information")
parser.add_argument('-im', action="store_true",
                    help="Indexing timestamp of logs including ns, auth, bash, nitro, notice, nsvpn, sh")
parser.add_argument('-a', action="store_true",
                    help="About Show Script")
args = parser.parse_args()

if args.i:
    try:
        # Printing system essential details
        os.system('clear')
        print('{:-^65}\n'.format('ADC Show Configuration'))
        print("ADC Firmware version: " +
              os.popen("cat nsconfig/ns.conf | grep \"#NS\" | cut -c 2-").read().strip())
        print("Platform Serial: " +
              os.popen("awk '/platform: serial/{print $NF;exit}' var/log/mess*").read().strip())
        print("Platform Model: " + os.popen(
            "awk \'/ns/&&/kernel: platform: sysid/{$NF;gsub(/Appliance/,\"Virtual Appliance\",$NF); print $NF;exit}\' var/log/mess*").read().strip())
        print("NSIP Address: " + os.popen(
            "sed -n '/ns config/,/Done/p' shell/showcmds.txt | grep \"NetScaler IP\" | egrep -o \"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\" | grep -v 255").read().strip() + " | " + os.popen("sed -n '/ns config/,/Done/p' shell/showcmds.txt | grep \"NetScaler IP\" | egrep -o \"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\" | grep 255").read().strip())
        print("NS Enabled Feature: " + os.popen(
            "awk \'/ns feature/{$1=$2=$3=\"\";print $0}\' nsconfig/ns.conf").read().strip())
        print("NS Enabled Mode: " + os.popen(
            "awk \'/ns mode/{$1=$2=$3=\"\";print $0}\' nsconfig/ns.conf").read().strip())
        print("Collector pack generated @ " +
              os.popen("cat shell/date.out").read().strip())
        print("Device uptime: " +
              os.popen("sed 's/^.*up //' shell/uptime.out | sed 's/,...users.*//'").read().strip() + "\n")
    finally:
        quit()
elif args.im:
    try:
        os.system('clear')
        print('{:-^65}\n'.format('ADC ns.log timestamp IndexMessages') + os.popen(
            "awk \'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}\'; for i in $(printf \'%s\n\' var/log/ns.lo*); do awk \'NR == 1 {printf \"%s %s %s\\t| \", $1,$2,$3}END{printf \"%s %s %s | %s\\n\",  $1,$2,$3,ARGV[1]}\' $i; done").read().strip() + "\n")
        print('{:-^65}\n'.format('ADC auth.log timestamp IndexMessages') + os.popen(
            "awk \'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}\'; for i in $(printf \'%s\n\' var/log/auth.lo*); do awk \'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,ARGV[1]}\' $i; done").read().strip() + "\n")
        print('{:-^65}\n'.format('ADC bash.log timestamp IndexMessages') + os.popen(
            "awk \'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}\'; for i in $(printf \'%s\n\' var/log/bash.lo*); do awk \'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,ARGV[1]}\' $i; done").read().strip() + "\n")
        print('{:-^65}\n'.format('ADC nitro.log timestamp IndexMessages') + os.popen(
            "awk \'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}\'; for i in $(printf \'%s\n\' var/log/nitro.lo*); do awk \'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,ARGV[1]}\' $i; done").read().strip() + "\n")
        print('{:-^65}\n'.format('ADC notice.log timestamp IndexMessages') + os.popen(
            "awk \'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}\'; for i in $(printf \'%s\n\' var/log/notice.lo*); do awk \'NR == 1 {printf \"%s %s %s\\t| \", $1,$2,$3}END{printf \"%s %s %s | %s\\n\",  $1,$2,$3,ARGV[1]}\' $i; done").read().strip() + "\n")
        print('{:-^65}\n'.format('ADC nsvpn.log timestamp IndexMessages') + os.popen(
            "awk \'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}\'; for i in $(printf \'%s\n\' var/log/nsvpn.lo*); do awk \'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,ARGV[1]}\' $i; done").read().strip() + "\n")
        print('{:-^65}\n'.format('ADC sh.log timestamp IndexMessages') + os.popen(
            "awk \'BEGIN{printf \"%s\\t| %s\\t  | %s\\n\", \"Start_Time\",\"End_Time\",\"File_Name\"}\'; for i in $(printf \'%s\n\' var/log/sh.lo*); do awk \'NR == 1 {printf \"%s %02d %s\\t| \", $1,$2,$3}END{printf \"%s %02d %s | %s\\n\",  $1,$2,$3,ARGV[1]}\' $i; done").read().strip() + "\n")
    finally:
        quit()
elif args.author:
    print(showscriptauthor)
elif args.a:
    print(showscriptabout)
else:
    print("Please use -h for help")
