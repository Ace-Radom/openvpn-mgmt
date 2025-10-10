import configparser

config = {
    "app": {"is_production_env": False},
    "profiles": {
        "generate_dir": "/root",
        "store_dir": "/var/openvpn-mgmt/profiles",
        "hash": "sha256",
        "max_per_user": 5,
    },
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

    if parser.has_section("profiles"):
        if (
            parser.has_option("profiles", "generate_dir")
            and len(parser["profiles"]["generate_dir"]) != 0
        ):
            config["profiles"]["generate_dir"] = parser["profiles"]["generate_dir"]
        if (
            parser.has_option("profiles", "store_dir")
            and len(parser["profiles"]["store_dir"]) != 0
        ):
            config["profiles"]["store_dir"] = parser["profiles"]["store_dir"]
        if (
            parser.has_option("profiles", "hash")
            and len(parser["profiles"]["hash"]) != 0
            and parser["profiles"]["hash"] in ["md5", "sha1", "sha256", "sha512"]
        ):
            config["profiles"]["hash"] = parser["profiles"]["hash"]
        if (
            parser.has_option("profiles", "max_per_user")
            and len(parser["profiles"]["max_per_user"]) != 0
            and parser["profiles"]["max_per_user"].isdigit()
        ):
            value = int(parser["profiles"]["max_per_user"])
            if value > 0:
                config["profiles"]["max_per_user"] = value

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
