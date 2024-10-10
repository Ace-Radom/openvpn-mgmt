#!/bin/bash

current_log_file="/var/openvpn-mgmt/log/openvpn-mgmt.0.log"

cn=$common_name
real_ip="$trusted_ip:$trusted_port"
virtual_ip=$ifconfig_pool_remote_ip
uplink_traffic=$bytes_received
downlink_traffic=$bytes_sent

log_msg_header=$(printf "%-49s" "$(date '+%Y-%m-%d %H:%M:%S.%6N %Z' | awk '{print $1, $2, $3}') [openvpn]")

flock -x "$current_log_file" echo "$log_msg_header Client diconnected. [cn='$cn', real_ip='$real_ip', virtual_ip='$virtual_ip', uplink=$uplink_traffic, downlink=$downlink_traffic]" >> "$current_log_file"

exit 0
