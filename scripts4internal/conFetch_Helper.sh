#!/usr/local/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 -i <directory>"
    echo "Example: $0 -i /path/to/directory"
}

# Check if the number of arguments is correct
if [ "$#" -ne 2 ]; then
    usage
    exit 1
fi

# Parse command line options
while getopts ":i:" opt; do
    case $opt in
        i)
            directory="$OPTARG"
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            exit 1
            ;;
    esac
done

# Check if the directory exists and navigate to it
cd "$directory" >/dev/null 2>&1
if [ $? -eq 0 ]; then
  # create a conFetch directory structure
  mkdir -p "conFetch/nsconmsg" "conFetch/Graph" "conFetch/show_output"
  # Run commands inside the directory
  (show -gz > /dev/null 2>&1 &)
  ([ ! -e "conFetch/show_output/show_imall.txt" ] && python /usr/local/bigfoot/python_scripts/show.py -imall > "conFetch/show_output/show_imall.txt" 2>&1 &)
  ([ ! -e "conFetch/show_output/show_ha.txt" ] && python /usr/local/bigfoot/python_scripts/show.py -ha > "conFetch/show_output/show_ha.txt" 2>&1 &)
  ([ ! -e "conFetch/nsconmsg/nsconmsg_counters.txt" ] && nsconmsg -K var/nslog/newnslog -d current | awk '!/reltime|Index/{print $6}' | sort | uniq -c | egrep '([a-z].*[_]).*' > "conFetch/nsconmsg/nsconmsg_counters.txt" 2>&1 &)
  fixperms ./ >/dev/null 2>&1 &
else
  echo -e "\e[31m$directory unable to navigate to case directory\e[0m"
fi
