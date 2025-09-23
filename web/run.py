import os

from app import config, create_app

base_dir = os.path.split(os.path.realpath(__file__))[0]
config.parse_config(os.path.join(base_dir, "web.cfg"))
if config.cfg["app"]["secret_key"] is None:
    raise RuntimeError("Secret key cannot be None")

app = create_app()
app.secret_key = config.cfg["app"]["secret_key"]
app.config.from_object("app.config.config")
if config.cfg["app"]["is_production_env"]:
    app.config.update(DEBUG=False, SESSION_COOKIE_SECURE=True)
else:
    app.config.update(DEBUG=True)

if __name__ == "__main__":
    app.run()
