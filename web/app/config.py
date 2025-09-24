import configparser

config = {
    "app": {
        "secret_key": None,
        "is_production_env": False,
        "db_path": "/var/openvpn-mgmt/web/users.db",
    }
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


class flask_config:
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
