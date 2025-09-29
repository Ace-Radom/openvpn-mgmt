import os

from app import config, create_app, db
from app.email import gmail

base_dir = os.path.split(os.path.realpath(__file__))[0]
config.parse_config(os.path.join(base_dir, "web.cfg"))
if config.config["app"]["secret_key"] is None:
    raise RuntimeError("Secret key cannot be None")

app = create_app()
app.secret_key = config.config["app"]["secret_key"]
app.config.from_object("app.config.flask_config")
if config.config["app"]["is_production_env"]:
    app.config.update(DEBUG=False, SESSION_COOKIE_SECURE=True)
else:
    app.config.update(DEBUG=True)

if not db.init_db():
    raise RuntimeError("Init DB failed")

gmail.fetch_gmail_discovery()
gmail.auth_gmail_api()
gmail.secure_gmail_related_files()

if __name__ == "__main__":
    app.run()
