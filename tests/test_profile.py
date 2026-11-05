import unittest
from datetime import date

from extensions import db
from modules.profile.profile_model import Profile, Social
from modules.profile.profile_route import profile_bp
from tests.support import auth_headers, make_app


def expected_age(date_of_birth):
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


class ProfileApiTest(unittest.TestCase):
    def setUp(self):
        self.app = make_app(profile_bp)
        self.client = self.app.test_client()
        self.headers = auth_headers(self.app)
        with self.app.app_context():
            db.session.add(
                Profile(
                    name="Roland",
                    date_of_birth=date(2000, 1, 1),
                    country="Ghana",
                    bio="Builder",
                )
            )
            db.session.commit()

    def test_get_me_returns_profile_with_computed_age(self):
        response = self.client.get("/me")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "Roland")
        self.assertEqual(data["date_of_birth"], "2000-01-01")
        self.assertEqual(data["country"], "Ghana")
        self.assertEqual(data["bio"], "Builder")
        self.assertEqual(data["age"], expected_age(date(2000, 1, 1)))

    def test_patch_me_requires_authentication(self):
        response = self.client.patch("/me", json={"bio": "New bio"})

        self.assertEqual(response.status_code, 401)

    def test_patch_me_updates_only_the_supplied_fields(self):
        response = self.client.patch(
            "/me", json={"bio": "New bio"}, headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["bio"], "New bio")
        self.assertEqual(data["name"], "Roland")
        self.assertEqual(data["country"], "Ghana")

    def test_patch_me_rejects_invalid_date(self):
        response = self.client.patch(
            "/me", json={"date_of_birth": "not-a-date"}, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("date_of_birth", response.get_json()["errors"])

    def test_get_socials_returns_platform_and_url(self):
        with self.app.app_context():
            db.session.add(Social(platform_name="LinkedIn", url="https://linkedin.com/in/roland"))
            db.session.commit()

        response = self.client.get("/me/socials")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [{"id": 1, "platform_name": "LinkedIn", "url": "https://linkedin.com/in/roland"}],
        )

    def test_create_social_requires_authentication(self):
        response = self.client.post(
            "/me/socials", json={"platform_name": "GitHub", "url": "https://github.com/roland"}
        )

        self.assertEqual(response.status_code, 401)

    def test_create_social(self):
        response = self.client.post(
            "/me/socials",
            json={"platform_name": "GitHub", "url": "https://github.com/roland"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["platform_name"], "GitHub")

    def test_create_social_rejects_missing_fields(self):
        response = self.client.post(
            "/me/socials", json={"platform_name": "GitHub"}, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("url", response.get_json()["errors"])

    def test_patch_social(self):
        with self.app.app_context():
            social = Social(platform_name="GitHub", url="https://github.com/roland")
            db.session.add(social)
            db.session.commit()
            social_id = social.id

        response = self.client.patch(
            f"/me/socials/{social_id}",
            json={"url": "https://github.com/roland-dev"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["url"], "https://github.com/roland-dev")

    def test_patch_social_returns_404_for_unknown_id(self):
        response = self.client.patch(
            "/me/socials/999", json={"url": "https://example.com"}, headers=self.headers
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_social(self):
        with self.app.app_context():
            social = Social(platform_name="GitHub", url="https://github.com/roland")
            db.session.add(social)
            db.session.commit()
            social_id = social.id

        response = self.client.delete(f"/me/socials/{social_id}", headers=self.headers)

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Social, social_id))
