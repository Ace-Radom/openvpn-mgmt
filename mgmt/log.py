#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import fcntl
import os

from mgmt import utils


class log:
    def __init__(self):
        self._log_file = "/var/openvpn-mgmt/log/openvpn-mgmt.0.log"
        self._tz = utils.get_tzname()

    def write_log(self, host: str, msg: str):
        log_msg = f"{ self.get_header( host ) } { msg }\n"
        if not os.path.isfile(self._log_file):
            utils.lprint(1, f"LOG -> { log_msg }")
            return
        # OpenVPN service inactive

        with open(self._log_file, "a", encoding="utf-8") as wFile:
            fcntl.flock(wFile, fcntl.LOCK_EX)
            try:
                wFile.write(log_msg)
            except Exception as e:
                utils.lprint(2, f"Failed to write msg to log: { e }")
                utils.lprint(1, f"LOG -> { log_msg }")
            finally:
                fcntl.flock(wFile, fcntl.LOCK_UN)

    def get_header(self, host: str) -> str:
        datetime_now = datetime.datetime.now()
        time_now_str = datetime_now.strftime("%Y-%m-%d %H:%M:%S.%f") + " " + self._tz
        log_header = f"{ time_now_str } [{ host }]"
        return log_header.ljust(49)

    def read_log(self) -> str:
        with open(self._log_file, "r", encoding="utf-8") as rFile:
            fcntl.flock(rFile, fcntl.LOCK_EX)
            try:
                log_str = rFile.read()
            except Exception as e:
                utils.lprint(
                    2, f"Failed to read log from file { self._log_file }: { e }"
                )
                log_str = ""
            finally:
                fcntl.flock(rFile, fcntl.LOCK_UN)
        return log_str


logger: log = None


def init_global_logger():
    global logger
    logger = log()


if __name__ == "__main__":
    print("This is a module, should not be executed")
    exit(1)
