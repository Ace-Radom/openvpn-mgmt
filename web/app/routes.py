from flask import (
    Blueprint,
    render_template,
    redirect,
    session,
    url_for,
    jsonify,
    request,
)
from .db import user_exists, add_user, check_user_password

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if "username" in session:
        return redirect(url_for("main.user"))
    return redirect(url_for("main.login"))


@bp.route("/login")
def login():
    if "username" in session:
        return redirect(url_for("main.user"))
    return render_template("login.html")


@bp.route("/register")
def register():
    return render_template("register.html")


@bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"success": False, "msg": "Username and password required"}), 400
    if user_exists(username):
        return jsonify({"success": False, "msg": "User already exists"}), 409
    add_user(username, password)
    session["allow_success"] = True
    return jsonify({"success": True, "msg": "Registration successful"})


@bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"success": False, "msg": "Username and password required"}), 400
    if not check_user_password(username, password):
        return jsonify({"success": False, "msg": "Username or password incorrect"}), 401
    session["username"] = username
    session["allow_success"] = True
    return jsonify({"success": True, "msg": "Login successful"})


@bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main.login"))


@bp.route("/user")
def user():
    if "username" not in session:
        return redirect(url_for("main.login"))
    return render_template("user.html", username=session["username"])


@bp.route("/success")
def success():
    if not session.pop("allow_success", None):
        return redirect(url_for("main.login"))
    msg = request.args.get("msg", "Operation Successful")
    next_url = request.args.get("next", "/")
    return render_template("success.html", msg=msg, next_url=next_url)
