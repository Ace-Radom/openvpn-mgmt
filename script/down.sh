#!/bin/bash

script_dir=$(dirname $(readlink -f "$0"))
server_cfg_dir=$(dirname "$script_dir")
log_dir="$server_cfg_dir/log"
current_log_file="$log_dir/openvpn.0.log"

echo "=== Service Stop $(date '+%Y-%m-%d %H:%M:%S %Z') ===" >> "$current_log_file"

max_log_index=$(ls "$log_dir" | grep -oP 'openvpn\.\d+\.log' | grep -oP '\d+' | sort -n | tail -1)
if [[ -z "$max_log_index" ]]; then
    max_log_index=0
fi

for ((i=max_log_index; i>=0; i--)); do
    if [[ -f "$log_dir/openvpn.$i.log" ]]; then
        next_log=$((i+1))
        mv "$log_dir/openvpn.$i.log" "$log_dir/openvpn.$next_log.log"
    fi
done

exit 0
