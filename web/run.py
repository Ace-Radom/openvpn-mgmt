import os

from app import challenge, config, create_app, profiles

app = create_app()
if config.config["app"]["is_production_env"]:
    app.config.update(DEBUG=False)
else:
    app.config.update(DEBUG=True)

profile_store_dir = config.config["profiles"]["store_dir"]
if not os.path.exists(profile_store_dir):
    os.makedirs(profile_store_dir)
if not os.path.isdir(profile_store_dir):
    raise RuntimeError("Profile store dir is not a directory")
profiles.sync_profile_store()

challenge.init()

if __name__ == "__main__":
    app.run()
