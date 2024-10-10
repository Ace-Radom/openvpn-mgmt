#!/bin/bash

log_dir="/var/openvpn-mgmt/log"
current_log_file="$log_dir/openvpn-mgmt.0.log"

flock -x "$current_log_file" echo "=== Service Stop $(date '+%Y-%m-%d %H:%M:%S.%6N %Z' | awk '{print $1, $2, $3}') ===" >> "$current_log_file"

max_log_index=$(ls "$log_dir" | grep -oP 'openvpn-mgmt\.\d+\.log' | grep -oP '\d+' | sort -n | tail -1)
if [[ -z "$max_log_index" ]]; then
    max_log_index=0
fi

for ((i=max_log_index; i>=0; i--)); do
    if [[ -f "$log_dir/openvpn-mgmt.$i.log" ]]; then
        this_log="$log_dir/openvpn-mgmt.$i.log"
        next_log="$log_dir/openvpn-mgmt.$((i+1)).log"
        flock -x "$this_log" mv "$this_log" "$next_log"
    fi
done

exit 0
