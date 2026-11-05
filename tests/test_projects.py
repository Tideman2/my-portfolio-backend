import unittest
from io import BytesIO
from unittest.mock import patch

from extensions import db
from modules.project.project_model import Project
from modules.project.project_route import project_bp
from modules.project_group.project_group_model import ProjectGroup
from modules.project_group.project_group_route import project_group_bp
from tests.support import auth_headers, make_app


class ProjectApiTest(unittest.TestCase):
    def setUp(self):
        self.app = make_app(project_bp, project_group_bp)
        self.client = self.app.test_client()
        self.headers = auth_headers(self.app)
        with self.app.app_context():
            solo = ProjectGroup(name="Solo", slug="solo")
            collab = ProjectGroup(name="Collab", slug="collab")
            db.session.add_all([solo, collab])
            db.session.commit()
            self.solo_id = solo.id
            self.collab_id = collab.id

    def create_project(self, group_id, title="Portfolio API"):
        return self.client.post(
            "/api/projects/",
            data={
                "title": title,
                "stack": "Flask, MySQL",
                "goal": "Serve portfolio data",
                "github_url": "https://github.com/roland/portfolio",
                "demo_url": "https://example.com",
                "group_id": str(group_id),
            },
            headers=self.headers,
        )

    def test_create_project_requires_a_group(self):
        response = self.client.post(
            "/api/projects/",
            data={
                "title": "No group",
                "stack": "Flask",
                "goal": "Test",
                "github_url": "https://example.com",
                "demo_url": "https://example.com",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("group_id", response.get_json()["errors"])

    def test_create_project_with_unknown_group_returns_400(self):
        response = self.create_project(999)

        self.assertEqual(response.status_code, 400)

    def test_create_project_with_group(self):
        response = self.create_project(self.solo_id)

        self.assertEqual(response.status_code, 201)
        with self.app.app_context():
            project = Project.query.one()
            self.assertEqual(project.group_id, self.solo_id)

    def test_get_projects_keeps_the_existing_response_shape(self):
        self.create_project(self.solo_id)

        response = self.client.get("/api/projects/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.get_json()[0].keys()),
            {"id", "title", "image", "stack", "goal", "github_url", "demo_url"},
        )

    def test_get_projects_filtered_by_group_id(self):
        self.create_project(self.solo_id, title="Solo project")
        self.create_project(self.collab_id, title="Collab project")

        response = self.client.get(f"/api/projects/?group_id={self.collab_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([p["title"] for p in response.get_json()], ["Collab project"])

    def test_get_projects_filtered_by_group_slug(self):
        self.create_project(self.solo_id, title="Solo project")
        self.create_project(self.collab_id, title="Collab project")

        response = self.client.get("/api/projects/?group=collab")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([p["title"] for p in response.get_json()], ["Collab project"])

    def test_get_projects_with_unknown_group_returns_404(self):
        response = self.client.get("/api/projects/?group=missing")

        self.assertEqual(response.status_code, 404)

    def project_id(self):
        with self.app.app_context():
            return Project.query.one().id

    def test_patch_project_requires_authentication(self):
        self.create_project(self.solo_id)

        response = self.client.patch(
            f"/api/projects/{self.project_id()}", data={"title": "Hacked"}
        )

        self.assertEqual(response.status_code, 401)

    def test_patch_project_updates_supplied_fields(self):
        self.create_project(self.solo_id)

        response = self.client.patch(
            f"/api/projects/{self.project_id()}",
            data={"title": "Updated title", "goal": "Updated goal"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            project = Project.query.one()
            self.assertEqual(project.title, "Updated title")
            self.assertEqual(project.goal, "Updated goal")
            self.assertEqual(project.stack, "Flask, MySQL")

    def test_patch_project_moves_it_to_another_group(self):
        self.create_project(self.solo_id)

        response = self.client.patch(
            f"/api/projects/{self.project_id()}",
            data={"group_id": str(self.collab_id)},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(Project.query.one().group_id, self.collab_id)

    def test_patch_project_rejects_unknown_group(self):
        self.create_project(self.solo_id)

        response = self.client.patch(
            f"/api/projects/{self.project_id()}",
            data={"group_id": "999"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)

    def test_patch_project_accepts_json(self):
        self.create_project(self.solo_id)

        response = self.client.patch(
            f"/api/projects/{self.project_id()}",
            json={"title": "JSON title"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(Project.query.one().title, "JSON title")

    def test_patch_project_rejects_an_empty_payload(self):
        self.create_project(self.solo_id)

        response = self.client.patch(
            f"/api/projects/{self.project_id()}", json={}, headers=self.headers
        )

        self.assertEqual(response.status_code, 400)

    def test_patch_project_returns_404_for_unknown_id(self):
        response = self.client.patch(
            "/api/projects/999", data={"title": "Missing"}, headers=self.headers
        )

        self.assertEqual(response.status_code, 404)

    def test_patch_project_replaces_the_image_and_removes_the_old_one(self):
        self.create_project(self.solo_id)
        with self.app.app_context():
            project = Project.query.one()
            project.image = "https://old.example/image.png"
            project.image_public_id = "old-public-id"
            db.session.commit()

        uploader = patch(
            "modules.project.project_route.uploadImage",
            return_value=("https://new.example/image.png", "new-public-id"),
        )
        destroyer = patch("modules.project.project_route.cloudinary.uploader.destroy")
        with uploader, destroyer as destroy:
            response = self.client.patch(
                f"/api/projects/{self.project_id()}",
                data={"image": (BytesIO(b"image-bytes"), "new.png")},
                content_type="multipart/form-data",
                headers=self.headers,
            )

        self.assertEqual(response.status_code, 200)
        destroy.assert_called_once_with("old-public-id")
        with self.app.app_context():
            project = Project.query.one()
            self.assertEqual(project.image, "https://new.example/image.png")
            self.assertEqual(project.image_public_id, "new-public-id")
