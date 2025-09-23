import configparser

cfg = {"app": {"secret_key": None, "is_production_env": False}}


def parse_config(config_path: str):
    parser = configparser.ConfigParser()
    parser.read(config_path)

    if parser.has_section("app"):
        if (
            parser.has_option("app", "secret_key")
            and len(parser["app"]["secret_key"]) != 0
        ):
            cfg["app"]["secret_key"] = parser["app"]["secret_key"]
        if (
            parser.has_option("app", "is_production_env")
            and len(parser["app"]["is_production_env"]) != 0
            and parser["app"]["is_production_env"].isdigit()
        ):
            cfg["app"]["is_production_env"] = (
                int(parser["app"]["is_production_env"]) != 0
            )


class config:
    def __init__(self) -> None:
        if cfg["app"]["secret_key"] is None:
            raise RuntimeError("Secret key cannot be None")
        return

    SECRET_KEY = cfg["app"]["secret_key"]
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"


class debug_config(config):
    DEBUG = True


class production_config(config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
