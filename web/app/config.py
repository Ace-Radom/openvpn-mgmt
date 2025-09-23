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
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
