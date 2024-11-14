#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import json
import os

from mgmt import log
from mgmt import ovpn_mgmt_interface
from mgmt import ovpn_status
from mgmt import settings
from mgmt import utils

class connection:
    CONNECTION_MODE_NORMAL = 0
    CONNECTION_MODE_MAINTAIN = 1
    CONNECTION_MODE_BLOCK = 2
    CONNECTION_DATA_DEFAULT = {
        "mode": CONNECTION_MODE_NORMAL
    }


    def __init__( self ):
        self._data_file = "/var/openvpn-mgmt/connection.json"
        self._data = connection.CONNECTION_DATA_DEFAULT
        self._ovpn_status = ovpn_status.ovpn_status()
        self._loghost = "connection"

        if not os.path.isdir( "/var/openvpn-mgmt" ):
            os.makedirs( "/var/openvpn-mgmt" )

        if not os.path.isfile( self._data_file ):
            self.write_data()

        return
    
    def _parse_ovpn_status( self ) -> int:
        ret = 0
        status_log = ""
        if settings.settings["base"]["use_mgmt_interface_as_default"]:
            mgmt_interface = ovpn_mgmt_interface.ovpn_mgmt_interface()
            ret = mgmt_interface.connect()
            if ret == 0:
                ret , status_log = mgmt_interface.exec( "status" )
                if ret != 0:
                    log.logger.write_log( self._loghost , "Get service status log from OpenVPN management interface failed, use status log file instead." )
                mgmt_interface.close()
            else:
                log.logger.write_log( self._loghost , "Connect to OpenVPN management interface failed, use status log file instead." )

        if ret != 0 or status_log == "":
            with open( settings.settings["server"]["status_log"] , 'r' , encoding = 'utf-8' ) as rFile:
                status_log = rFile.read()

        return self._ovpn_status.parse_status_log( status_log )
    
    def read_data( self ):
        if not os.path.isfile( self._data_file ):
            return
        
        with open( self._data_file , 'r' , encoding = 'utf-8' ) as rFile:
            try:
                self._data = json.load( rFile )
            except:
                self._data = connection.CONNECTION_DATA_DEFAULT
        return
    
    def write_data( self ):
        with open( self._data_file , 'w' , encoding = 'utf-8' ) as wFile:
            json.dump( self._data , wFile )
        return
        
    def get_mode( self ) -> int:
        self.read_data()
        return self._data["mode"]
    
    def set_mode( self , mode: int ) -> int:
        if mode not in [ connection.CONNECTION_MODE_NORMAL , connection.CONNECTION_MODE_MAINTAIN , connection.CONNECTION_MODE_BLOCK ]:
            utils.lprint( 2 , f"Illegal connection mode: { mode }" )
            return 1

        self.read_data()
        self._data["mode"] = mode
        self.write_data()
        log.logger.write_log( self._loghost , f"Connection mode changed. [new_mode={ mode }]" )
        return 0
    
    def list_connection_datas( self ) -> int:
        self._parse_ovpn_status()

        last_log_refresh_time_str = self._ovpn_status.last_log_refresh_datetime.strftime( "%Y-%m-%d %H:%M:%S" )
        last_log_refresh_time_delta_str = f"{ ( datetime.datetime.now() - self._ovpn_status.last_log_refresh_datetime ).total_seconds() :.0f}"

        utils.lprint( 1 , f"Last log refresh: { last_log_refresh_time_str } { utils.get_tzname() } ({ last_log_refresh_time_delta_str } seconds ago)" )
        utils.lprint( 1 , f"Current connected clients count: { self._ovpn_status.connection_count }" )

        detailed_connection_data_list = []
        detailed_connection_data_list.append( [
            "Common Name" ,
            "Real IP" ,
            "Virtual IP" ,
            "Uplink Traffic (B)" ,
            "Downlink Traffic (B)" ,
            "Connected Since" ,
            "Username" ,
            "Client ID" ,
            "Data Channal Cipher"
        ] )

        for data in self._ovpn_status.detailed_connection_data:
            connected_since_time_str = datetime.datetime.fromtimestamp( data["connected_since"] ).strftime( "%Y-%m-%d %H:%M:%S" )
            detailed_connection_data_list.append( [
                data["common_name"] ,
                data["real_addr"] ,
                data["virtual_addr"] ,
                f"{ utils.conv_bytes_to_formel_str( data['uplink'] ) } ({ data['uplink'] })" ,
                f"{ utils.conv_bytes_to_formel_str( data['downlink'] ) } ({ data['downlink'] })" ,
                f"{ connected_since_time_str } { utils.get_tzname() }" ,
                data["username"] ,
                data["client_id"] ,
                data["data_channal_cipher"]
            ] )

        col_widths = [max( len( str( item ) ) for item in col ) for col in zip( *detailed_connection_data_list )]
        for row in detailed_connection_data_list:
            utils.lprint( 1 , " | ".join( f"{ item.ljust( col_widths[i] ) }" for i , item in enumerate( row ) ) )

        return 0
    
    def kill_connection( self , common_name: str ) -> int:
        if settings.settings["server"]["mgmt_interface_server"] is None or settings.settings["server"]["mgmt_interface_port"] is None:
            utils.lprint( 2 , f"Cannot kill client connection without OpenVPN management interface setup" )
            return 1
        
        self._parse_ovpn_status()
        if not self._ovpn_status.is_connected( common_name ):
            utils.lprint( 2 , f"Client \"{ common_name }\" isn't connected, cannot kill connection" )
            return 1
        
        ret = 0
        response = ""
        mgmt_interface = ovpn_mgmt_interface.ovpn_mgmt_interface()
        ret = mgmt_interface.connect()
        if ret == 0:
            ret , response = mgmt_interface.exec( f"kill { common_name }" , end_sign = "SUCCESS" )
            if ret == 0:
                log.logger.write_log( self._loghost , f"Client connection killed. [cn='{ common_name }', response='{ response }']" )
            else:
                log.logger.write_log( self._loghost , f"Kill client connection failed. [cn='{ common_name }', response='{ response }']" )
            mgmt_interface.close()
        else:
            log.logger.write_log( self._loghost , f"Connect to OpenVPN management interface failed, cannot kill client connection. [cn='{ common_name }']" )

        return ret
        # if success, ret should be 0; otherwise it should not be 0

if __name__ == "__main__":
    print( "This is a module, should not be executed" )
    exit( 1 )
