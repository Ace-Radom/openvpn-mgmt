#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser

settings = {
    "base": {
        "output_level": 1 ,
        "use_mgmt_interface_as_default": False
    } ,
    "server": {
        "service_name": "openvpn-server@server.service" ,
        "status_log": "/run/openvpn-server/status-server.log" ,
        "server_dir": "/etc/openvpn/server/" ,
        "server_cfg": "/etc/openvpn/server/server.conf" ,
        "mgmt_interface_server": None ,
        "mgmt_interface_port": None ,
        "mgmt_interface_pswd": None
    } ,
    "clients": {
        "admins": [] ,
        "blocked_users": []
    }
}

def parse_settings( settings_path: str ):
    parser = configparser.ConfigParser()
    parser.read( settings_path )

    if parser.has_section( "base" ):
        if parser.has_option( "base" , "output_level" ) and len( parser["base"]["output_level"] ) != 0 and parser["base"]["output_level"].isdigit():
            settings["base"]["output_level"] = int( parser["base"]["output_level"] )
        if parser.has_option( "base" , "use_mgmt_interface_as_default" ) and len( parser["base"]["use_mgmt_interface_as_default"] ) != 0 and parser["base"]["use_mgmt_interface_as_default"].isdigit():
            settings["base"]["use_mgmt_interface_as_default"] = ( int( parser["base"]["use_mgmt_interface_as_default"] ) != 0 )
    
    if parser.has_section( "server" ):
        if parser.has_option( "server" , "service_name" ) and len( parser["server"]["service_name"] ) != 0:
            settings["server"]["service_name"] = parser["server"]["service_name"]
        if parser.has_option( "server" , "status_log" ) and len( parser["server"]["status_log"] ) != 0:
            settings["server"]["status_log"] = parser["server"]["status_log"]
        if parser.has_option( "server" , "server_dir" ) and len( parser["server"]["server_dir"] ) != 0:
            settings["server"]["server_dir"] = parser["server"]["server_dir"]
        if parser.has_option( "server" , "server_cfg" ) and len( parser["server"]["server_cfg"] ) != 0:
            settings["server"]["server_cfg"] = parser["server"]["server_cfg"]
        if parser.has_option( "server" , "mgmt_interface_server" ) and len( parser["server"]["mgmt_interface_server"] ) != 0:
            settings["server"]["mgmt_interface_server"] = parser["server"]["mgmt_interface_server"]
        if parser.has_option( "server" , "mgmt_interface_port" ) and len( parser["server"]["mgmt_interface_port"] ) != 0 and parser["server"]["mgmt_interface_port"].isdigit():
            settings["server"]["mgmt_interface_port"] = int( parser["server"]["mgmt_interface_port"] )
        if parser.has_option( "server" , "mgmt_interface_pswd" ) and len( parser["server"]["mgmt_interface_pswd"] ) != 0:
            settings["server"]["mgmt_interface_pswd"] = parser["server"]["mgmt_interface_pswd"]

    if parser.has_section( "clients" ):
        if parser.has_option( "clients" , "admins" ) and len( parser["clients"]["admins"] ) != 0:
            admins_str = parser["clients"]["admins"]
            settings["clients"]["admins"] = admins_str.split( ',' )
            for admin in settings["clients"]["admins"]:
                admin.strip()
        if parser.has_option( "clients" , "blocked_users" ) and len( parser["clients"]["blocked_users"] ) != 0:
            blocked_users_str = parser["clients"]["blocked_users"]
            settings["clients"]["blocked_users"] = blocked_users_str.split( ',' )
            for blocked_user in settings["clients"]["blocked_users"]:
                blocked_user.strip()

if __name__ == "__main__":
    print( "This is a module, should not be executed" )
    exit( 1 )
