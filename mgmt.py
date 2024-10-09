import csv
import datetime
import subprocess

localtz_name = datetime.datetime.now().astimezone().tzname()

def conv_bytes_to_formel_str( bytes_count: int ) -> str:
    if bytes_count < 1024:
        return f"{ bytes_count } bytes"
    elif bytes_count < 1048576:
        return f"{ bytes_count / 1024 :.2f} KB"
    elif bytes_count < 1073741824:
        return f"{ bytes_count / 1048576 :.2f} MB"
    else:
        return f"{ bytes_count / 1073741824 :.2f} GB"

def main():
    try:
        result = subprocess.run(
            [ "systemctl" , "status" , "openvpn-server@server.service" ] ,
            stdout = subprocess.PIPE ,
            stderr = subprocess.PIPE ,
            text = True
        )

        if "active (running)" not in result.stdout:
            print( "OpenVPN server is not running" )
            exit( 1 )
        # service stopped

        for line in result.stdout.splitlines():
            if "Active:" in line:
                uptime_line = line.split( ';' )[0]
                uptime = uptime_line.split( "since" )[-1][4:].strip()

    except Exception as e:
        print( f"Error when checking service: { e }" )
        exit( 1 )
    # check service status

    with open( "/run/openvpn-server/status-server.log" , 'r' , encoding = 'utf-8' ) as rFile:
        log_rows = []
        for row in csv.reader( rFile ):
            log_rows.append( row )

    print( log_rows[0][1] )
    # server version

    datetime_now = datetime.datetime.now()
    time_now_str = datetime_now.strftime( "%Y-%m-%d %H:%M:%S" )
    print( f"Time now: { time_now_str } { localtz_name }" )
    # time now

    print( f"Service active since: { uptime }" )
    # active since

    last_log_refresh_time = datetime.datetime.fromtimestamp( int( log_rows[1][2] ) )
    last_log_refresh_time_str = last_log_refresh_time.strftime( "%Y-%m-%d %H:%M:%S" )
    last_log_refresh_time_delta_str = f"{ ( datetime_now - last_log_refresh_time ).total_seconds() :.0f}"
    print( f"Last log refresh: { last_log_refresh_time_str } { localtz_name } ({ last_log_refresh_time_delta_str } seconds ago)" )
    # last log refresh time

    log_rows.pop( 0 )
    log_rows.pop( 0 )
    log_rows.pop( -1 )
    log_rows.pop( -1 )
    # pop datas: server version; last refresh time; global stats; END sign

    print()

    current_connection_count = ( len( log_rows ) - 2 ) // 2
    print( f"Connected profiles count: { current_connection_count }" )
    # connection count

    connected_profiles = []
    detailed_connections_data = []
    detailed_connections_data.append( [
        "Common Name" ,
        "Real Addr." ,
        "Virtual Addr." ,
        "Uplink Traffic (B)" ,
        "Downlink Traffic (B)" ,
        "Connected Since" ,
        "Username" ,
        "Client ID" ,
        "Data Channal Cipher"
    ] )
    for i in range( 1 , current_connection_count + 1 ):
        connected_since_time_str = datetime.datetime.fromtimestamp( int( log_rows[i][8] ) ).strftime( "%Y-%m-%d %H:%M:%S" )
        connected_profiles.append( log_rows[i][1] )
        detailed_connections_data.append( [
            log_rows[i][1] ,  # common name
            log_rows[i][2] ,  # real addr
            log_rows[i][3] ,  # virtual addr
            f"{ conv_bytes_to_formel_str( int( log_rows[i][5] ) ) } ({ log_rows[i][5] })" ,  # uplink traffic
            f"{ conv_bytes_to_formel_str( int( log_rows[i][6] ) ) } ({ log_rows[i][6] })" ,  # downlink traffic
            f"{ connected_since_time_str } { localtz_name }" ,  # connected since
            log_rows[i][9] ,  # username
            log_rows[i][10] ,  # client id
            log_rows[i][12]  # data channal cipher
        ] )

    col_widths = [max( len( str( item ) ) for item in col ) for col in zip( *detailed_connections_data )]
    for row in detailed_connections_data:
        print( " | ".join( f"{ item.ljust( col_widths[i] ) }" for i , item in enumerate( row ) ) )
    # connected profiles

    print()

    with open( "/etc/openvpn/server/easy-rsa/pki/index.txt" , 'r' , encoding = "utf-8" ) as rFile:
        cert_index_lines = rFile.readlines()[1:]

    valid_certs = []
    for line in cert_index_lines:
        if line.startswith( 'R' ):
            continue
        parts = line.split( '=' )
        if len( parts ) > 1:
            valid_certs.append( parts[1].strip() )
    valid_certs.sort()

    print( f"Valid certifications count: { len( valid_certs ) }" )
    # certs count

    detailed_certs_data = []
    detailed_certs_data.append( [
        "Common Name" ,
        "Status"
    ] )
    for cert in valid_certs:
        detailed_certs_data.append( [
            cert ,
            "Connected" if cert in connected_profiles else "Disconnected"
        ] )

    col_widths = [max( len( str( item ) ) for item in col ) for col in zip( *detailed_certs_data )]
    for row in detailed_certs_data:
        print( " | ".join( f"{ item.ljust( col_widths[i] ) }" for i , item in enumerate( row ) ) )

if __name__ == "__main__":
    main()
