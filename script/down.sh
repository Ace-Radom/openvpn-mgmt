#!/bin/bash

log_dir="/var/openvpn-mgmt/log"
current_log_file="$log_dir/openvpn-mgmt.0.log"

echo "=== Service Stop $(date '+%Y-%m-%d %H:%M:%S.%N %Z' | cut -c1-26) ===" >> "$current_log_file"

max_log_index=$(ls "$log_dir" | grep -oP 'openvpn-mgmt\.\d+\.log' | grep -oP '\d+' | sort -n | tail -1)
if [[ -z "$max_log_index" ]]; then
    max_log_index=0
fi

for ((i=max_log_index; i>=0; i--)); do
    if [[ -f "$log_dir/openvpn-mgmt.$i.log" ]]; then
        next_log=$((i+1))
        mv "$log_dir/openvpn-mgmt.$i.log" "$log_dir/openvpn-mgmt.$next_log.log"
    fi
done

exit 0
