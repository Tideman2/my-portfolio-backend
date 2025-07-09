import os
from flask_cors import CORS  # <-- Add this
from flask import Flask
# from flask_migrate import Migrate
from dotenv import load_dotenv
from extensions import db, mail
from modules.project.project_route import project_bp
from modules.project.project_model import Project
from modules.user.user_route import auth_dp
from modules.mail.mail_route import mail_dp

load_dotenv(override=True)


def create_app():
    appy = Flask(__name__)
    # SQLite and SQLAlchemy config
    appy.config['SQLALCHEMY_DATABASE_URI'] = str(
        os.environ.get("DATABASE_URI"))
    appy.config['UPLOAD_FOLDER'] = 'static/project_images'
    appy.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT config
    appy.config['JWT_SECRET_KEY'] = os.environ.get(
        "JWT_SECRET_KEY", "dev-secret")
    appy.config['JWT_ALGORITHM'] = os.environ.get("JWT_ALGORITHM", "HS256")
    appy.config['JWT_EXPIRES_IN'] = int(os.environ.get("JWT_EXPIRES_IN"))

    # Mail config
    appy.config['MAIL_SERVER'] = 'smtp.gmail.com'
    appy.config['MAIL_PORT'] = 587
    appy.config['MAIL_USE_TLS'] = True
    appy.config['MAIL_USERNAME'] = str(os.environ.get("FLASK_MAIL_USERNAME"))
    appy.config['MAIL_PASSWORD'] = str(os.environ.get("FLASK_MAIL_PASSWORD"))
    appy.config['MAIL_DEFAULT_SENDER'] = str(
        os.environ.get("FLASK_MAIL_USERNAME"))

    # <-- This line enables CORS for all routes
    CORS(appy, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # init dependencies
    mail.init_app(appy)
    db.init_app(appy)
    # migrate = Migrate(appy, db)
    # register routes blue0prints
    appy.register_blueprint(project_bp)
    appy.register_blueprint(auth_dp)
    appy.register_blueprint(mail_dp)
    return appy


app = create_app()

# Create the table if it doesn't exist
with app.app_context():
    db.create_all()
    # Only insert if the table is empty
    if not Project.query.first():
        project1 = Project(
            title="Portfolio Website",
            image="static/project_images/portfolio.png",
            stack="HTML, CSS, JavaScript, Flask",
            goal="To showcase my skills and projects",
            github_url="https://github.com/yourusername/portfolio",
            demo_url="https://your-portfolio-demo.com"
        )
        db.session.add(project1)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
