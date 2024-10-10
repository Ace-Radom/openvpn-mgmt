import csv
import json
import os

from mgmt import log
from mgmt import settings

class clients:
    USER_ADMIN = 0
    USER_NORMAL = 1
    USER_BLOCKED = 2

    def __init__( self ):
        self._client_certs_list_file = os.path.join( settings.settings["server"]["server_dir"] , "easy-rsa/pki/index.txt" )
        self._client_ipp_file = os.path.join( settings.settings["server"]["server_dir"] , "ipp.txt" )
        self._client_data_file = "/var/openvpn-mgmt/clients.json"
        self._loghost = "clients"
        if not os.path.isfile( self._client_certs_list_file ):
            raise Exception( f"Valid clients list file missing: \"{ self._client_ipp_file }\"" )
        if not os.path.isfile( self._client_ipp_file ):
            raise Exception( f"Valid clients ipp file missing: \"{ self._client_ipp_file }\"" )
        
        if not os.path.isfile( self._client_data_file ):
            self.refresh_clients_data()

        if not os.path.isdir( "/var/openvpn-mgmt" ):
            os.makedirs( "/var/openvpn-mgmt" )

        return
    
    def refresh_clients_data( self ):
        log.logger.write_log( self._loghost , "Refreshing clients data..." )

        with open( self._client_certs_list_file , 'r' , encoding = 'utf-8' ) as rFile:
            cert_index_lines = rFile.readlines()[1:]

        valid_clients = []
        detailed_valid_clients = []
        for line in cert_index_lines:
            if line.startswith( 'R' ):
                continue
            valid_clients.append( line.split( '=' )[1].strip() )
        valid_clients.sort()
        # parse client certs list file

        with open( self._client_ipp_file , 'r' , encoding = 'utf-8' ) as rFile:
            ipps = []
            for row in csv.reader( rFile ):
                ipps.append( row )
            ipps.sort()
        # parse client ipp file

        for ipp in ipps:
            common_name = ipp[0].strip()
            virtual_ip = ipp[1].strip()
            if common_name in valid_clients:
                detailed_valid_clients.append( {
                    "common_name": common_name ,
                    "virtual_ip": virtual_ip
                } )

        client_datas = []
        new_client_datas = []
        if os.path.isfile( self._client_data_file ):
            with open( self._client_data_file , 'r' , encoding = 'utf-8' ) as rFile:
                client_datas = json.load( rFile )

        for client in detailed_valid_clients:
            if len( client_datas ) != 0 and any( client["common_name"] == client_data["common_name"] for client_data in client_datas ):
                client_data = list( filter( lambda it : it["common_name"] == client["common_name"] , client_datas ) )
                this_client_data = {
                    "common_name": client["common_name"] ,
                    "virtual_ip": client["virtual_ip"] ,
                    "user_group": client_data[0]["user_group"] ,
                    "block_to": client_data[0]["block_to"]
                }
            else:
                this_client_data = {
                    "common_name": client["common_name"] ,
                    "virtual_ip": client["virtual_ip"] ,
                    "user_group": self.USER_NORMAL ,
                    "block_to": -1
                }

            if this_client_data["common_name"] in settings.settings["clients"]["admins"]:
                this_client_data["user_group"] = self.USER_ADMIN
                this_client_data["block_to"] = -1
            elif this_client_data["common_name"] in settings.settings["clients"]["blocked_users"]:
                this_client_data["user_group"] = self.USER_BLOCKED
                this_client_data["block_to"] = -1

            new_client_datas.append( this_client_data )

        with open( self._client_data_file , 'w' , encoding = 'utf-8' ) as wFile:
            json.dump( new_client_datas , wFile )

        log.logger.write_log( self._loghost , f"Clients data refreshed. [client_count={ len( new_client_datas ) }, old_cliend_count={ len( client_datas ) }]" )
        return
