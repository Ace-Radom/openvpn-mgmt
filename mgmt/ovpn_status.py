#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import datetime
import io

from mgmt import settings

class ovpn_status:
    def __init__( self ):
        self.version = ""
        self.last_log_refresh_datetime = datetime.datetime.min
        self.connection_count = 0
        self.detailed_connection_data = []
        if settings.settings["server"]["is_ipv6_enabled"]:
            self.col_offset = 1
        else:
            self.col_offset = 0

    def parse_status_log( self , log: str ) -> int:
        log_rows = []
        for row in csv.reader( io.StringIO( log ) ):
            log_rows.append( row )

        self.version = log_rows[0][1]
        self.last_log_refresh_datetime = datetime.datetime.fromtimestamp( int( log_rows[1][2] ) )

        log_rows.pop( 0 )
        log_rows.pop( 0 )
        log_rows.pop( -1 )
        log_rows.pop( -1 )
        # pop datas: server version; last refresh time; global stats; END sign

        self.connection_count = ( len( log_rows ) - 2 ) // 2
        self.detailed_connection_data = []

        for i in range( 1 , self.connection_count + 1 ):
            self.detailed_connection_data.append( {
                "common_name": log_rows[i][1] ,
                "real_addr": log_rows[i][2] ,
                "virtual_addr": log_rows[i][3] ,
                "uplink": int( log_rows[i][5+self.col_offset] ) ,
                "downlink": int( log_rows[i][6+self.col_offset] ) ,
                "connected_since": int( log_rows[i][8+self.col_offset] ) ,
                "username": log_rows[i][9+self.col_offset] ,
                "client_id": log_rows[i][10+self.col_offset] ,
                "data_channal_cipher": log_rows[i][12+self.col_offset]
            } )

        return 0

    def is_connected( self , common_name: str ) -> bool:
        for client in self.detailed_connection_data:
            if client["common_name"] == common_name:
                return True
        return False

if __name__ == "__main__":
    print( "This is a module, should not be executed" )
    exit( 1 )
