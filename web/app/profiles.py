import hashlib
import os
import re
import shutil
import threading

from app import config

lock = threading.RLock()


def get_hash_worker():
    return hashlib.new(config.config["profiles"]["hash"])


def list_profiles(path: str) -> list:
    profiles = []
    for files in os.listdir(path):
        for file in files:
            filename, ext = os.path.splitext(file)
            if ext == ".ovpn" and re.match(r"^[A-Z][a-z]*$", filename):
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
            lines.append(config.config["profiles"]["hash"])
            for index in index_list:
                filename = index["filename"]
                hash = index["hash"]
                lines.append(f"{filename} {hash}")

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
