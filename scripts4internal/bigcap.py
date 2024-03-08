#!/usr/local/bin/python3.7
#!/usr/local/bin/tshark

from os.path import exists as file_exists
import os
from os import path
import subprocess as sp
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

# Parser args
parser = argparse.ArgumentParser(description="Project bigCap", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--trace', metavar="", action="append", help="nstrace File")
parser.add_argument('--sslkey', metavar="", action="append", help="SSL Key File")
parser.add_argument('-i', action="store_true", help="Trace File Basic Information")
args = parser.parse_args()

try:
    if not args.trace:
        print(style.RED + "Nothing to run without trace file" + style.RESET)
        quit()
    if not args.sslkey:
        print(style.RED + "SSL Decryption without SSLKey file is not possbile" + style.RESET)
        trace_file = './'.join(args.trace[0])
    else:
        trace_file = './'.join(args.trace[0])
        sslkey_file = './'.join(args.sslkey[0])
except:
    print(style.RED + "Something broken" + style.RESET)
    quit()

if args.i:
    if file_exists(trace_file):
        print("Success")
    else:
        print("No file")