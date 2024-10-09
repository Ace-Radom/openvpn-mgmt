#!/bin/bash

script_dir=$(dirname $(readlink -f "$0"))
server_cfg_dir=$(dirname "$script_dir")
log_dir="$server_cfg_dir/log"

mkdir -p "$log_dir"

log_file="$log_dir/openvpn.0.log"

echo "=== Service Start $(date '+%Y-%m-%d %H:%M:%S %Z') ===" > "$log_file"

exit 0
