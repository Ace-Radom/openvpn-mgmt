from flask import (
    Blueprint,
    render_template,
    redirect,
    session,
    url_for,
    request,
)

bp = Blueprint("view", __name__)


@bp.route("/")
def index():
    if "username" in session:
        return redirect(url_for("view.user"))
    return redirect(url_for("view.login"))


@bp.route("/login")
def login():
    if "username" in session:
        return redirect(url_for("view.user"))
    return render_template("login.html")


@bp.route("/register")
def register():
    return render_template("register.html")


@bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("view.login"))


@bp.route("/user")
def user():
    if "username" not in session:
        return redirect(url_for("view.login"))
    return render_template("user.html", username=session["username"])


@bp.route("/success")
def success():
    if not session.pop("allow_success", None):
        return redirect(url_for("view.login"))
    msg = request.args.get("msg", "Operation Successful")
    next_url = request.args.get("next", "/")
    return render_template("success.html", msg=msg, next_url=next_url)


@bp.route("/error")
def error():
    if not session.pop("allow_error", None):
        return redirect(url_for("view.login"))
    msg = request.args.get("msg", "Operation Failed")
    next_url = request.args.get("next", "/")
    return render_template("error.html", msg=msg, next_url=next_url)
