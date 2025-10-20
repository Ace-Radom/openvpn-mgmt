import json
import os
import secrets
import threading

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime

from app import config
from app.helpers import redis_helper

lock = threading.RLock()


def init():
    pubkey_store_dir = config.config["challenge"]["pubkey_store_dir"]
    if not os.path.exists(pubkey_store_dir):
        os.makedirs(pubkey_store_dir)
    if not os.path.isdir(pubkey_store_dir):
        raise RuntimeError("Challenge pubkey store dir is not a directory")


def get_index() -> dict | None:
    index_path = os.path.join(
        config.config["challenge"]["pubkey_store_dir"],
        config.config["challenge"]["index_filename"],
    )

    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as file:
                index = json.load(file)
        except:
            return None
    else:
        return None

    return index


def get_hash_func():
    hash_name = config.config["challenge"]["hash"]
    if hash_name == "md5":
        return hashes.MD5()
    elif hash_name == "sha1":
        return hashes.SHA1()
    elif hash_name == "sha256":
        return hashes.SHA256()
    elif hash_name == "sha512":
        return hashes.SHA512()


def get_padding_algo():
    if config.config["challenge"]["use_pss"]:
        return padding.PSS(
            msf=padding.MGF1(get_hash_func()), salt_length=padding.PSS.MAX_LENGTH
        )
    else:
        return padding.PKCS1v15()


def gen_challenge_str() -> str:
    return secrets.token_hex(config.config["challenge"]["challenge_str_len"])


def gen_token() -> str:
    return secrets.token_hex(config.config["challenge"]["token_len"])


def do_handshake(common_name: str) -> tuple[int, str]:
    index = get_index()
    if index is None:
        return 500, "Failed to load index"

    if common_name not in index:
        return 400, "Common_name not found"

    prefix = config.config["redis"]["key_prefix"]
    key = f"{ prefix }:{ common_name }:challenge-str"
    challenge_str = gen_challenge_str()

    if not redis_helper.set(
        key, challenge_str, config.config["challenge"]["handshake_timeout_after"]
    ):
        return 500, "Redis error"
    # it doesn't matter if a unverified handshake still exist
    # if it does, overwrite it

    return 200, challenge_str


def do_verify(common_name: str, signature: bytes) -> tuple[int, str]:
    index = get_index()
    if index is None:
        return 500, "Failed to load index"

    if common_name not in index:
        return 400, "Common_name not found"

    prefix = config.config["redis"]["key_prefix"]
    challenge_key = f"{ prefix }:{ common_name }:challenge-str"
    challenge_str = redis_helper.get(challenge_key)
    if challenge_str is None:
        return 400, "no handshake or timeout"

    pubkey_path = os.path.join(["challenge"]["pubkey_store_dir"], index["common_name"])
    if not os.path.exists(pubkey_path):
        return 500, "public key not found"

    with open(pubkey_path, "rb") as file:
        pubkey = serialization.load_pem_public_key(
            file.read(), backend=default_backend()
        )

    try:
        pubkey.verify(signature, challenge_str, get_hash_func(), get_hash_func())
    except:
        return 403, "failed to verify signature"

    token = gen_token()
    token_key = f"{ prefix }:token:{ token }"
    value = json.dumps(
        {
            "common_name": common_name,
            "verified_time_ts": int(datetime.now().timestamp()),
        }
    )
    if not redis_helper.set(
        token_key, value, config.config["challenge"]["token_expire_after"]
    ):
        return 500, "redis error"
    redis_helper.delete(challenge_key)

    return 200, token


def check_token_valid(token: str) -> tuple[int, str]:
    prefix = config.config["redis"]["key_prefix"]
    token_key = f"{ prefix }:token:{ token }"

    if not redis_helper.exists(token_key):
        return 404, "Token not found"
    
    return 200, "Token found"
