from flask_cors import CORS  # <-- Add this
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from extensions import db
from modules.project.project_route import project_bp
from modules.project.project_model import Project


def create_app():
    appy = Flask(__name__)
    # Using SQLite for now
    appy.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    appy.config['UPLOAD_FOLDER'] = 'static/project_images'
    appy.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    CORS(appy)  # <-- This line enables CORS for all routes

    db.init_app(appy)
    appy.register_blueprint(project_bp)
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
