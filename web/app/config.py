import configparser

config = {
    "app": {"is_production_env": False},
    "glances": {"server_url": "http://localhost:61208/api/4", "phys_na_name": "eth0"},
}


def parse_config(config_path: str):
    parser = configparser.ConfigParser()
    parser.read(config_path)

    if parser.has_section("app"):
        if (
            parser.has_option("app", "is_production_env")
            and len(parser["app"]["is_production_env"]) != 0
            and parser["app"]["is_production_env"].isdigit()
        ):
            config["app"]["is_production_env"] = (
                int(parser["app"]["is_production_env"]) != 0
            )

    if parser.has_section("glances"):
        if (
            parser.has_option("glances", "server_url")
            and len(parser["glances"]["server_url"]) != 0
        ):
            config["glances"]["server_url"] = parser["glances"]["server_url"]
        if (
            parser.has_option("glances", "phys_na_name")
            and len(parser["glances"]["phys_na_name"]) != 0
        ):
            config["glances"]["phys_na_name"] = parser["glances"]["phys_na_name"]
