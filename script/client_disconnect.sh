#!/bin/bash

current_log_file="/var/openvpn-mgmt/log/openvpn-mgmt.0.log"

cn=$common_name
real_ip="$trusted_ip:$trusted_port"
virtual_ip=$ifconfig_pool_remote_ip

log_msg_header=$(printf "%-39s" "$(date '+%Y-%m-%d %H:%M:%S.%N %Z' | cut -c1-26) [openvpn]")

echo "$log_msg_header Client diconnected. [CN='$cn', REAL_IP='$real_ip', VIRTUAL_IP='$virtual_ip']" >> "$current_log_file"
