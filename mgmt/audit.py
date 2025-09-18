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
        self._uplink_total = 0
        self._downlink_total = 0
        self._service_starttime = ""
        self._period_str = ""

    def _parse_log_in_period(self, year: int, month: int, day: int) -> bool:
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
                disconnected_time = datetime.datetime.strptime(
                    disconnected_time_match.group(), "%Y-%m-%d %H:%M:%S.%f"
                )
                if not (
                    (year == 0 or year == disconnected_time.year)
                    and (month == 0 or month == disconnected_time.month)
                    and (day == 0 or day == disconnected_time.day)
                ):
                    continue
                # not in period

                data_match = re.search(data_pattern, msg)
                if not data_match:
                    utils.lprint(2, f"Cannot match datas on line { line_count }, skip")
                    utils.lprint(2, f"Line: { msg }")
                    error_line_count += 1
                    continue
                # match datas
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
            f"Total { len(self._connection_datas) } connection datas in period found, { error_line_count } lines parse failed",
        )
        return True

    @staticmethod
    def _parse_period_to_str(year, month, day) -> str:
        if year == 0 and month == 0 and day == 0:
            return ""

        if month == 0 and day == 0:
            return f"{ year }"

        month_str = {
            1: "Jan.",
            2: "Feb.",
            3: "Mar.",
            4: "Apr.",
            5: "May.",
            6: "Jun.",
            7: "Jul.",
            8: "Aug.",
            9: "Sep.",
            10: "Oct.",
            11: "Nov.",
            12: "Dec.",
        }.get(month)

        if day == 0:
            return f"{month_str} {year}"

        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        day_str = f"{day}{suffix}"

        return f"{day_str} {month_str} {year}"

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
            if not self._parse_log_in_period(year, month, day):
                utils.lprint(2, "Failed to parse log, cannot collect usage data")
                return 1

        for data in self._connection_datas:
            cn = data["cn"]
            uplink = data["uplink"]
            downlink = data["downlink"]
            if cn not in self._usage_datas:
                self._usage_datas[cn] = {"uplink": 0, "downlink": 0}
            # new cn
            self._usage_datas[cn]["uplink"] += uplink
            self._usage_datas[cn]["downlink"] += downlink
            self._uplink_total += uplink
            self._downlink_total += downlink

        self._usage_datas = {
            k: self._usage_datas[k] for k in sorted(self._usage_datas.keys())
        }
        self._period_str = self._parse_period_to_str(year, month, day)
        return 0

    def show_usage_data(self) -> int:
        datas_list = []
        datas_list.append(["Common Name", "Uplink (B)", "Downlink (B)"])

        for cn, data in self._usage_datas.items():
            uplink = data["uplink"]
            downlink = data["downlink"]
            datas_list.append(
                [
                    cn,
                    f"{ utils.conv_bytes_to_formel_str(uplink) } ({ uplink })",
                    f"{ utils.conv_bytes_to_formel_str(downlink) } ({ downlink })",
                ]
            )

        utils.lprint(1)
        if self._period_str == "":
            utils.lprint(
                1,
                f"Usage data since OpenVPN service started on { self._service_starttime }:",
            )
        else:
            utils.lprint(1, f"Usage data in period { self._period_str }:")
        utils.lprint(
            1,
            f"Total uplink: { utils.conv_bytes_to_formel_str(self._uplink_total) } ({self._uplink_total})",
        )
        utils.lprint(
            1,
            f"Total downlink: {utils.conv_bytes_to_formel_str(self._downlink_total)} ({self._downlink_total})",
        )

        col_widths = [max(len(str(item)) for item in col) for col in zip(*datas_list)]
        for row in datas_list:
            utils.lprint(
                1,
                " | ".join(
                    f"{ item.ljust( col_widths[i] ) }" for i, item in enumerate(row)
                ),
            )

        return 0


if __name__ == "__main__":
    print("This is a module, should not be executed")
    exit(1)
