from datetime import date

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from decorators.jwt_required import jwt_required
from extensions import db
from modules.profile.profile_model import Profile, Social
from modules.schemas.profile_schema import ProfileSchema, SocialSchema

profile_bp = Blueprint("profile", __name__, url_prefix="/me")


def calculate_age(date_of_birth):
    if not date_of_birth:
        return None
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


def serialize_profile(profile):
    return {
        "name": profile.name,
        "date_of_birth": (
            profile.date_of_birth.isoformat() if profile.date_of_birth else None
        ),
        "age": calculate_age(profile.date_of_birth),
        "country": profile.country,
        "bio": profile.bio,
    }


def serialize_social(social):
    return {
        "id": social.id,
        "platform_name": social.platform_name,
        "url": social.url,
    }


@profile_bp.route("", methods=["GET"], strict_slashes=False)
def get_me():
    profile = Profile.query.first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(serialize_profile(profile))


@profile_bp.route("", methods=["PATCH"], strict_slashes=False)
@jwt_required
def update_me():
    profile = Profile.query.first()
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    schema = ProfileSchema()
    try:
        data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for field, value in data.items():
        setattr(profile, field, value)
    db.session.commit()
    return jsonify(serialize_profile(profile))


@profile_bp.route("/socials", methods=["GET"])
def get_socials():
    socials = Social.query.order_by(Social.id).all()
    return jsonify([serialize_social(social) for social in socials])


@profile_bp.route("/socials", methods=["POST"])
@jwt_required
def create_social():
    schema = SocialSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    social = Social(**data)
    db.session.add(social)
    db.session.commit()
    return jsonify(serialize_social(social)), 201


@profile_bp.route("/socials/<int:id>", methods=["PATCH"])
@jwt_required
def update_social(id):
    social = db.session.get(Social, id)
    if not social:
        return jsonify({"error": "Social not found"}), 404

    schema = SocialSchema()
    try:
        data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for field, value in data.items():
        setattr(social, field, value)
    db.session.commit()
    return jsonify(serialize_social(social))


@profile_bp.route("/socials/<int:id>", methods=["DELETE"])
@jwt_required
def delete_social(id):
    social = db.session.get(Social, id)
    if not social:
        return jsonify({"error": "Social not found"}), 404

    db.session.delete(social)
    db.session.commit()
    return jsonify({"message": "Social deleted"}), 200
