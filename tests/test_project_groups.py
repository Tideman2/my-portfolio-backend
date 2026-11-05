import unittest

from extensions import db
from modules.project.project_model import Project
from modules.project_group.project_group_model import ProjectGroup
from modules.project_group.project_group_route import project_group_bp
from tests.support import auth_headers, make_app


class ProjectGroupApiTest(unittest.TestCase):
    def setUp(self):
        self.app = make_app(project_group_bp)
        self.client = self.app.test_client()
        self.headers = auth_headers(self.app)

    def test_get_groups_is_public(self):
        with self.app.app_context():
            db.session.add(ProjectGroup(name="Solo", slug="solo"))
            db.session.commit()

        response = self.client.get("/api/project-groups")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"id": 1, "name": "Solo", "slug": "solo"}])

    def test_create_group_requires_authentication(self):
        response = self.client.post("/api/project-groups", json={"name": "Collab"})

        self.assertEqual(response.status_code, 401)

    def test_create_group_generates_slug(self):
        response = self.client.post(
            "/api/project-groups",
            json={"name": "Open Source Collaborations"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Open Source Collaborations")
        self.assertEqual(data["slug"], "open-source-collaborations")

    def test_create_group_rejects_missing_name(self):
        response = self.client.post(
            "/api/project-groups", json={}, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.get_json()["errors"])

    def test_create_group_rejects_duplicate_name(self):
        with self.app.app_context():
            db.session.add(ProjectGroup(name="Solo", slug="solo"))
            db.session.commit()

        response = self.client.post(
            "/api/project-groups", json={"name": "Solo"}, headers=self.headers
        )

        self.assertEqual(response.status_code, 409)

    def test_rename_group_keeps_its_slug(self):
        with self.app.app_context():
            group = ProjectGroup(name="Collab", slug="collab")
            db.session.add(group)
            db.session.commit()
            group_id = group.id

        response = self.client.patch(
            f"/api/project-groups/{group_id}",
            json={"name": "Collaboration"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Collaboration")
        self.assertEqual(response.get_json()["slug"], "collab")

    def test_rename_group_returns_409_for_duplicate_name(self):
        with self.app.app_context():
            db.session.add(ProjectGroup(name="Solo", slug="solo"))
            db.session.add(ProjectGroup(name="Collab", slug="collab"))
            db.session.commit()
            collab = ProjectGroup.query.filter_by(name="Collab").first()
            collab_id = collab.id

        response = self.client.patch(
            f"/api/project-groups/{collab_id}",
            json={"name": "Solo"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 409)

    def test_delete_empty_group(self):
        with self.app.app_context():
            group = ProjectGroup(name="Solo", slug="solo")
            db.session.add(group)
            db.session.commit()
            group_id = group.id

        response = self.client.delete(
            f"/api/project-groups/{group_id}", headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertIsNone(db.session.get(ProjectGroup, group_id))

    def test_delete_group_returns_404_for_unknown_id(self):
        response = self.client.delete("/api/project-groups/999", headers=self.headers)

        self.assertEqual(response.status_code, 404)

    def test_delete_group_with_projects_returns_409(self):
        with self.app.app_context():
            group = ProjectGroup(name="Solo", slug="solo")
            db.session.add(group)
            db.session.commit()
            db.session.add(
                Project(
                    title="Portfolio API",
                    stack="Flask",
                    goal="Serve data",
                    github_url="https://example.com",
                    demo_url="https://example.com",
                    group_id=group.id,
                )
            )
            db.session.commit()
            group_id = group.id

        response = self.client.delete(
            f"/api/project-groups/{group_id}", headers=self.headers
        )

        self.assertEqual(response.status_code, 409)
        with self.app.app_context():
            self.assertIsNotNone(db.session.get(ProjectGroup, group_id))
