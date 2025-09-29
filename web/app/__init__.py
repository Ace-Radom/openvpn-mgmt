from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes import api, verify, view

    app.register_blueprint(view.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(verify.bp)

    return app
