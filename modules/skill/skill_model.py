from extensions import db


class ProfessionalSkill(db.Model):
    __tablename__ = 'professional_skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    proficiency = db.Column(db.Integer, nullable=False)


class TechnicalSkill(db.Model):
    __tablename__ = 'technical_skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    proficiency = db.Column(db.Integer, nullable=False)
