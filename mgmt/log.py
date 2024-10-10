import datetime
import fcntl
import os

from mgmt import utils

class log:
    def __init__( self , tz: str ):
        self._tz = tz

    def write_log( self , host: str , msg: str ):
        log_msg = f"{ self.get_header( host ) } { msg }"
        current_log_file = "/var/openvpn-mgmt/log/openvpn-mgmt.0.log"
        if not os.path.isfile( current_log_file ):
            utils.lprint( 1 , f"LOG -> { log_msg }" )
            return
        # OpenVPN service inactive

        with open( current_log_file , 'a' , encoding = 'utf-8' ) as rFile:
            fcntl.flock( rFile , fcntl.LOCK_EX )
            try:
                rFile.write( log_msg )
            except Exception as e:
                utils.lprint( 2 , f"Failed to write msg to log: { e }" )
                utils.lprint( 1 , f"LOG -> { log_msg }" )
            finally:
                fcntl.flock( rFile , fcntl.LOCK_UN )

    def get_header( self , host: str ) -> str:
        datetime_now = datetime.datetime.now()
        time_now_str = datetime_now.strftime( "%Y-%m-%d %H:%M:%S.%f" )[:-3] + self._tz
        log_header = f"{ time_now_str } [{ host }]"
        return log_header.ljust( 49 )
    
logger: log = None
    
def init_global_logger( tz: str ):
    global logger
    logger = log( tz )

if __name__ == "__main__":
    print( "This is a module, should not be executed" )
    exit( 1 )
