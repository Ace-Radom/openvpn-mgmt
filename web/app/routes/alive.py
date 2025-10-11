from flask import Blueprint, jsonify

bp = Blueprint("alive", __name__)


@bp.route("/alive")
def alive():
    return jsonify({"success": True, "data": {"msg": "openvpn-mgmt"}})
