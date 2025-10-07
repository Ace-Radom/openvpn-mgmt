from flask import Blueprint, jsonify, request

from app import glances

bp = Blueprint("main", __name__)


@bp.route("/usage/cpu")
def usage_cpu():
    data = glances.get_cpu_data()
    if data is None:
        return (
            jsonify({"success": False, "msg": "Failed to get cpu data from glances"}),
            500,
        )

    return jsonify({"success": True, "data": data})


@bp.route("/usage/mem")
def usage_mem():
    data = glances.get_mem_data()
    if data is None:
        return (
            jsonify({"success": False, "msg": "Failed to get mem data from glances"}),
            500,
        )

    return jsonify({"success": True, "data": data})


@bp.route("/usage/network")
def usage_network():
    data = glances.get_network_data()
    if data is None:
        return (
            jsonify(
                {"success": False, "msg": "Failed to get network data from glances"}
            ),
            500,
        )

    return jsonify({"success": True, "data": data})
