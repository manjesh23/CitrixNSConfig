#!/usr/local/bin/python3.9
import os
import subprocess as sp
import argparse
import re

parser = argparse.ArgumentParser(description="Project conFetch Wrapper", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', action="append", help="Provide Collector bundle absolute path")
args = parser.parse_args()

# Input file name to variable
NSPath = ''.join(args.i)

# show command options
showcmd = ["i", "stat \"system memory\"", "p", "v", "-case"]

if args.i:
    try:
        os.chdir(NSPath)
        os.system("fixperms ./ > /dev/null")
        for Switch in showcmd:
            conFetch_Out = sp.run("python /home/CITRITE/manjeshn/manscript/show.py -" + Switch, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE).stdout
            pattern = r'\x1b\[[0-9;]*m'
            output = re.sub(pattern, '', conFetch_Out)
            print(output)
    finally:
        os.system("fixperms ./ > /dev/null")
        pass
else:
    print("For use of conFetch_Wrapper, please use conFetch -h")
