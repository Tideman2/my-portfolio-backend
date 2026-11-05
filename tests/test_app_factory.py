import os
import tempfile
import unittest
from unittest.mock import patch

import app as app_module
from extensions import db
from modules.profile.profile_model import Profile
from modules.user.user_model import User


class AppFactoryTest(unittest.TestCase):
    def test_create_app_survives_a_database_without_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            uri = f"sqlite:///{tmp}/empty.db"
            with patch.dict(os.environ, {"DATABASE_URI": uri}):
                application = app_module.create_app()

            self.assertEqual(application.name, "app")

    def test_create_app_seeds_admin_and_profile_once_tables_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            uri = f"sqlite:///{tmp}/seeded.db"
            with patch.dict(os.environ, {"DATABASE_URI": uri}):
                first = app_module.create_app()
                with first.app_context():
                    db.create_all()
                second = app_module.create_app()

            with second.app_context():
                self.assertIsNotNone(User.query.filter_by(username="Admin").first())
                self.assertIsNotNone(Profile.query.first())
