import csv
import datetime
import json
import os
import re

from mgmt import log
from mgmt import settings
from mgmt import utils

class clients:
    USER_ADMIN = 0
    USER_NORMAL = 1
    USER_BLOCKED = 2

    def __init__( self ):
        self._client_certs_list_file = os.path.join( settings.settings["server"]["server_dir"] , "easy-rsa/pki/index.txt" )
        self._client_ipp_file = os.path.join( settings.settings["server"]["server_dir"] , "ipp.txt" )
        self._client_data_file = "/var/openvpn-mgmt/clients.json"
        self._client_data = []
        self._loghost = "clients"
        
        if not os.path.isdir( "/var/openvpn-mgmt" ):
            os.makedirs( "/var/openvpn-mgmt" )

        if not os.path.isfile( self._client_data_file ):
            self.refresh_client_data()

        return
    
    def read_client_data( self ) -> list:
        if not os.path.isfile( self._client_data_file ):
            return []

        with open( self._client_data_file , 'r' , encoding = 'utf-8' ) as rFile:
            try:
                self._client_data = json.load( rFile )
            except:
                self._client_data = []
        return
    
    def write_client_data( self ):
        with open( self._client_data_file , 'w' , encoding = 'utf-8' ) as wFile:
            json.dump( self._client_data , wFile )
        return

    def refresh_client_data( self ) -> int:
        log.logger.write_log( self._loghost , "Refreshing clients data..." )

        if not os.path.isfile( self._client_certs_list_file ):
            raise Exception( f"Valid clients list file missing: \"{ self._client_certs_list_file }\"" )
        
        if not os.path.isfile( self._client_ipp_file ):
            raise Exception( f"Valid clients ipp file missing: \"{ self._client_ipp_file }\"" )

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

        self.read_client_data()
        new_client_data = []

        for client in detailed_valid_clients:
            if len( self._client_data ) != 0 and any( client["common_name"] == client_data["common_name"] for client_data in self._client_data ):
                client_data = list( filter( lambda it : it["common_name"] == client["common_name"] , self._client_data ) )
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

            new_client_data.append( this_client_data )

        self._client_data = new_client_data
        self.write_client_data()

        utils.lprint( 1 , "Clients data refreshed." )
        log.logger.write_log( self._loghost , f"Clients data refreshed. [client_count={ len( self._client_data ) }]" )
        log.logger.write_log( self._loghost , f"New client data: { json.dumps( new_client_data ) }" )
        return 0
    
    def refresh_client_block_to( self ) -> int:
        self.read_client_data()

        for i in range( 0 , len( self._client_data ) ):
            user_group = self._client_data[i]["user_group"]
            if user_group == self.USER_ADMIN or user_group == self.USER_BLOCKED:
                continue
            # no need to update admin users' & blocked users' block_to ts
            elif user_group == self.USER_NORMAL:
                block_to = self._client_data[i]["block_to"]
                if block_to == -1 or block_to == 0:
                    continue
                # this normal user is not blocked or indefinitely blocked
                else:
                    ts_now = datetime.datetime.fromtimestamp( datetime.datetime.now() )
                    if block_to < ts_now:
                        log.logger.write_log( self._loghost , f"Client is no longer blocked. [cn=\"{ self._client_data[i]['common_name'] }\", block_to={ block_to }]" )
                        self._client_data[i]["block_to"] = -1

        self.write_client_data()
        return 0

    def list_client( self ) -> int:
        self.read_client_data()

        if len( self._client_data ) == 0:
            utils.lprint( 2 , "Clients data empty, run \"clients --refresh\" first to refresh cached clients data." )
            return 1
        
        clients_list = []
        clients_list.append( [
            "Common Name" ,
            "Virtual IP" ,
            "User Group"
        ] )

        for client in self._client_data:
            clients_list.append( [ client["common_name"] , client["virtual_ip"] , { 0: "Admin" , 1: "Normal User" , -1: "Blocked User" }.get( client["user_group"] , "Unknown" ) ] )

        utils.lprint( 1 , f"Current clients count: { len( self._client_data ) }" )

        col_widths = [max( len( str( item ) ) for item in col ) for col in zip( *clients_list )]
        for row in clients_list:
            utils.lprint( 1 , " | ".join( f"{ item.ljust( col_widths[i] ) }" for i , item in enumerate( row ) ) )

        return 0
    
    def block_client( self , common_name: str , block_time_length_str: str ) -> int:
        self.read_client_data()

        pattern = r"(?:(\d+)mo)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
        match = re.fullmatch( pattern , block_time_length_str )
        if not match:
            utils.lprint( 2 , "Invalid block time input." )
            return 1
        
        months = int( match.group( 1 ) or 0 )
        days = int( match.group( 2 ) or 0 )
        hours = int( match.group( 3 ) or 0 )
        minutes = int( match.group( 4 ) or 0 )
        seconds = int( match.group( 5 ) or 0 )
        block_to = datetime.datetime.now()
        if months:
            for _ in range( 0 , months ):
                month = block_to.month + 1
                year = block_to.year
                if month > 12:
                    month = 1
                    year += 1
                block_to = block_to.replace( year = year , month = month )
        block_to += datetime.timedelta(
            days = days ,
            hours = hours ,
            minutes = minutes ,
            seconds = seconds
        )

        for client in self._client_data:
            if client["common_name"] == common_name:
                block_to_ts = int( datetime.datetime.timestamp( block_to ) )
                client["block_to"] = block_to_ts
                self.write_client_data()
                utils.lprint( 1 , f"Client \"{ common_name }\" has been blocked to { block_to.strftime( '%Y-%m-%d %H:%M:%S' ) } { datetime.datetime.now().astimezone().tzname() }." )
                log.logger.write_log( self._loghost , f"Client blocked. [cn=\"{ common_name }\", block_to={ block_to_ts }]" )
                return 0
            
        utils.lprint( 2 , f"Client \"{ common_name }\" not found in cached client data. You may try refreshing cached client data first." )
        return 1

    def is_client_blocked( self , common_name: str ) -> int:
        # this function uses print, not utils.lprint, since it would be called by OpenVPN scripts
        self.refresh_client_block_to()
        # here: refresh_client_block_to already updated self._client_data, no need to read from file again
        client_data = list( filter( lambda it : it["common_name"] == common_name , self._client_data ) )
        if len( client_data ) == 0:
            print( "error" )
            print( f"Client \"{ common_name }\" not found in cached client data." )
            return 1
        
        if client_data[0]["user_group"] == self.USER_ADMIN:
            print( "no" )
            print( f"Client \"{ common_name }\" is in admin user group." )
            return 0
        elif client_data[0]["user_group"] == self.USER_BLOCKED:
            print( "yes" )
            print( f"Client \"{ common_name }\" is in blocked user group." )
            return 0
        elif client_data[0]["user_group"] == self.USER_NORMAL:
            block_to = client_data[0]["block_to"]
            if block_to == -1:
                print( "no" )
                print( f"Client \"{ common_name }\" is not blocked." )
            elif block_to == 0:
                print( "yes" )
                print( f"Client \"{ common_name }\" is indefinitely blocked." )
            else:
                ts_now = datetime.datetime.timestamp( datetime.datetime.now() )
                if ts_now < block_to:
                    print( "yes" )
                    print( f"Client \"{ common_name }\" is blocked to { datetime.datetime.fromtimestamp( block_to ).strftime( '%Y-%m-%d %H:%M:%S' ) } { datetime.datetime.now().astimezone().tzname() }." )
                else:
                    print( "no" )
                    print( f"Client \"{ common_name }\" is no longer blocked." )
            return 0
        else:
            print( "error" )
            print( "Unrecognized user group." )
            return 1
