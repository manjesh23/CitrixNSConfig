#!/usr/local/bin/python

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("casenum")
args = parser.parse_args()

try:
    val = int(args.casenum)
    if args.casenum == 'manjesh':
        print('You did called Manjesh, whatsup')
    else:
        try:
            path = "/upload/ftp/" + args.casenum
            print("Getting you to " + path)
            os.chdir(path)
        except FileNotFoundError:
            print("Looks like the case directory is not on sjanalysis server !!!")
except ValueError:
    print("You need to enter case number only !!!")
