from flask import Blueprint, request, jsonify, current_app
from utils.jwt import generate_jwt_token
from datetime import datetime, timedelta
from modules.user.user_model import User
from modules.schemas.user_schema import UserSchema
from marshmallow import ValidationError
from decorators.jwt_required import jwt_required

auth_dp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_dp.route('/login', methods=["POST"])
def login_user():
    schema = UserSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    payload = {
        "sub": str(user.id),
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(seconds=current_app.config["JWT_EXPIRES_IN"])
    }

    token = generate_jwt_token(
        payload, current_app.config["JWT_ALGORITHM"], current_app.config["JWT_SECRET_KEY"])
    return jsonify({
        "access_token": token,
        "user": user.get_user_identity()
    }), 200


@auth_dp.route('/verify', methods=["POST"])
@jwt_required
def verify_token():

    return jsonify({
        "verified": True
    })
