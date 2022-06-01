#!/usr/local/bin/bash
if [[ "$1" =~ ^[0-9]+$ ]] ;
  then
    cd $(echo /upload/ftp/$1)
else
  echo "/upload/ftp/$1 is not a case number"
fi