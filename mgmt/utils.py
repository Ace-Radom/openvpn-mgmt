#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import subprocess

from mgmt import settings


def conv_bytes_to_formel_str(bytes_count: int) -> str:
    if bytes_count < 1024:
        return f"{ bytes_count } bytes"
    elif bytes_count < 1048576:
        return f"{ bytes_count / 1024 :.2f} KB"
    elif bytes_count < 1073741824:
        return f"{ bytes_count / 1048576 :.2f} MB"
    else:
        return f"{ bytes_count / 1073741824 :.2f} GB"


def lprint(level: int, *args, **kwargs):
    if level >= settings.settings["base"]["output_level"]:
        print(*args, **kwargs)


def get_tzname() -> str:
    return datetime.datetime.now().astimezone().tzname()


class systemctl:
    RET_ERROR = -1
    RET_HAS_SERVICE = 0
    RET_NOT_HAS_SERVICE = 1
    RET_SERVICE_RUNNING = 0
    RET_SERVICE_NOT_RUNNING = 1

    @staticmethod
    def has_service(service: str) -> int:
        try:
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if service in result.stdout:
                return systemctl.RET_HAS_SERVICE
            else:
                return systemctl.RET_NOT_HAS_SERVICE
        except:
            return systemctl.RET_ERROR

    @staticmethod
    def is_service_running(service: str) -> int:
        try:
            result = subprocess.run(
                ["systemctl", "status", service],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if "active (running)" in result.stdout:
                return systemctl.RET_SERVICE_RUNNING
            else:
                return systemctl.RET_SERVICE_NOT_RUNNING
        except:
            return systemctl.RET_ERROR


if __name__ == "__main__":
    print("This is a module, should not be executed")
    exit(1)
