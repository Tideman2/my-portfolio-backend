from extensions import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(500))
    stack = db.Column(db.String(255))
    goal = db.Column(db.Text)
    github_url = db.Column(db.String(500))
    demo_url = db.Column(db.String(500))
    image_public_id = db.Column(db.String(255))
