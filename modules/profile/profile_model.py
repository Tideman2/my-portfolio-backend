from extensions import db


class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    date_of_birth = db.Column(db.Date)
    country = db.Column(db.String(100))
    bio = db.Column(db.Text)


class Social(db.Model):
    __tablename__ = 'social'
    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
