import configparser
import os
import shutil

from mgmt import log
from mgmt import settings
from mgmt import utils

class ovpn_script:
    def __init__( self , base_dir: str ):
        self._script_dir = os.path.join( base_dir , "script" )
        self._loghost = "ovpnscr"

        parser = configparser.ConfigParser()
        parser.read( os.path.join( self._script_dir , "script.cfg" ) )
        if not parser.has_section( "script" ):
            raise Exception( "OpenVPN script cfg file has no \"script\" section" )
        
        scripts = parser.options( "script" )
        self._scripts = []
        for script in scripts:
            script_path = parser["script"][script]
            if len( script_path ) == 0:
                continue
            if not os.path.isfile( os.path.join( self._script_dir , script_path ) ):
                continue
            self._scripts.append( {
                "script": script ,
                "path": script_path
            } )
        # erase all empty / not existing script settings

        return
    
    def install( self , target: str ) -> int:
        script_install_dir = os.path.join( settings.settings["server"]["server_dir"] , "script" )
        ovpn_cfg_setup_info = ""
        copied = False
        utils.lprint( 1 , f"Installing OpenVPN scripts to: { script_install_dir }" )
        for script in self._scripts:
            if target != "all" and target != script["script"]:
                continue
            # not installing all, target is not this script

            from_path = os.path.join( self._script_dir , script["path"] )
            to_path = os.path.join( script_install_dir , script["path"] )
            try:
                shutil.copyfile( from_path , to_path )
                os.chmod( to_path , 0o755 )
                copied = True
                # for not installing all situation: target has been found
            except Exception as e:
                log.logger.write_log( self._loghost , f"Failed to install OpenVPN script. [type='{ script['script'] }', from='{ from_path }', to='{ to_path }', error='{ e }']" )
                utils.lprint( 2 , f" - { from_path } -> { to_path }: Failed ({ e })" )
                continue

            log.logger.write_log( self._loghost , f"Installed OpenVPN script. [type='{ script['script'] }', from='{ from_path }', to='{ to_path }']" )
            utils.lprint( 1 , f" - { from_path } -> { to_path }: Succeeded" )
            ovpn_cfg_setup_info += f" - { script['script'] } \"script/{ script['path'] }\"\n"

        if not copied:
            utils.lprint( 2 , f"Target \"{ target }\" doesn't exist or none of the installation succeeded." )
            return 1

        ovpn_cfg_setup_info = "OpenVPN script installation finished.\nYou may add the following lines into your server config file:\n" + ovpn_cfg_setup_info
        ovpn_cfg_setup_info += "If you have already done this, you can ignore this message."
        utils.lprint( 1 , ovpn_cfg_setup_info )
        return 0

if __name__ == "__main__":
    print( "This is a module, should not be executed" )
    exit( 1 )
