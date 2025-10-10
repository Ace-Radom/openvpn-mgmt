from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes import hardware, profiles, usage

    app.register_blueprint(hardware.bp)
    app.register_blueprint(profiles.bp)
    app.register_blueprint(usage.bp)

    return app
