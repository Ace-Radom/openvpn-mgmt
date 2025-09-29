import configparser

from app.utils import is_valid_ipv4

config = {
    "app": {
        "secret_key": None,
        "is_production_env": False,
        "db_path": "/var/openvpn-mgmt/web/users.db",
    },
    "server": {
        "public_ip": None,
        "private_ip": None,
        "port": None,
        "use_https": False
        # all traffics should be forwarded by nginx
        # so if nginx enables https, we need to know
    },
    "gmail": {
        "discovery_path": None,
        "token_path": None,
        "secret_path": None,
        "sender_email_addr": None,
    },
}


def parse_config(config_path: str):
    parser = configparser.ConfigParser()
    parser.read(config_path)

    if parser.has_section("app"):
        if (
            parser.has_option("app", "secret_key")
            and len(parser["app"]["secret_key"]) != 0
        ):
            config["app"]["secret_key"] = parser["app"]["secret_key"]
        if (
            parser.has_option("app", "is_production_env")
            and len(parser["app"]["is_production_env"]) != 0
            and parser["app"]["is_production_env"].isdigit()
        ):
            config["app"]["is_production_env"] = (
                int(parser["app"]["is_production_env"]) != 0
            )
        if parser.has_option("app", "db_path") and len(parser["app"]["db_path"]) != 0:
            config["app"]["db_path"] = parser["app"]["db_path"]

    if parser.has_section("server"):
        if (
            parser.has_option("server", "public_ip")
            and len(parser["server"]["public_ip"]) != 0
            and is_valid_ipv4(parser["server"]["public_ip"])
        ):
            config["server"]["public_ip"] = parser["server"]["public_ip"]
        if (
            parser.has_option("server", "private_ip")
            and len(parser["server"]["private_ip"]) != 0
            and is_valid_ipv4(parser["server"]["private_ip"])
        ):
            config["server"]["private_ip"] = parser["server"]["private_ip"]
        if (
            parser.has_option("server", "port")
            and len(parser["server"]["port"]) != 0
            and parser["server"]["port"].isdigit()
        ):
            config["server"]["port"] = int(parser["server"]["port"])
        if (
            parser.has_option("server", "use_https")
            and len(parser["server"]["use_https"]) != 0
            and parser["server"]["use_https"].isdigit()
        ):
            config["server"]["use_https"] = int(parser["server"]["use_https"]) != 0

    if parser.has_section("gmail"):
        if (
            parser.has_option("gmail", "discovery_path")
            and len(parser["gmail"]["discovery_path"]) != 0
        ):
            config["gmail"]["discovery_path"] = parser["gmail"]["discovery_path"]
        if (
            parser.has_option("gmail", "token_path")
            and len(parser["gmail"]["token_path"]) != 0
        ):
            config["gmail"]["token_path"] = parser["gmail"]["token_path"]
        if (
            parser.has_option("gmail", "secret_path")
            and len(parser["gmail"]["secret_path"]) != 0
        ):
            config["gmail"]["secret_path"] = parser["gmail"]["secret_path"]
        if (
            parser.has_option("gmail", "sender_email_addr")
            and len(parser["gmail"]["sender_email_addr"]) != 0
            and parser["gmail"]["sender_email_addr"].find("@gmail.com") != -1
        ):
            config["gmail"]["sender_email_addr"] = parser["gmail"]["sender_email_addr"]


class flask_config:
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
