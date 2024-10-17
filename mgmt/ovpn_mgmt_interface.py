import socket

from mgmt import log
from mgmt import settings

ovpn_mgmt_interface_connected = False

class ovpn_mgmt_interface:
    def __init__( self ):
        if settings.settings["server"]["mgmt_interface_server"] is None or settings.settings["server"]["mgmt_interface_port"] is None:
            raise Exception( "OpenVPN management interface address or port is empty in settings" )

        self._loghost = "ovpnmgmtitf"
        self._sock = None
        self._host = settings.settings["server"]["mgmt_interface_server"]
        self._port = settings.settings["server"]["mgmt_interface_port"]

    def connect( self ) -> int:
        try:
            if ovpn_mgmt_interface_connected:
                raise Exception( "OpenVPN management interface connection conflict" )

            self._sock = socket.socket( socket.AF_INET , socket.SOCK_STREAM )
            self._sock.connect( self._host , self._port )
            response = self._sock.recv( 1024 ).decode( 'utf-8' )
            if "ENTER PASSWORD" in response:
                if settings.settings["server"]["mgmt_interface_pswd"] is None:
                    raise Exception( "Connecting to OpenVPN management interface with password protected but password is not provided in settings" )
                
                self._sock.sendall( settings.settings["server"]["mgmt_interface_pswd"].encode( 'utf-8' ) )
                response = self._sock.recv( 1024 ).decode( 'utf-8' )
                if "SUCCESS" not in response:
                    raise Exception( "Authentication failed" )

            else:
                if ">INFO:OpenVPN Management Interface" not in response:
                    raise Exception( "Connection failed" )
                
            log.logger.write_log( self._loghost , "Connected to OpenVPN management interface" )
            ovpn_mgmt_interface_connected = True
            return 0
        
        except Exception as e:
            log.logger.write_log( self._loghost , f"Failed to connect to OpenVPN management interface. [error='{ e }']" )
            self._sock = None
            return 1
        
    def exec( self , cmd: str ) -> tuple[int,str]:
        try:
            if self._sock is None or not ovpn_mgmt_interface_connected:
                raise Exception( "OpenVPN management interface not connected" )
            
            log.logger.write_log( self._loghost , f"Executing command. [cmd='{ cmd }']")
            self._sock.sendall( cmd.encode( 'utf-8' ) )
            response = b""
            while True:
                data = self._sock.recv( 1024 )
                if not data:
                    break
                response += data

            response_str = response.decode( 'utf-8' )
            log.logger.write_log( self._loghost , f"Execute command succeeded. [response='{ response_str }']" )
            return ( 0 , response.decode( 'utf-8' ) )
        
        except Exception as e:
            log.logger.write_log( self._loghost , f"Failed to execute command. [cmd='{ cmd }', error='{ e }']" )
            return ( 1 , "" )
        
    def close( self ) -> int:
        try:
            if self._sock is None or not ovpn_mgmt_interface_connected:
                raise Exception( "OpenVPN management interface not connected" )
            
            self._sock.sendall( b"exit" )
            self._sock.close()
            self._sock = None
            ovpn_mgmt_interface_connected = False
            log.logger.write_log( self._loghost , "OpenVPN management interface disconnected." )
            return 0
        
        except Exception as e:
            log.logger.write_log( self._loghost , f"Failed to disconnect OpenVPN management interface. [error='{ e }']" )
            return 1
