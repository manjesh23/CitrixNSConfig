#!/usr/local/bin/bash
caseformat="^[0-9]{8}"
url="https://tooltrack.deva.citrite.net/use/conFetch"
ver="2.4"
datad="datad--$1--$(date +%s)"
s="Success"
f="Failed"
i="Invalid"
successq="version=$ver&user=$(whoami)&sr=$1&action=$datad&runtime=0&result=$s&format=string"
failedq="version=$ver&user=$(whoami)&sr=$1&action=$datad&runtime=0&result=$f&format=string"
invalidq="version=$ver&user=$(whoami)&sr=$1&action=$datad&runtime=0&result=$i&format=string"

if [[ $1 =~ $caseformat ]]; then
    cd $(echo /upload/ftp/$1) >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        # Find and print all the collector bundles of NetScaler (Including nested directories)
        [ "$(find ./ -type d -name 'collector_*')" ] && find ./ -type d -name "collector_*" -exec ls -ld {} + | cut -d: -f2- | cut -c 6- | sed 's/ /\\ /g' | sed 's/(/\\(/g' | sed 's/)/\\)/g' | awk 'BEGIN{printf "\n\t%s\n\n", "\033[1;97mCollector_Bundles\033[0m"}!/tar|gz/{printf "%s%s\n", "\033[36m","./"$0"\033[0m"}'
        [ "$(find ./ -type d -name 'NetScaler_ADM_*mps')" ] && find ./ -type d -name "NetScaler_ADM_*mps" -exec ls -ld {} + | cut -d: -f2- | cut -c 6- | sed 's/ /\\ /g' | sed 's/(/\\(/g' | sed 's/)/\\)/g' | awk 'BEGIN{printf "\n\t%s\n\n", "\033[1;97mNetScaler_ADM_Bundles\033[0m"}!/tar|gz/{printf "%s%s\n", "\033[36m","./"$0"\033[0m"}'
        [ "$(find ./ -type d -name 'Citrix_ADM_*mps')" ] && find ./ -type d -name "Citrix_ADM_*mps" -exec ls -ld {} + | cut -d: -f2- | cut -c 6- | sed 's/ /\\ /g' | sed 's/(/\\(/g' | sed 's/)/\\)/g' | awk 'BEGIN{printf "\n\t%s\n\n", "\033[1;97mCitrix_ADM_Bundles\033[0m"}!/tar|gz/{printf "%s%s\n", "\033[36m","./"$0"\033[0m"}'
        echo -e "\033[5;33m\nCheck out the new features! Use \`show --help\` to learn more.\033[0m"
        # Write the datad usage to tooltrack
        screen -dmS "tooltrack" curl -k --silent --data $successq $url >/dev/null 2>&1
    else
        echo -e "\e[31m/upload/ftp/$1 unable to navigate to case directory\e[0m"
        echo "$(date) -- $(whoami) -- used datad -- Invalid" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"
        curl -k --silent --data $invalidq $url >/dev/null 2>&1
    fi
else
    echo -e "\e[31m/upload/ftp/$1 is not a valid case number\e[0m"
    echo "$(date) -- $(whoami) -- used datad -- Failed" >> "/home/CITRITE/manjeshn/manscript/showdata/$(whoami).datad.txt"
    curl -k --silent --data $failedq $url >/dev/null 2>&1
fi
