import re
import requests

from app import config

glances_base_url = ""


def get_data_from_glances(endpoint: str, plaintext=False):
    global glances_base_url

    if not glances_base_url:
        glances_base_url = config.config["glances"]["server_url"]

    response = requests.get(f"{ glances_base_url }/{ endpoint }")
    if response.status_code != 200:
        return None

    try:
        if plaintext:
            data = response.text
        else:
            data = response.json()
    except:
        return None

    return data


def get_cpu_usage_data() -> dict | None:
    cpu_data = get_data_from_glances("cpu")
    if cpu_data is None:
        return None

    total_usage = cpu_data["total"]
    core_count = cpu_data["cpucore"]

    percpu_data = get_data_from_glances("percpu")
    if percpu_data is None:
        return None

    percpu_usage = []
    for cpu_core_data in percpu_data:
        key = cpu_core_data["key"]
        index = cpu_core_data[key]
        usage = cpu_core_data["total"]
        percpu_usage.append({"index": index, "usage": usage})

    return {
        "total_usage": total_usage,
        "core_count": core_count,
        "percpu_usage": percpu_usage,
    }


def get_mem_usage_data() -> dict | None:
    data = get_data_from_glances("mem")
    if data is None:
        return None

    return {
        "total": data["total"],
        "available": data["available"],
        "used": data["used"],
        "usage_percent": data["percent"],
    }


def get_network_usage_data() -> dict | None:
    data = get_data_from_glances("network")
    if data is None:
        return None

    eth0_data = next(
        (
            i
            for i in data
            if i.get(i.get("key")) == config.config["glances"]["phys_na_name"]
        ),
        None,
    )
    if eth0_data is None:
        return None

    return {
        "speed": eth0_data["speed"],
        "time_since_last_update": eth0_data["time_since_update"],
        "bytes_sent_since_last_update": eth0_data["bytes_sent"],
        "bytes_recv_since_last_update": eth0_data["bytes_recv"],
        "bytes_sent_rate_per_sec": eth0_data["bytes_sent_rate_per_sec"],
        "bytes_recv_rate_per_sec": eth0_data["bytes_recv_rate_per_sec"],
    }


def get_cpu_hardware_data():
    data = get_data_from_glances("core")
    if data is None:
        return None

    return {"phys_core_count": data["phys"], "log_core_count": data["log"]}


def get_uptime_data():
    data = get_data_from_glances("uptime", plaintext=True)
    if data is None:
        return None

    days = 0
    hours = 0
    minutes = 0
    seconds = 0

    day_match = re.search(r"(\d+)\s+day", data)
    if day_match:
        days = int(day_match.group(1))

    time_match = re.search(r"(\d+):(\d+):(\d+)", data)
    if time_match:
        hours, minutes, seconds = map(int, time_match.groups())

    return {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}
