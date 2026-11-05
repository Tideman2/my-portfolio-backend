from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask

from extensions import db


def make_app(*blueprints):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY="test-secret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRES_IN=3600,
    )
    db.init_app(app)
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    with app.app_context():
        db.create_all()
    return app


def auth_headers(app):
    payload = {
        "sub": "1",
        "username": "Admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(
        payload,
        app.config["JWT_SECRET_KEY"],
        algorithm=app.config["JWT_ALGORITHM"],
    )
    return {"Authorization": f"Bearer {token}"}
