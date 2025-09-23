import os

from app import config, create_app

base_dir = os.path.split(os.path.realpath(__file__))[0]
config.parse_config(os.path.join(base_dir, "web.cfg"))

app = create_app()
if config.cfg["app"]["is_production_env"]:
    app.config.from_object("app.config.production_config")
else:
    app.config.from_object("app.config.debug_config")

if __name__ == "__main__":
    app.run()
