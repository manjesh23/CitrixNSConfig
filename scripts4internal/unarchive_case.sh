for i in $(cat extracted_Cases.txt); 
do 
    echo "archive = " $i
    coll=$(tar tvzf $i | egrep "/shell/ns_running_config.conf" | awk '{$1=$2=$3=$4=$5=$6=$7=$8=""; print}')
    echo "coll" = $coll
    if [ ! -z "${coll}" ]
    then
        tar xvzf $i $coll
    fi
done
