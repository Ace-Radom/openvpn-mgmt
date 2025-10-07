import requests

GLANCES_BASE_URL = "http://127.0.0.1:61208/api/4"


def get_cpu_data() -> dict | None:
    response = requests.get(f"{ GLANCES_BASE_URL }/cpu")
    if response.status_code != 200:
        return None

    try:
        cpu_data = response.json()
    except:
        return None

    total_usage = cpu_data["total"]
    core_count = cpu_data["cpucore"]

    response = requests.get(f"{ GLANCES_BASE_URL }/percpu")
    if response.status_code != 200:
        return None

    try:
        percpu_data = response.json()
    except:
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


def get_mem_data() -> dict | None:
    response = requests.get(f"{ GLANCES_BASE_URL }/mem")
    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except:
        return None

    return {
        "total": data["total"],
        "available": data["available"],
        "used": data["used"],
        "usage_percent": data["percent"],
    }


def get_network_data() -> dict | None:
    response = requests.get(f"{ GLANCES_BASE_URL }/network")
    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except:
        return None

    eth0_data = next((i for i in data if i.get(i.get("key")) == "eth0"), None)
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
