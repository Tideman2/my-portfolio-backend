import io
import logging
import unittest
import warnings
from contextlib import redirect_stdout

from flask import Flask
from flask_migrate import Migrate, upgrade

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

        with warnings.catch_warnings(), app.app_context(), redirect_stdout(
            io.StringIO()
        ) as output:
            warnings.simplefilter("ignore")
            upgrade(directory="migrations", sql=True)

        sql = output.getvalue()
        self.assertIn("CREATE TABLE project_group", sql)
        self.assertIn("ALTER TABLE project ADD COLUMN group_id", sql)
        self.assertIn("FOREIGN KEY(group_id) REFERENCES project_group (id)", sql)
