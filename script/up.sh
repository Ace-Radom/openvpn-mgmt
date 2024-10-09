#!/bin/bash

log_dir="/var/openvpn-mgmt/log"

if [[ ! -d "$log_dir" ]]; then
    mkdir -p "$log_dir"
    chmod 777 "$log_dir"
fi

log_file="$log_dir/openvpn-mgmt.0.log"

echo "=== Service Start $(date '+%Y-%m-%d %H:%M:%S.%N %Z' | cut -c1-26) ===" > "$log_file"

exit 0
