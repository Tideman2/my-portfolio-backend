import unittest

from extensions import db
from modules.user.user_model import User
from modules.user.user_route import auth_dp
from tests.support import make_app


class AuthApiTest(unittest.TestCase):
    def setUp(self):
        self.app = make_app(auth_dp)
        self.client = self.app.test_client()
        with self.app.app_context():
            user = User(username="Admin")
            user.set_password("secret123")
            db.session.add(user)
            db.session.commit()

    def test_register_endpoint_is_removed(self):
        response = self.client.post(
            "/api/auth/register",
            json={"username": "intruder", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 404)

    def test_login_still_returns_a_token(self):
        response = self.client.post(
            "/api/auth/login",
            json={"username": "Admin", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            "/api/auth/login",
            json={"username": "Admin", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 401)

    def test_login_rejects_missing_fields(self):
        response = self.client.post("/api/auth/login", json={})

        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.get_json())
