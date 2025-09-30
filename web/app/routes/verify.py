from flask import Blueprint, redirect, url_for, session

from app import db

bp = Blueprint("verify", __name__)


@bp.route("/verify/user/<token>")
def verify_user(token: str):
    if not db.verify_token_exists(token):
        session["allow_error"] = True
        return redirect(
            url_for("view.error", msg="验证失败", next_url=url_for("view.login"))
        )

    if not db.verify_user(token):
        session["allow_error"] = True
        return redirect(
            url_for("view.error", msg="验证失败", next_url=url_for("view.login"))
        )
    else:
        session["allow_success"] = True
        return redirect(
            url_for("view.success", msg="验证成功", next_url=url_for("view.login"))
        )
