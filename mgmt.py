#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import csv
import datetime
import os
import re
import sys
from typing import Tuple

from mgmt import audit
from mgmt import clients
from mgmt import connection
from mgmt import log
from mgmt import ovpn_script
from mgmt import settings
from mgmt import utils

localtz_name = utils.get_tzname()
base_dir = os.path.split(os.path.realpath(__file__))[0]
server_uptime = ""
parser = argparse.ArgumentParser()


def setup_args():
    features_arg_group = parser.add_mutually_exclusive_group()
    features_arg_group.add_argument(
        "--refresh-cfg-cache",
        default=False,
        action="store_true",
        help="Refresh OpenVPN service config & openvpn-mgmt config cache",
    )
    features_arg_group.add_argument(
        "--install-ovpn-script",
        nargs="?",
        metavar="SCRIPT_NAME",
        const="all",
        type=str,
        help="Install OpenVPN scripts to server directory",
    )

    subcommand_subparser = parser.add_subparsers(dest="subcommand")

    audit_parser = subcommand_subparser.add_parser("audit", help="Audit OpenVPN usage")
    audit_parser.add_argument(
        "--period",
        metavar="PERIOD",
        type=str,
        help="Set usage audit period (YEAR[.MONTH[.DAY]])",
    )

    clients_parser = subcommand_subparser.add_parser(
        "clients", help="Manage OpenVPN clients"
    )
    clients_arg_group = clients_parser.add_mutually_exclusive_group()
    clients_arg_group.add_argument(
        "--list", default=False, action="store_true", help="List all valid clients"
    )
    clients_arg_group.add_argument(
        "--status",
        default=False,
        action="store_true",
        help="Show all valid clients' detailed status",
    )
    clients_arg_group.add_argument(
        "--refresh",
        default=False,
        action="store_true",
        help="Refresh valid clients cached datas",
    )
    clients_arg_group.add_argument(
        "--block",
        nargs=2,
        metavar=tuple(["COMMON_NAME", "BLOCK_TO"]),
        type=str,
        help="Block a specific client",
    )
    clients_arg_group.add_argument(
        "--is-blocked",
        metavar="COMMON_NAME",
        type=str,
        help="Check is a specific client being blocked",
    )

    connection_parser = subcommand_subparser.add_parser(
        "connection", help="Manage OpenVPN server connections"
    )
    connection_arg_group = connection_parser.add_mutually_exclusive_group()
    connection_arg_group.add_argument(
        "--mode",
        nargs="?",
        metavar="MODE",
        const="__get__",
        type=str,
        help="Get / Set OpenVPN server connection mode",
    )
    connection_arg_group.add_argument(
        "--list",
        default=False,
        action="store_true",
        help="List all connection detailed datas",
    )
    connection_arg_group.add_argument(
        "--kill",
        metavar="COMMON_NAME",
        type=str,
        help="Kill a connected client's connection",
    )


def parse_period(period: str) -> Tuple[int, int, int]:
    if period is None:
        utils.lprint(2, "Empty period string")
        return -1, -1, -1

    s = period.strip()
    if s == "":
        utils.lprint(2, "Empty period string")
        return -1, -1, -1

    m = re.match(r"^\s*(\d+)(?:\.(\d*))?(?:\.(\d*))?\s*$", s)
    if not m:
        utils.lprint(2, f"Invalid period format: {period!r}")
        return -1, -1, -1

    year = int(m.group(1))
    month = int(m.group(2)) if m.group(2) else 0
    day = int(m.group(3)) if m.group(3) else 0

    if month != 0 and not (1 <= month <= 12):
        utils.lprint(2, f"Invalid month: {month}")
        return -1, -1, -1
    if day != 0 and not (1 <= day <= 31):
        utils.lprint(2, f"Invalid day: {day}")
        return -1, -1, -1

    return year, month, day


def is_openvpn_server_running() -> bool:
    service_name = settings.settings["server"]["service_name"]
    ret = utils.systemctl.has_service(service_name)
    if ret != utils.systemctl.RET_HAS_SERVICE:
        utils.lprint(2, f"Check OpenVPN service existence failed with code { ret }")
        return False
    ret = utils.systemctl.is_service_running(service_name)
    if ret != utils.systemctl.RET_SERVICE_RUNNING:
        utils.lprint(2, f"OpenVPN server is not running or error occured: { ret }")
        return False
    return True


def main():
    log.init_global_logger()
    settings.parse_settings(os.path.join(base_dir, "mgmt.cfg"))

    if len(sys.argv) > 1:
        setup_args()
        args = parser.parse_args()

        if args.install_ovpn_script:
            script_mgmt = ovpn_script.ovpn_script(base_dir)
            exit(script_mgmt.install(args.install_ovpn_script))

        if args.subcommand:
            if args.subcommand == "audit":
                audit_mgmt = audit.audit()
                year = 0
                month = 0
                day = 0
                if args.period:
                    year, month, day = parse_period(args.period)
                    if year == -1 or month == -1 or day == -1:
                        exit(1)
                    # invalid period
                audit_mgmt.collect_usage_data_in_period(year, month, day)
                audit_mgmt.show_usage_data()
                exit(0)

            if args.subcommand == "clients":
                clients_mgmt = clients.clients()
                if args.refresh:
                    exit(clients_mgmt.refresh_client_data())
                elif args.list:
                    exit(clients_mgmt.list_client())
                elif args.status:
                    exit(clients_mgmt.list_client_status())
                elif args.block:
                    exit(clients_mgmt.block_client(args.block[0], args.block[1]))
                elif args.is_blocked:
                    exit(clients_mgmt.is_client_blocked(args.is_blocked))

            if args.subcommand == "connection":
                connection_mgmt = connection.connection()
                if args.mode:
                    if args.mode == "__get__":
                        mode_str = {
                            connection.connection.CONNECTION_MODE_NORMAL: "normal",
                            connection.connection.CONNECTION_MODE_MAINTAIN: "maintain",
                            connection.connection.CONNECTION_MODE_BLOCK: "block",
                        }.get(connection_mgmt.get_mode(), "unknown")
                        utils.lprint(
                            1,
                            f"OpenVPN server is currently in { mode_str } connection mode",
                        )
                        exit(0)
                    else:
                        mode_str = args.mode.lower()
                        if mode_str == "normal":
                            mode = connection.connection.CONNECTION_MODE_NORMAL
                        elif mode_str == "maintain":
                            mode = connection.connection.CONNECTION_MODE_MAINTAIN
                        elif mode_str == "block":
                            mode = connection.connection.CONNECTION_MODE_BLOCK
                        else:
                            utils.lprint(
                                2,
                                f"Illegal OpenVPN server connection mode string: { args.mode }",
                            )
                            exit(1)
                        exit(connection_mgmt.set_mode(mode))
                elif args.list:
                    exit(connection_mgmt.list_connection_datas())
                elif args.kill:
                    exit(connection_mgmt.kill_connection(args.kill))

    if not is_openvpn_server_running():
        exit(1)
    # check service status

    with open("/run/openvpn-server/status-server.log", "r", encoding="utf-8") as rFile:
        log_rows = []
        for row in csv.reader(rFile):
            log_rows.append(row)

    utils.lprint(1, log_rows[0][1])
    # server version

    datetime_now = datetime.datetime.now()
    time_now_str = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
    utils.lprint(1, f"Time now: { time_now_str } { localtz_name }")
    # time now

    utils.lprint(1, f"Service active since: { server_uptime }")
    # active since

    last_log_refresh_time = datetime.datetime.fromtimestamp(int(log_rows[1][2]))
    last_log_refresh_time_str = last_log_refresh_time.strftime("%Y-%m-%d %H:%M:%S")
    last_log_refresh_time_delta_str = (
        f"{ ( datetime_now - last_log_refresh_time ).total_seconds() :.0f}"
    )
    utils.lprint(
        1,
        f"Last log refresh: { last_log_refresh_time_str } { localtz_name } ({ last_log_refresh_time_delta_str } seconds ago)",
    )
    # last log refresh time

    log_rows.pop(0)
    log_rows.pop(0)
    log_rows.pop(-1)
    log_rows.pop(-1)
    # pop datas: server version; last refresh time; global stats; END sign

    utils.lprint(1)

    current_connection_count = (len(log_rows) - 2) // 2
    utils.lprint(1, f"Connected profiles count: { current_connection_count }")
    # connection count

    connected_profiles = []
    detailed_connections_data = []
    detailed_connections_data.append(
        [
            "Common Name",
            "Real IP Addr.",
            "Virtual IP Addr.",
            "Uplink Traffic (B)",
            "Downlink Traffic (B)",
            "Connected Since",
            "Username",
            "Client ID",
            "Data Channal Cipher",
        ]
    )
    for i in range(1, current_connection_count + 1):
        connected_since_time_str = datetime.datetime.fromtimestamp(
            int(log_rows[i][8])
        ).strftime("%Y-%m-%d %H:%M:%S")
        connected_profiles.append(log_rows[i][1])
        detailed_connections_data.append(
            [
                log_rows[i][1],  # common name
                log_rows[i][2],  # real ip addr
                log_rows[i][3],  # virtual ip addr
                f"{ utils.conv_bytes_to_formel_str( int( log_rows[i][5] ) ) } ({ log_rows[i][5] })",  # uplink traffic
                f"{ utils.conv_bytes_to_formel_str( int( log_rows[i][6] ) ) } ({ log_rows[i][6] })",  # downlink traffic
                f"{ connected_since_time_str } { localtz_name }",  # connected since
                log_rows[i][9],  # username
                log_rows[i][10],  # client id
                log_rows[i][12],  # data channal cipher
            ]
        )

    col_widths = [
        max(len(str(item)) for item in col) for col in zip(*detailed_connections_data)
    ]
    for row in detailed_connections_data:
        utils.lprint(
            1,
            " | ".join(
                f"{ item.ljust( col_widths[i] ) }" for i, item in enumerate(row)
            ),
        )
    # connected profiles

    utils.lprint(1)

    with open(
        "/etc/openvpn/server/easy-rsa/pki/index.txt", "r", encoding="utf-8"
    ) as rFile:
        cert_index_lines = rFile.readlines()[1:]

    valid_certs = []
    for line in cert_index_lines:
        if line.startswith("R"):
            continue
        parts = line.split("=")
        if len(parts) > 1:
            valid_certs.append(parts[1].strip())
    valid_certs.sort()

    utils.lprint(1, f"Valid certifications count: { len( valid_certs ) }")
    # certs count

    detailed_certs_data = []
    detailed_certs_data.append(["Common Name", "Status"])
    for cert in valid_certs:
        detailed_certs_data.append(
            [cert, "Connected" if cert in connected_profiles else "Disconnected"]
        )

    col_widths = [
        max(len(str(item)) for item in col) for col in zip(*detailed_certs_data)
    ]
    for row in detailed_certs_data:
        utils.lprint(
            1,
            " | ".join(
                f"{ item.ljust( col_widths[i] ) }" for i, item in enumerate(row)
            ),
        )


if __name__ == "__main__":
    main()
