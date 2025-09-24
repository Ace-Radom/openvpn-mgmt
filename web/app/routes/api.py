from flask import (
    Blueprint,
    session,
    jsonify,
    request,
)
from app import db

bp = Blueprint("api", __name__)


@bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"success": False, "msg": "Username and password required"}), 400
    if db.user_exists(username):
        return jsonify({"success": False, "msg": "User already exists"}), 409
    if not db.add_user(username, password):
        return jsonify({"success": False, "msg": "DB error"}), 500
    session["allow_success"] = True
    return jsonify({"success": True, "msg": "Registration successful"})


@bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"success": False, "msg": "Username and password required"}), 400
    if not db.check_user_password(username, password):
        return jsonify({"success": False, "msg": "Username or password incorrect"}), 401
    session["username"] = username
    session["allow_success"] = True
    return jsonify({"success": True, "msg": "Login successful"})
