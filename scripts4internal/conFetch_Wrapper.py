## This is a wrapper script to use show commands under Project conFetch. Advanced to usage within bigfoot ##

#!/usr/local/bin/python3.9
import os
import subprocess as sp
import argparse
import pathlib


parser = argparse.ArgumentParser(
    description="Project conFetch Wrapper", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-NSPath', action="append",
                    help="Provide Collector absolute path")
parser.add_argument('-Switch', action="append",
                    help="conFetch Switch")
args = parser.parse_args()

# conFetch Dir
path = "conFetch/Preprocessor"

if args.NSPath and args.Switch:
    try:
        for NSPath in args.NSPath:
            os.chdir(NSPath)
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            os.system("fixperms ./ > /dev/null")
            os.chdir(path)
            for Switch in args.Switch:
                f = open(Switch+".txt", "w")
                conFetch_Out = sp.run(
                    "python /home/CITRITE/manjeshn/manscript/show.py -" + Switch, shell=True, text=True, stdout=f, stderr=sp.PIPE)
    except FileNotFoundError as e:
        print(e)
    finally:
        pass
elif args.NSPath:
    try:
        print("You have provided only Collector bundle. Please input show Switch.")
    finally:
        pass

elif args.Switch:
    try:
        print("You have provided only show Switch. Please input Collector bundle absolute path.")
    finally:
        pass
else:
    try:
        print("For use of ")
    finally:
        pass
