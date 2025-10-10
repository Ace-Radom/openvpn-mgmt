import re

from flask import Blueprint, jsonify, request

from app import config, profiles

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


@bp.route("/profiles/maxperusr")
def profile_maxperusr():
    return jsonify(
        {
            "success": True,
            "data": {"max_per_user": config.config["profiles"]["max_per_user"]},
        }
    )


@bp.route("/profiles/exist", methods=["POST"])
def profile_exist():
    data = request.json
    cn = data["common_name"]
    if not cn:
        return jsonify({"success": False, "msg": "Common_name required"}), 400

    return jsonify({"success": True, "data": {"exist": profiles.profile_exists(cn)}})


@bp.route("/profiles/add", methods=["POST"])
def profiles_add():
    data = request.json
    username = data["username"]
    cn = data["common_name"]
    if not username or not cn:
        return (
            jsonify({"success": False, "msg": "Username and common_name required"}),
            400,
        )
    if not re.match(r"^[A-Z][a-z]*$", username):
        return jsonify({"success": False, "msg": "Illegal username"}), 400
    if username not in cn or not re.match(r"^[A-Z][a-z]*-[0-9]+$", cn):
        return jsonify({"success": False, "msg": "Illegal common_name"}), 400
    if (
        profiles.count_user_profiles(username)
        >= config.config["profiles"]["max_per_user"]
    ):
        return (
            jsonify({"success": False, "msg": "User reached max_per_user limit"}),
            400,
        )
    if profiles.profile_exists(cn):
        return jsonify({"success": False, "msg": "Common_name exists"}), 400

    if not profiles.add_profile(cn):
        return jsonify({"success": False, "msg": "Failed to add new profile"}), 500

    return jsonify({"success": True})
