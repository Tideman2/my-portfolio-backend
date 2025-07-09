import jwt
from utils.jwt import decode_jwt_token
from flask import request, jsonify, current_app
from functools import wraps


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        try:
            decoded = decode_jwt_token(
                token,
                current_app.config["JWT_ALGORITHM"],
                current_app.config["JWT_SECRET_KEY"]
            )
            request.user = decoded  # attach decoded user data to the request
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403

        return f(*args, **kwargs)

    return decorated
