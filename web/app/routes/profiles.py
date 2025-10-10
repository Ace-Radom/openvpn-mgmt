from flask import Blueprint, jsonify

from app import profiles

bp = Blueprint("profiles", __name__)


@bp.route("/profiles/list")
def profiles_list():
    data = profiles.get_stored_profile_index()
    if data is None:
        return (
            jsonify(
                {"success": False, "msg": "Failed to read cached profile index data"}
            ),
            500,
        )

    return jsonify({"success": True, "data": data})
