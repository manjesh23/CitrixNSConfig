# This is a wrapper script to use show commands under Project conFetch. Advanced to usage within bigfoot

#!/usr/local/bin/python3.9
import os
import subprocess as sp
import argparse

parser = argparse.ArgumentParser(
    description="Project conFetch Wrapper", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-i', action="append",
                    help="Provide Collector bundle absolute path")
args = parser.parse_args()

# Input file name to variable
NSPath = ''.join(args.i)

# show command options
showcmd = ["i", "stat \"system memory\"", "p", "v"]

if args.i:
    try:
        os.chdir(NSPath)
        os.system("fixperms ./ > /dev/null")
        for Switch in showcmd:
            conFetch_Out = sp.run(
                "python /home/CITRITE/manjeshn/manscript/show.py -" + Switch, shell=True, text=True, stdout=sp.PIPE, stderr=sp.PIPE)
            print(conFetch_Out.stdout)
    finally:
        os.system("fixperms ./ > /dev/null")
        pass
elif args.i:
    print("You have provided only Collector bundle. Please input Ouput file path and name.")
else:
    print("For use of conFetch_Wrapper, please use conFetch -h")
