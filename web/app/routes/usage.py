from flask import Blueprint, jsonify

from app import glances

bp = Blueprint("usage", __name__)


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


@bp.route("/usage/all")
def usage_all():
    cpu_data = glances.get_cpu_data()
    mem_data = glances.get_mem_data()
    network_data = glances.get_network_data()
    if cpu_data is None:
        return (
            jsonify({"success": False, "msg": "Failed to get cpu data from glances"}),
            500,
        )
    elif mem_data is None:
        return (
            jsonify({"success": False, "msg": "Failed to get mem data from glances"}),
            500,
        )
    elif network_data is None:
        return (
            jsonify(
                {"success": False, "msg": "Failed to get network data from glances"}
            ),
            500,
        )

    return jsonify(
        {"success": True, "cpu": cpu_data, "mem": mem_data, "network": network_data}
    )
