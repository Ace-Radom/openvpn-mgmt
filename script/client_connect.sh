#!/bin/bash

current_log_file="/var/openvpn-mgmt/log/openvpn-mgmt.0.log"
openvpn_mgmt_main_path="$OPENVPN_MGMT_MAIN_PATH"

cn=$common_name
real_ip="$trusted_ip:$trusted_port"
virtual_ip=$ifconfig_pool_remote_ip

log_msg_header=$(printf "%-49s" "$(date '+%Y-%m-%d %H:%M:%S.%6N %Z' | awk '{print $1, $2, $3}') [openvpn]")

is_blocked_response=$(python3 $openvpn_mgmt_main_path clients --is-blocked $cn)
read -r response <<< "$is_blocked_response"
read -r msg <<< "$(echo "$is_blocked_response" | sed -n '2p')"

if [[ "$response" == "yes" ]]; then
    flock -x "$current_log_file" echo "$log_msg_header Client connection denied. [cn='$cn', real_ip='$real_ip', virtual_ip='$virtual_ip', mgmt_msg='$msg']" >> "$current_log_file"
    exit 1
elif [[ "$response" == "error" ]]; then
    flock -x "$current_log_file" echo "$log_msg_header Error occured when asking client status, connection denied. [cn='$cn', real_ip='$real_ip', virtual_ip='$virtual_ip', mgmt_msg='$msg']" >> "$current_log_file"
    exit 1
elif [[ "$response" == "no" ]]; then
    flock -x "$current_log_file" echo "$log_msg_header Authed client connection accepted. [cn='$cn', real_ip='$real_ip', virtual_ip='$virtual_ip']" >> "$current_log_file"
    exit 0
else
    flock -x "$current_log_file" echo "$log_msg_header Unexpected mgmt response, connection denied. [cn='$cn', real_ip='$real_ip', virtual_ip='$virtual_ip', mgmt_response='$response', mgmt_msg='$msg']" >> "$current_log_file"
    exit 1
fi
