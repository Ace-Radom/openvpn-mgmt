import hashlib
import os
import re
import subprocess
import shutil
import threading

from app import config

lock = threading.RLock()


def get_hash_worker():
    return hashlib.new(config.config["profiles"]["hash"])


def list_profiles(path: str) -> list:
    profiles = []
    for file in os.listdir(path):
        filename, ext = os.path.splitext(file)
        if ext == ".ovpn" and re.match(r"^[A-Z][a-z]*-[0-9]+$", filename):
            profiles.append(file)

    return profiles


def get_stored_profile_index() -> dict | None:
    with lock:
        with open(
            os.path.join(config.config["profiles"]["store_dir"], "index.txt"),
            "r",
            encoding="utf-8",
        ) as file:
            lines = file.readlines()

        hash = None
        profiles = []
        for line in lines:
            line = line.strip()
            if hash is None:
                hash = line
                continue
            subline = line.split(" ")
            profiles.append({"filename": subline[0], "hash": subline[1]})

        if hash is None:
            return None

        return {"hash": hash, "profiles": profiles}


def update_stored_profile_index() -> None:
    with lock:
        store_dir = config.config["profiles"]["store_dir"]
        stored_profiles = list_profiles(store_dir)

        index_list = []
        for profile in stored_profiles:
            hasher = get_hash_worker()
            with open(os.path.join(store_dir, profile), "rb") as file:
                for chunk in iter(lambda: file.read(1024), b""):
                    hasher.update(chunk)
            index_list.append({"filename": profile, "hash": hasher.hexdigest()})

        with open(os.path.join(store_dir, "index.txt"), "w", encoding="utf-8") as file:
            lines = []
            lines.append(config.config["profiles"]["hash"] + "\n")
            for index in index_list:
                filename = index["filename"]
                hash = index["hash"]
                lines.append(f"{filename} {hash}\n")

            file.writelines(lines)


def sync_profile_store() -> None:
    with lock:
        src_dir = config.config["profiles"]["generate_dir"]
        target_dir = config.config["profiles"]["store_dir"]

        src_profiles = list_profiles(src_dir)
        target_profiles = list_profiles(target_dir)

        new_profiles = [
            profile for profile in src_profiles if profile not in target_profiles
        ]
        # only copy these profiles which doesn't exist under store dir
        # if one profile has already been copied, it won't be checked again
        # since store dir shouldn't be changed manually

        if len(new_profiles) == 0:
            return

        for profile in new_profiles:
            shutil.copy(
                os.path.join(src_dir, profile), os.path.join(target_dir, profile)
            )

        update_stored_profile_index()


def count_user_profiles(username: str) -> int:
    with lock:
        index = get_stored_profile_index()
        if index is None:
            return -1

        profiles = index["profiles"]
        count = 0
        for profile in profiles:
            if username in profile["filename"]:
                count += 1

        return count


def profile_exists(cn: str) -> bool:
    with lock:
        return os.path.exists(f"/etc/openvpn/server/easy-rsa/pki/issued/{ cn }.crt")
    # See: openvpn-install.sh:L451


def add_profile(cn: str) -> bool:
    if profile_exists(cn):
        return False

    proc = subprocess.run(
        ["python3", config.config["app"]["mgmt_path"], "clients", "--add", cn],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    ret = proc.returncode
    if ret != 0:
        return False

    sync_profile_store()
    return True
