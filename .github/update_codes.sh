#/bin/bash

cd $1
# enter install dir

if [ ! -d "openvpn-mgmt" ]; then
    git clone --recursive https://github.com/Ace-Radom/openvpn-mgmt.git
    cd openvpn-mgmt
else
    cd openvpn-mgmt
    git fetch --all
    git reset --hard origin/main
    git submodule update --recursive
fi

log_file="/var/openvpn-mgmt/log/openvpn-mgmt.0.log"
if [[ -f "$log_file" ]]; then
    main_commit=$(git log -1 --pretty=format:%h)
    log_msg_header=$(printf "%-49s" "$(date '+%Y-%m-%d %H:%M:%S.%6N %Z' | awk '{print $1, $2, $3}') [gh_codeupdater]")
    flock -x "$log_file" echo "$log_msgs_header openvpn-mgmt updated. [commit=$main_commit]" >> "$log_file"
fi

exit 0
