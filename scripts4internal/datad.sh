#!/usr/local/bin/bash
echo you entered $1
if [[ "$1" =~ ^[0-9]+$ ]] ;
  then
    casepath="/upload/ftp/$1"
    echo "Getting you to $casepath"
    cd $(echo $casepath)
  else
    echo "$input is not an integer or not defined"
  fi