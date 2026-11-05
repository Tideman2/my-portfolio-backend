import unittest

from extensions import db
from modules.skill.skill_model import ProfessionalSkill, TechnicalSkill
from modules.skill.skill_route import skill_bp
from tests.support import auth_headers, make_app


class SkillApiTest(unittest.TestCase):
    def setUp(self):
        self.app = make_app(skill_bp)
        self.client = self.app.test_client()
        self.headers = auth_headers(self.app)

    def test_get_professional_skills_is_public(self):
        with self.app.app_context():
            db.session.add(
                ProfessionalSkill(
                    name="Communication",
                    description="Explaining technical work to non-technical teammates",
                    proficiency=5,
                )
            )
            db.session.commit()

        response = self.client.get("/me/professional-skills")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [
                {
                    "id": 1,
                    "name": "Communication",
                    "description": "Explaining technical work to non-technical teammates",
                    "proficiency": 5,
                }
            ],
        )

    def test_get_technical_skills_is_public(self):
        with self.app.app_context():
            db.session.add(
                TechnicalSkill(
                    name="HTML/CSS",
                    description="Built responsive portfolio pages",
                    proficiency=4,
                )
            )
            db.session.commit()

        response = self.client.get("/me/technical-skills")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["name"], "HTML/CSS")

    def test_create_professional_skill_requires_authentication(self):
        response = self.client.post(
            "/me/professional-skills",
            json={"name": "Leadership", "description": "Led a team", "proficiency": 4},
        )

        self.assertEqual(response.status_code, 401)

    def test_create_technical_skill(self):
        response = self.client.post(
            "/me/technical-skills",
            json={
                "name": "Flask",
                "description": "Built and deployed this API",
                "proficiency": 4,
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "Flask")
        self.assertEqual(response.get_json()["proficiency"], 4)

    def test_create_skill_rejects_missing_description(self):
        response = self.client.post(
            "/me/technical-skills",
            json={"name": "Flask", "proficiency": 4},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.get_json()["errors"])

    def test_create_skill_rejects_proficiency_out_of_range(self):
        for proficiency in (0, 6):
            with self.subTest(proficiency=proficiency):
                response = self.client.post(
                    "/me/technical-skills",
                    json={
                        "name": "Flask",
                        "description": "Built this API",
                        "proficiency": proficiency,
                    },
                    headers=self.headers,
                )

                self.assertEqual(response.status_code, 400)
                self.assertIn("proficiency", response.get_json()["errors"])

    def test_patch_technical_skill(self):
        with self.app.app_context():
            skill = TechnicalSkill(
                name="HTML/CSS", description="Old description", proficiency=3
            )
            db.session.add(skill)
            db.session.commit()
            skill_id = skill.id

        response = self.client.patch(
            f"/me/technical-skills/{skill_id}",
            json={"proficiency": 5},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["proficiency"], 5)
        self.assertEqual(response.get_json()["description"], "Old description")

    def test_patch_skill_returns_404_for_unknown_id(self):
        response = self.client.patch(
            "/me/professional-skills/999",
            json={"proficiency": 2},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_professional_skill(self):
        with self.app.app_context():
            skill = ProfessionalSkill(
                name="Leadership", description="Led a team", proficiency=4
            )
            db.session.add(skill)
            db.session.commit()
            skill_id = skill.id

        response = self.client.delete(
            f"/me/professional-skills/{skill_id}", headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNone(db.session.get(ProfessionalSkill, skill_id))
