#!/usr/local/bin/bash
caseformat="^[0-9]{8}"
url="https://tooltrack.deva.citrite.net/use/conFetch"
ver="1.2"
datad="datad--$1--$(date +%s)"
s="Success"
f="Failed"
i="Invalid"
successq="version=$ver&user=$(whoami)&sr=$1&action=$datad&runtime=0&result=$s&format=string"
failedq="version=$ver&user=$(whoami)&sr=$1&action=$datad&runtime=0&result=$f&format=string"
invalidq="version=$ver&user=$(whoami)&sr=$1&action=$datad&runtime=0&result=$i&format=string"
if [[ $1 =~ $caseformat ]];
  then
    cd $(echo /upload/ftp/$1) >/dev/null 2>&1
    if [ $? -eq 0 ];
      then
        echo "$(date) -- $(whoami) -- used datad -- OK" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"
        curl --silent --data $successq $url >/dev/null 2>&1
      else
        echo -e "\e[31m/upload/ftp/$1 unable to navigate to case directory\e[0m"
        echo "$(date) -- $(whoami) -- used datad -- Invalid" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"
        curl --silent --data $invalidq $url >/dev/null 2>&1
    fi
  else
    echo -e "\e[31m/upload/ftp/$1 is not a valid case number\e[0m"
    echo "$(date) -- $(whoami) -- used datad -- Failed" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"
    curl --silent --data $failedq $url >/dev/null 2>&1
fi