#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime

from mgmt import settings

def conv_bytes_to_formel_str( bytes_count: int ) -> str:
    if bytes_count < 1024:
        return f"{ bytes_count } bytes"
    elif bytes_count < 1048576:
        return f"{ bytes_count / 1024 :.2f} KB"
    elif bytes_count < 1073741824:
        return f"{ bytes_count / 1048576 :.2f} MB"
    else:
        return f"{ bytes_count / 1073741824 :.2f} GB"
    
def lprint( level: int , *args , **kwargs ):
    if level >= settings.settings["base"]["output_level"]:
        print( *args , **kwargs )

def get_tzname() -> str:
    return datetime.datetime.now().astimezone().tzname()

if __name__ == "__main__":
    print( "This is a module, should not be executed" )
    exit( 1 )
