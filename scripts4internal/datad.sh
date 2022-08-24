#!/usr/local/bin/bash
if [[ "$1" =~ ^[0-9]+$ ]] ;
  then
    cd $(echo /upload/ftp/$1)
    echo "$(date) -- $(whoami) -- used datad -- OK" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"
else
  echo "/upload/ftp/$1 is not a case number"
  echo "$(date) -- $(whoami) -- used datad -- OK" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"
fi