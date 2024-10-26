# Datad alias
alias datad="source /home/CITRITE/manjeshn/manscript/datad.sh"
alias datadd="source /home/CITRITE/manjeshn/manscript/datadd.sh"

# conFetch alias
alias show="python /home/CITRITE/manjeshn/manscript/show.py"
alias showd="python /home/CITRITE/manjeshn/manscript/showd.py"
alias conFetch="python /home/CITRITE/manjeshn/manscript/conFetch_Wrapper.py"

# bigCap alias
alias bigcap="python /home/CITRITE/manjeshn/manscript/bigcap.py"

# disposableToys
alias dt="python /home/CITRITE/manjeshn/manscript/disposableToys/Project_dT/dt.py"

# My style of tshoot
alias ll="ls -lah"
alias ld="ls -laht"

# allnewnslog alias
#alias allnewnslog='function _allnewnslog() { for i in $(ls -lah | awk "/newnslog/{print \$NF}"); do echo -e "\033[1;33m------------------------ $i ------------------------\033[0m"; nsconmsg -K "$i" -d "$1" -s disptime=1; done; }; _allnewnslog'
alias allnewnslog='function _allnewnslog() { base_dir="$(pwd | sed '\''s|\(.*collector[^/]*\)/.*|\1|'\'')"; find "$base_dir/var/nslog/" -maxdepth 1 -type d -name "newnslog*" -print0 | while IFS= read -r -d "" i; do echo -e "\033[1;33m------------------------ $i ------------------------\033[0m"; nsconmsg -K "$i" -d "$1" -s disptime=1; done; }; _allnewnslog'

alias ..="cd .."
alias ...="cd ../../"
alias ....="cd ../../../"
alias .....="cd ../../.././"
alias .1="cd .."
alias .2="cd ../../"
alias .3="cd ../../../"
alias .4="cd ../../../../"

alias h='history'
alias gh="history | grep "
alias c="clear"

alias zzgrep='grep -i --color=always'
alias zzless='less -R'
alias countcol="awk -F, '{for(i=1;i<=NF;i++) { print i, \$i } exit}'"
