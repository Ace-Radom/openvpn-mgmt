from flask import (
    Blueprint,
    session,
    jsonify,
    request,
)

from app import db, utils
from app.email import gmail

bp = Blueprint("api", __name__)


@bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password or not email:
        return (
            jsonify(
                {"success": False, "msg": "Username, password and email are required"}
            ),
            400,
        )
    if db.user_exists(username):
        return jsonify({"success": False, "msg": "User already exists"}), 409
    verify_token = db.add_user_not_verified(username, password, email)
    if verify_token is None:
        return jsonify({"success": False, "msg": "DB error"}), 500

    try:
        gmail.send_email(
            email,
            "验证您的邮箱 - OpenVPN Mgmt",
            "verify_zhCN.html",
            {
                "username": username,
                "verify_url": utils.build_server_link(
                    f"verify/user/{ verify_token }", is_public_link=True
                ),
            },
        )
    except:
        return jsonify({"success": False, "msg": "Failed to send verify email"}), 500

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
