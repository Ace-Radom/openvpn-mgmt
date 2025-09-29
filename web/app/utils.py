import ipaddress

from app import config


def build_server_link(route: str, is_public_link: bool = False) -> str:
    if is_public_link:
        host = config.config["server"]["public_ip"]
    else:
        host = config.config["server"]["private_ip"]

    if config.config["server"]["use_https"]:
        protocol = "https"
    else:
        protocol = "http"

    port = config.config["server"]["port"]

    if route[0] == "/":
        route = route[1:]

    return f"{ protocol }://{ host }:{ port }/{ route }"


def is_valid_ipv4(ip: str) -> bool:
    try:
        _ = ipaddress.IPv4Address(ip)
        return True
    except:
        return False
