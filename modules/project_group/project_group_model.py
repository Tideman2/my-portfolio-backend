from extensions import db


class ProjectGroup(db.Model):
    __tablename__ = 'project_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True)
