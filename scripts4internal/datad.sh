#!/usr/local/bin/bash
caseformat="^[0-9]{8}"
url="https://tooltrack.deva.citrite.net/use/conFetch"
ver="1.8"
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
        # Log the datad usage into local file (Use only in the absence of tooltrack)
        # echo "$(date) -- $(whoami) -- used datad -- OK" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"        
        # Find and print all the collector bundles of NetScaler (Including nested directories) | Escapes the space and round bracket with backslash
        find ./ -type d -name "collector_*" -exec ls -ld {} + | cut -d: -f2- | cut -c 6- | sed 's/ /\\ /g' | sed 's/(/\\(/g' | sed 's/)/\\)/g' | awk 'BEGIN{printf "\n\t%s\n\n", "\033[1;97mCollector_Bundles\033[0m"}!/tar|gz/{printf "%s%s\n", "\033[36m","./"$0"\033[0m"}'
        # Checks and prints all nsconmsg counters within the newnslog into Collector bundle + conFetch/nsconmsg/nsconmsg_counters.txt
        for i in $(find . -name "collector_*" -type d -exec printf "%s/conFetch/nsconmsg/nsconmsg_counters.txt\n" {} +); do if ! [ -e "$i" ]; then screen -dmS "nsconmsg_counter" bash -c 'for i in $(find . -type d -name "collector_*" | sed "s/ /\\ /g" | sed "s/(/\\(/g" | sed "s/)/\\)/g"); do mkdir -p $i"/conFetch/nsconmsg"; nsconmsg -K $i/var/nslog/newnslog -d current | awk '\''!/reltime|Index/{print $6}'\'' | sort | uniq -c | egrep '\''([a-z].*[_]).*'\'' > $i"/conFetch/nsconmsg/nsconmsg_counters.txt"; done'; fi; done
        # Checks and prints all nsconmsg filenames + conFetch/nsconmsg/newnslog_names.txt
        #screen -dmS "newnslog_names" bash -c 'for i in $(find ./ -type d -name "collector_*" | sed "s/ /\\ /g" | sed "s/(/\\(/g" | sed "s/)/\\)/g"); do mkdir -p $i"/conFetch/nsconmsg"; j=$(find $i/ -type d -name "newnslog.*" | sort); echo $j | sed '\''s/ .\//\n.\//g'\'' | awk -F/ '\''{print "var/nslog/"$NF}END{print "var/nslog/newnslog"}'\'' > $i/conFetch/nsconmsg/newnslog_names.txt;done'
        # Checks and creates newnslog setime (Only the very first and very last) + conFetch/nsconmsg/newnslog_setime.txt
        #screen -dmS "newnslog_setime" bash -c 'for i in $(find . -type d -name "collector_*" | sed "s/ /\\ /g" | sed "s/(/\\(/g" | sed "s/)/\\)/g"); do echo $(nsconmsg -K "$i/"$(ls -lah "$i/var/nslog/" | grep -v tar | grep -v gz | awk '\''/newnslog./{printf "var/nslog/"$NF; exit}'\'' | sed -n '1p') -d setime | awk '\''/start/&&!/Displaying/{$1=$2=""; printf }'\'' | awk '\''{$1=$1=""}1'\''; printf " --> "; nsconmsg -K $i/var/nslog/newnslog -d setime | awk '\''/end/&&!/Displaying/{$1=$2=""; print}'\'' | awk '\''{$1=$1=""}1'\'') > $i/conFetch/nsconmsg/newnslog_setime.txt; done'
        # Fix file permission
        #screen -dmS "fixperms 30" sleep 30 && fixperms ./ > /dev/null 2>&1
        #screen -dmS "fixperms 300" sleep 300 && fixperms ./ > /dev/null 2>&1
        # Write the datad usage to tooltrack
        screen -dmS "tooltrack" curl --silent --data $successq $url >/dev/null 2>&1
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