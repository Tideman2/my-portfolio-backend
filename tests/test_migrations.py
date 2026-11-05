import io
import logging
import unittest
import warnings
from contextlib import redirect_stdout

from flask import Flask
from flask_migrate import Migrate, downgrade, upgrade

from extensions import db
from modules.profile.profile_model import Profile, Social
from modules.project.project_model import Project
from modules.project_group.project_group_model import ProjectGroup
from modules.skill.skill_model import ProfessionalSkill, TechnicalSkill
from modules.user.user_model import User


class MigrationTest(unittest.TestCase):
    def test_migration_chain_generates_mysql_sql_offline(self):
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "mysql+pymysql://user:pass@localhost/portfolio"
        )
        db.init_app(app)
        Migrate(app, db)

        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)

        with warnings.catch_warnings(), app.app_context():
            warnings.simplefilter("ignore")

            with redirect_stdout(io.StringIO()) as output:
                upgrade(directory="migrations", sql=True)

            with redirect_stdout(io.StringIO()) as downgrade_output:
                downgrade(directory="migrations", revision="head:base", sql=True)

        sql = output.getvalue()
        self.assertIn("CREATE TABLE project_group", sql)
        self.assertIn(
            "INSERT INTO project_group (name, slug) VALUES ('Uncategorized', 'uncategorized')",
            sql,
        )
        self.assertIn(
            "INSERT INTO profile (name, date_of_birth, country, bio) "
            "VALUES (NULL, NULL, NULL, NULL)",
            sql,
        )
        self.assertIn("ALTER TABLE project ADD COLUMN group_id", sql)
        self.assertIn(
            "UPDATE project SET group_id = ("
            "SELECT id FROM project_group WHERE slug = 'uncategorized'"
            ")",
            sql,
        )
        self.assertIn("FOREIGN KEY(group_id) REFERENCES project_group (id)", sql)
        self.assertIn("MODIFY title VARCHAR(150)", sql)
        self.assertIn("MODIFY image VARCHAR(500)", sql)
        self.assertIn("MODIFY stack VARCHAR(255)", sql)
        self.assertIn("MODIFY goal TEXT", sql)
        self.assertIn("MODIFY github_url VARCHAR(500)", sql)
        self.assertIn("MODIFY demo_url VARCHAR(500)", sql)

        downgrade_sql = downgrade_output.getvalue()
        self.assertIn("DROP TABLE project_group", downgrade_sql)
        self.assertIn("DROP TABLE profile", downgrade_sql)
        self.assertIn("DROP TABLE social", downgrade_sql)
        self.assertIn("DROP TABLE professional_skill", downgrade_sql)
        self.assertIn("DROP TABLE technical_skill", downgrade_sql)
        self.assertIn("DROP FOREIGN KEY fk_project_group_id", downgrade_sql)
        self.assertIn("DROP COLUMN group_id", downgrade_sql)
