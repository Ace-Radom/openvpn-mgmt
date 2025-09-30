from flask import Blueprint, redirect, url_for, session

from app import db, utils
from app.email import gmail

bp = Blueprint("verify", __name__)


@bp.route("/verify/user/<token>")
def verify_user(token: str):
    if not db.verify_token_exists(token):
        session["allow_error"] = True
        return redirect(
            url_for("view.error", msg="验证失败", next_url=url_for("view.login"))
        )
    # invalid token

    user_data = db.get_not_verified_user_data_with_verify_token(token)
    if "username" not in user_data or "email" not in user_data:
        session["allow_error"] = True
        return redirect(
            url_for("view.error", msg="验证失败", next_url=url_for("view.login"))
        )
    # failed to get user data

    if not db.verify_user(token):
        session["allow_error"] = True
        return redirect(
            url_for("view.error", msg="验证失败", next_url=url_for("view.login"))
        )
    # failed to verify user (db error)

    try:
        gmail.send_email(
            user_data["email"],
            "您的账户已被激活 - OpenVPN Mgmt",
            "welcome_zhCN.html",
            {
                "username": user_data["username"],
                "login_url": utils.build_server_link("login", is_public_link=True),
            },
        )
    except:
        pass

    session["allow_success"] = True
    return redirect(url_for("view.success", msg="验证成功", next_url=url_for("view.login")))
