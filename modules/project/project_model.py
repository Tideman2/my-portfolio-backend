from extensions import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100))  # Path to image file
    stack = db.Column(db.String(200))  # e.g., "Python, Flask, HTML"
    goal = db.Column(db.String(300))
    github_url = db.Column(db.String(200))
    demo_url = db.Column(db.String(200))  # Link to live demo
