#!/bin/bash

log_dir="/var/openvpn-mgmt/log"

if [[ ! -d "$log_dir" ]]; then
    mkdir -p "$log_dir"
    chmod 777 "$log_dir"
fi

log_file="$log_dir/openvpn-mgmt.0.log"

touch "$log_file"
chmod 666 "$log_file"
flock -x "$log_file" echo "=== Service Start $(date '+%Y-%m-%d %H:%M:%S.%6N %Z' | awk '{print $1, $2, $3}') ===" > "$log_file"

exit 0
