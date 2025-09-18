#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import re

from mgmt import log
from mgmt import utils


class audit:
    def __init__(self) -> None:
        self._connection_datas = []
        self._usage_datas = {}
        self._service_starttime = ""

    def parse_log(self) -> bool:
        log_str = log.logger.read_log()
        if log_str == "":
            utils.lprint(2, "Cannot read log, parse failed")
            return False

        log_msgs = log_str.splitlines()
        utils.lprint(1, f"Total { len(log_msgs) } lines of log found")

        time_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+"

        if log_msgs[0][:3] != "===":
            utils.lprint(2, "Log doesn't start with service start time")
            self._service_starttime = ""
        else:
            service_starttime_match = re.search(time_pattern, log_msgs[0])
            if service_starttime_match:
                self._service_starttime = service_starttime_match.group()
            else:
                utils.lprint(
                    2, "Failed to find service start time in the first line of the log"
                )
                self._service_starttime = ""

        data_pattern = r"cn='(?P<cn>[^']+)'\s*,\s*real_ip='(?P<real_ip>[^']+)'\s*,\s*virtual_ip='(?P<virtual_ip>[^']+)'\s*,\s*uplink=(?P<uplink>\d+)\s*,\s*downlink=(?P<downlink>\d+)"
        line_count = -1
        error_line_count = 0
        for msg in log_msgs:
            line_count += 1

            if "openvpn" in msg and "diconnected" in msg:
                disconnected_time_match = re.search(time_pattern, msg)
                if not disconnected_time_match:
                    utils.lprint(
                        2, f"Cannot match diconnected time on line { line_count }, skip"
                    )
                    utils.lprint(2, f"Line: { msg }")
                    error_line_count += 1
                    continue
                # match disconnected time str

                data_match = re.search(data_pattern, msg)
                if not data_match:
                    utils.lprint(2, f"Cannot match datas on line { line_count }, skip")
                    utils.lprint(2, f"Line: { msg }")
                    error_line_count += 1
                    continue
                # match datas

                disconnected_time = datetime.datetime.strptime(
                    disconnected_time_match.group(), "%Y-%m-%d %H:%M:%S.%f"
                )
                data = data_match.groupdict()
                connection_data = {
                    "line": line_count,
                    "dt_year": disconnected_time.year,
                    "dt_month": disconnected_time.month,
                    "dt_day": disconnected_time.day,
                    "dt_hour": disconnected_time.hour,
                    "dt_minute": disconnected_time.minute,
                    "dt_second": disconnected_time.second,
                    "dt_microsecond": disconnected_time.microsecond,
                    "cn": data["cn"],
                    "real_ip": data["real_ip"],
                    "virtual_ip": data["virtual_ip"],
                    "uplink": int(data["uplink"]),
                    "downlink": int(data["downlink"]),
                }
                self._connection_datas.append(connection_data)
        # find & parse connection datas

        utils.lprint(
            1,
            f"Total { len(self._connection_datas) } connection datas found, { error_line_count } lines parse failed",
        )
        return True

    def collect_usage_data_in_period(
        self, year: int = 0, month: int = 0, day: int = 0
    ) -> int:
        if year == 0 and month != 0:
            utils.lprint(2, "Invalid period: month was specified without year")
            return 1
        if month == 0 and day != 0:
            utils.lprint(2, "Invalid period: day was specified without month")
            return 1

        if len(self._connection_datas) == 0:
            if not self.parse_log():
                utils.lprint(2, "Failed to parse log, cannot collect usage data")
                return 1

        for data in self._connection_datas:
            if (
                (year == 0 or year == data["dt_year"])
                and (month == 0 or month == data["dt_month"])
                and (day == 0 or day == data["dt_day"])
            ):
                cn = data["cn"]
                uplink = data["uplink"]
                downlink = data["downlink"]
                if cn not in self._usage_datas:
                    self._usage_datas[cn] = {"uplink": 0, "downlink": 0}
                # new cn
                self._usage_datas[cn]["uplink"] += uplink
                self._usage_datas[cn]["downlink"] += downlink

        return 0

    def show_usage_data(self) -> int:
        for key, data in self._usage_datas.items():
            print(key, data)

        return 0


if __name__ == "__main__":
    print("This is a module, should not be executed")
    exit(1)
