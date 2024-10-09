import configparser

settings = {
    "base": {
        "output_level": 1
    } ,
    "server": {
        "status_log": "/run/openvpn-server/status-server.log" ,
        "server_dir": "/etc/openvpn/server/" ,
        "server_cfg": "/etc/openvpn/server/server.conf" ,
        "mgmt_interface_server": "127.0.0.1" ,
        "mgmt_interface_port": 5555
    } ,
    "blocked_users": {
        "users": []
    }
}

def parse_settings( settings_path: str ):
    parser = configparser.ConfigParser()
    parser.read( settings_path )

    if parser.has_section( "base" ):
        if parser.has_option( "base" , "output_level" ) and len( parser["base"]["output_level"] ) != 0 and parser["base"]["output_level"].isdigit():
            settings["base"]["output_level"] = int( parser["base"]["output_level"] )
    
    if parser.has_section( "server" ):
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

    if parser.has_section( "blocked_users" ):
        if parser.has_option( "blocked_users" , "users" ) and len( parser["blocked_users"]["users"] ) != 0:
            users_str = parser["blocked_users"]["users"]
            settings["blocked_users"]["users"] = users_str.split( ',' )

if __name__ == "__main__":
    print( "This is a module, should not be executed" )
    exit( 1 )