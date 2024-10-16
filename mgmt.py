#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import os
import subprocess
import sys

from mgmt import clients
from mgmt import log
from mgmt import ovpn_script
from mgmt import settings
from mgmt import utils

localtz_name = datetime.datetime.now().astimezone().tzname()
base_dir = os.path.split( os.path.realpath( __file__ ) )[0]
server_uptime = ""
parser = argparse.ArgumentParser()

def setup_args():
    features_arg_group = parser.add_mutually_exclusive_group()
    features_arg_group.add_argument( "--refresh-cfg-cache" , default = False , action = "store_true" , help = "Refresh OpenVPN service config & openvpn-mgmt config cache" )
    features_arg_group.add_argument( "--install-ovpn-script" , nargs = '?' , metavar = "SCRIPT_NAME" , const = "all" , type = str , help = "Install OpenVPN scripts to server directory" )
    
    clients_parser = parser.add_subparsers( dest = "clients" ).add_parser( "clients" , help = "Manage OpenVPN clients" )
    clients_arg_group = clients_parser.add_mutually_exclusive_group()
    clients_arg_group.add_argument( "--list" , default = False , action = "store_true" , help = "List all valid clients" )
    clients_arg_group.add_argument( "--status" , default = False , action = "store_true" , help = "Show all valid clients' detailed status" )
    clients_arg_group.add_argument( "--refresh" , default = False , action = "store_true" , help = "Refresh valid clients cached datas" )
    clients_arg_group.add_argument( "--block" , nargs = 2 , metavar = tuple( [ "COMMON_NAME" , "BLOCK_TO" ] ) , type = str , help = "Block a specific client" )
    clients_arg_group.add_argument( "--is-blocked" , metavar = "COMMON_NAME" , type = str , help = "Check is a specific client being blocked" )

def is_openvpn_server_running() -> bool:
    try:
        result = subprocess.run(
            [ "systemctl" , "status" , settings.settings["server"]["service_name"] ] ,
            stdout = subprocess.PIPE ,
            stderr = subprocess.PIPE ,
            text = True
        )

        if "active (running)" not in result.stdout:
            utils.lprint( 2 , "OpenVPN server is not running" )
            return False
        # service stopped

        for line in result.stdout.splitlines():
            if "Active:" in line:
                global server_uptime
                uptime_line = line.split( ';' )[0]
                server_uptime = uptime_line.split( "since" )[-1][4:].strip()
                return True

    except Exception as e:
        utils.lprint( 2 , f"Error when checking service: { e }" )
        return False

    return False

def main():
    log.init_global_logger( localtz_name )
    settings.parse_settings( os.path.join( base_dir , "mgmt.cfg" ) )
        
    if len( sys.argv ) > 1:
        setup_args()
        args = parser.parse_args()

        if args.install_ovpn_script:
            script_mgmt = ovpn_script.ovpn_script( base_dir )
            exit( script_mgmt.install( args.install_ovpn_script ) )

        if args.clients:
            clients_mgmt = clients.clients()
            if args.refresh:
                exit( clients_mgmt.refresh_client_data() )
            elif args.list:
                exit( clients_mgmt.list_client() )
            elif args.block:
                exit( clients_mgmt.block_client( args.block[0] , args.block[1] ) )
            elif args.is_blocked:
                exit( clients_mgmt.is_client_blocked( args.is_blocked ) )

    if not is_openvpn_server_running():
        exit( 1 )
    # check service status

    with open( "/run/openvpn-server/status-server.log" , 'r' , encoding = 'utf-8' ) as rFile:
        log_rows = []
        for row in csv.reader( rFile ):
            log_rows.append( row )

    utils.lprint( 1 , log_rows[0][1] )
    # server version

    datetime_now = datetime.datetime.now()
    time_now_str = datetime_now.strftime( "%Y-%m-%d %H:%M:%S" )
    utils.lprint( 1 , f"Time now: { time_now_str } { localtz_name }" )
    # time now

    utils.lprint( 1 , f"Service active since: { server_uptime }" )
    # active since

    last_log_refresh_time = datetime.datetime.fromtimestamp( int( log_rows[1][2] ) )
    last_log_refresh_time_str = last_log_refresh_time.strftime( "%Y-%m-%d %H:%M:%S" )
    last_log_refresh_time_delta_str = f"{ ( datetime_now - last_log_refresh_time ).total_seconds() :.0f}"
    utils.lprint( 1 , f"Last log refresh: { last_log_refresh_time_str } { localtz_name } ({ last_log_refresh_time_delta_str } seconds ago)" )
    # last log refresh time

    log_rows.pop( 0 )
    log_rows.pop( 0 )
    log_rows.pop( -1 )
    log_rows.pop( -1 )
    # pop datas: server version; last refresh time; global stats; END sign

    utils.lprint( 1 )

    current_connection_count = ( len( log_rows ) - 2 ) // 2
    utils.lprint( 1 , f"Connected profiles count: { current_connection_count }" )
    # connection count

    connected_profiles = []
    detailed_connections_data = []
    detailed_connections_data.append( [
        "Common Name" ,
        "Real IP Addr." ,
        "Virtual IP Addr." ,
        "Uplink Traffic (B)" ,
        "Downlink Traffic (B)" ,
        "Connected Since" ,
        "Username" ,
        "Client ID" ,
        "Data Channal Cipher"
    ] )
    for i in range( 1 , current_connection_count + 1 ):
        connected_since_time_str = datetime.datetime.fromtimestamp( int( log_rows[i][8] ) ).strftime( "%Y-%m-%d %H:%M:%S" )
        connected_profiles.append( log_rows[i][1] )
        detailed_connections_data.append( [
            log_rows[i][1] ,  # common name
            log_rows[i][2] ,  # real ip addr
            log_rows[i][3] ,  # virtual ip addr
            f"{ utils.conv_bytes_to_formel_str( int( log_rows[i][5] ) ) } ({ log_rows[i][5] })" ,  # uplink traffic
            f"{ utils.conv_bytes_to_formel_str( int( log_rows[i][6] ) ) } ({ log_rows[i][6] })" ,  # downlink traffic
            f"{ connected_since_time_str } { localtz_name }" ,  # connected since
            log_rows[i][9] ,  # username
            log_rows[i][10] ,  # client id
            log_rows[i][12]  # data channal cipher
        ] )

    col_widths = [max( len( str( item ) ) for item in col ) for col in zip( *detailed_connections_data )]
    for row in detailed_connections_data:
        utils.lprint( 1 , " | ".join( f"{ item.ljust( col_widths[i] ) }" for i , item in enumerate( row ) ) )
    # connected profiles

    utils.lprint( 1 )

    with open( "/etc/openvpn/server/easy-rsa/pki/index.txt" , 'r' , encoding = "utf-8" ) as rFile:
        cert_index_lines = rFile.readlines()[1:]

    valid_certs = []
    for line in cert_index_lines:
        if line.startswith( 'R' ):
            continue
        parts = line.split( '=' )
        if len( parts ) > 1:
            valid_certs.append( parts[1].strip() )
    valid_certs.sort()

    utils.lprint( 1 , f"Valid certifications count: { len( valid_certs ) }" )
    # certs count

    detailed_certs_data = []
    detailed_certs_data.append( [
        "Common Name" ,
        "Status"
    ] )
    for cert in valid_certs:
        detailed_certs_data.append( [
            cert ,
            "Connected" if cert in connected_profiles else "Disconnected"
        ] )

    col_widths = [max( len( str( item ) ) for item in col ) for col in zip( *detailed_certs_data )]
    for row in detailed_certs_data:
        utils.lprint( 1 , " | ".join( f"{ item.ljust( col_widths[i] ) }" for i , item in enumerate( row ) ) )

if __name__ == "__main__":
    main()
