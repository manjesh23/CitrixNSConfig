for i in {36..62}; do
    ip="10.110.123.$i"
    if ping -c 1 -W 1 $ip >/dev/null; then
        echo -e "\e[32m$ip is up\e[0m"
    else
        echo -e "\e[31m$ip is down\e[0m"
    fi
done
