import jwt
from flask import Blueprint, request, jsonify, current_app
from utils.jwt import generate_jwt_token
from datetime import datetime, timedelta
from extensions import db
from modules.user.user_model import User
from modules.schemas.user_schema import UserSchema
from marshmallow import ValidationError
from decorators.jwt_required import jwt_required

auth_dp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_dp.route('/register', methods=["POST"])
def register_user():
    try:
        schema = UserSchema()
        data = schema.load(request.get_json())
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing fields"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


@auth_dp.route('/login', methods=["POST"])
def login_user():
    schema = UserSchema()
    data = schema.load(request.get_json())
    username = data.get("username")
    password = data.get("password")
    print(username, password)
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
    print(token)
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
