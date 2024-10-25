#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import utils

from mgmt import log

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
        self._loghost = "connection"

        if not os.path.isdir( "/var/openvpn-mgmt" ):
            os.makedirs( "/var/openvpn-mgmt" )

        if not os.path.isfile( self._data_file ):
            self.write_data()

        return
    
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
