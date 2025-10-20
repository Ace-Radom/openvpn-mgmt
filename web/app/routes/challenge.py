import base64
from datetime import datetime
from flask import Blueprint, jsonify, request

from app import challenge, config

bp = Blueprint("challenge", __name__)


@bp.route("/challenge/handshake", methods=["POST"])
def challenge_handshake():
    data = request.json
    cn = data.get("common_name")
    if not cn:
        return jsonify({"success": False, "msg": "Common_name required"}), 400

    status_code, msg = challenge.do_handshake(cn)
    if status_code != 200:
        return jsonify({"success": False, "msg": msg}), status_code

    return jsonify(
        {
            "success": True,
            "data": {
                "challenge_str": msg,
                "use_pss": config.config["challenge"]["use_pss"],
                "hash": config.config["challenge"]["hash"],
                "timeout_after_ts": int(datetime.now().timestamp())
                + config.config["challenge"]["handshake_timeout_after"],
            },
        }
    )


@bp.route("/challenge/verify", methods=["POST"])
def challenge_verify():
    data = request.json
    cn = data.get("common_name")
    signature_base64 = data.get("signature")
    if not cn or not signature_base64:
        return (
            jsonify({"success": False, "msg": "Common_name and signature required"}),
            400,
        )

    try:
        signature = base64.b64decode(signature_base64)
    except:
        return (
            jsonify({"success": False, "msg": "Illegal base64 encoded signature"}),
            400,
        )

    status_code, msg = challenge.do_verify(cn, signature)
    if status_code != 200:
        return jsonify({"success": False, "msg": msg}), status_code

    return jsonify(
        {
            "success": True,
            "data": {
                "token": msg,
                "expired_time_ts": int(datetime.now().timestamp())
                + config.config["challenge"]["token_expire_after"],
            },
        }
    )


@bp.route("/challenge/valid", methods=["POST"])
def challenge_valid():
    data = request.json
    token = data.get("token")
    if not token:
        return jsonify({"success": False, "msg": "Token required"}), 400
    
    status_code, msg = challenge.check_token_valid(token)
    if status_code != 200:
        return jsonify({"success": False, "msg": msg}), status_code
    
    return jsonify({"success": True, "msg": "Token found"})
