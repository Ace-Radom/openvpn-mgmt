from app import config, create_app, profiles

app = create_app()
if config.config["app"]["is_production_env"]:
    app.config.update(DEBUG=False)
else:
    app.config.update(DEBUG=True)

profiles.sync_profile_store()

if __name__ == "__main__":
    app.run()
