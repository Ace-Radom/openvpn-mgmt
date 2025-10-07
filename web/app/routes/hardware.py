from flask import Blueprint, jsonify

from app import glances

bp = Blueprint("hardware", __name__)


@bp.route("/hardware/cpu")
def hardware_cpu():
    data = glances.get_cpu_hardware_data()
    if data is None:
        return (
            jsonify(
                {
                    "success": False,
                    "msg": "Failed to get cpu hardware data from glances",
                }
            ),
            500,
        )

    return jsonify({"success": True, "data": data})


@bp.route("/hardware/uptime")
def hardware_uptime():
    data = glances.get_uptime_data()
    if data is None:
        return (
            jsonify(
                {"success": False, "msg": "Failed to get uptime data from glances"}
            ),
            500,
        )

    return jsonify({"success": True, "data": data})
