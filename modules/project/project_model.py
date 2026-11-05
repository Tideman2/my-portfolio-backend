from extensions import db


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(500))
    stack = db.Column(db.String(255))
    goal = db.Column(db.Text)
    github_url = db.Column(db.String(500))
    demo_url = db.Column(db.String(500))
    image_public_id = db.Column(db.String(255))
    group_id = db.Column(
        db.Integer, db.ForeignKey('project_group.id'), nullable=False
    )
    group = db.relationship('ProjectGroup', backref='projects')
