import configparser

config = {
    "app": {"is_production_env": False, "mgmt_path": "/openvpn-mgmt/mgmt.py"},
    "challenge": {
        "pubkey_store_dir": "/var/openvpn-mgmt/web/challenge",
        "index_filename": "index.json",
        "use_pss": True,
        "hash": "sha256",
        "challenge_str_len": 32,
        "token_len": 64,
        "handshake_timeout_after": 60,
        "token_expire_after": 300,
    },
    "profiles": {
        "generate_dir": "/root",
        "store_dir": "/var/openvpn-mgmt/profiles",
        "hash": "sha256",
        "max_per_user": 5,
    },
    "glances": {"server_url": "http://localhost:61208/api/4", "phys_na_name": "eth0"},
    "redis": {"key_prefix": "openvpn-mgmt-webapi:", "db_url": "redis://127.0.0.1:6379"},
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
        if (
            parser.has_option("app", "mgmt_path")
            and len(parser["app"]["mgmt_path"]) != 0
        ):
            config["app"]["mgmt_path"] = parser["app"]["mgmt_path"]

    if parser.has_section("challenge"):
        if (
            parser.has_option("challenge", "pubkey_store_dir")
            and len(parser["challenge"]["pubkey_store_dir"]) != 0
        ):
            config["challenge"]["pubkey_store_dir"] = parser["challenge"][
                "pubkey_store_dir"
            ]
        if (
            parser.has_option("challenge", "index_filename")
            and len(parser["challenge"]["index_filename"]) != 0
        ):
            config["challenge"]["index_filename"] = parser["challenge"][
                "index_filename"
            ]
        if (
            parser.has_option("challenge", "use_pss")
            and len(parser["challenge"]["use_pss"]) != 0
            and parser["challenge"]["use_pss"].isdigit()
        ):
            config["challenge"]["use_pss"] = int(parser["challenge"]["use_pss"]) != 0
        if (
            parser.has_option("challenge", "hash")
            and len(parser["challenge"]["hash"]) != 0
            and parser["challenge"]["hash"] in ["md5", "sha1", "sha256", "sha512"]
        ):
            config["challenge"]["hash"] = parser["challenge"]["hash"]
        if (
            parser.has_option("challenge", "challenge_str_len")
            and len(parser["challenge"]["challenge_str_len"]) != 0
            and parser["challenge"]["challenge_str_len"].isdigit()
        ):
            config["challenge"]["challenge_str_len"] = int(
                parser["challenge"]["challenge_str_len"]
            )
        if (
            parser.has_option("challenge", "token_len")
            and len(parser["challenge"]["token_len"]) != 0
            and parser["challenge"]["token_len"].isdigit()
        ):
            config["challenge"]["token_len"] = int(parser["challenge"]["token_len"])
        if (
            parser.has_option("challenge", "handshake_timeout_after")
            and len(parser["challenge"]["handshake_timeout_after"]) != 0
            and parser["challenge"]["handshake_timeout_after"].isdigit()
        ):
            config["challenge"]["handshake_timeout_after"] = int(
                parser["challenge"]["handshake_timeout_after"]
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

    if parser.has_section("redis"):
        if (
            parser.has_option("redis", "key_prefix")
            and len(parser["redis"]["key_prefix"]) != 0
        ):
            config["redis"]["key_prefix"] = parser["redis"]["key_prefix"]
        if parser.has_option("redis", "db_url") and len(parser["redis"]["db_url"]) != 0:
            config["redis"]["db_url"] = parser["redis"]["db_url"]
