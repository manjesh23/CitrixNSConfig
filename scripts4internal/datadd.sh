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
if [[ $1 =~ $caseformat ]]; then
  cd "/upload/ftp/$1" >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    # find directories containing "collector_" pattern
    find . -type d -name '*collector_*' | while read dir; do
    # create a conFetch directory structure
    mkdir -p "${dir}/conFetch/nsconmsg" "${dir}/conFetch/Graph" "${dir}/conFetch/show_output"
    # run command inside the directory
    (cd "${dir}" && show -gz > /dev/null 2>&1 &)
    (cd "${dir}" && [ ! -e "conFetch/show_output/show_imall.txt" ] && show -imall > "conFetch/show_output/show_imall.txt" 2>&1 &)
    (cd "${dir}" && [ ! -e "conFetch/show_output/show_ha.txt" ] && show -ha > "conFetch/show_output/show_ha.txt" 2>&1 &)
    (cd "${dir}" && [ ! -e "conFetch/nsconmsg/nsconmsg_counters.txt" ] && nsconmsg -K var/nslog/newnslog -d current | awk '!/reltime|Index/{print $6}' | sort | uniq -c | egrep '([a-z].*[_]).*' > "conFetch/nsconmsg/nsconmsg_counters.txt" 2>&1 &)
    curl --silent --data $successq $url >/dev/null 2>&1
done
    # display the list of matching directories
    find ./ -type d -name "collector_*" -exec ls -ld {} + | cut -d: -f2- | cut -c 6- | sed 's/ /\\ /g' | sed 's/(/\\(/g' | sed 's/)/\\)/g' | awk 'BEGIN{printf "\n\t%s\n\n", "\033[1;97mCollector_Bundles\033[0m"}!/tar|gz/{printf "%s%s\n", "\033[36m","./"$0"\033[0m"}'
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
screen -dmS "fixperms" fixperms ./
