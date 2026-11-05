from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from decorators.jwt_required import jwt_required
from extensions import db
from modules.schemas.skill_schema import ProfessionalSkillSchema, TechnicalSkillSchema
from modules.skill.skill_model import ProfessionalSkill, TechnicalSkill

skill_bp = Blueprint("skill", __name__, url_prefix="/me")


def serialize_skill(skill):
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "proficiency": skill.proficiency,
    }


def list_skills(model):
    skills = model.query.order_by(model.id).all()
    return jsonify([serialize_skill(skill) for skill in skills])


def create_skill(model, schema_class):
    schema = schema_class()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    skill = model(**data)
    db.session.add(skill)
    db.session.commit()
    return jsonify(serialize_skill(skill)), 201


def update_skill(model, schema_class, id):
    skill = db.session.get(model, id)
    if not skill:
        return jsonify({"error": "Skill not found"}), 404

    schema = schema_class()
    try:
        data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for field, value in data.items():
        setattr(skill, field, value)
    db.session.commit()
    return jsonify(serialize_skill(skill))


def delete_skill(model, id):
    skill = db.session.get(model, id)
    if not skill:
        return jsonify({"error": "Skill not found"}), 404

    db.session.delete(skill)
    db.session.commit()
    return jsonify({"message": "Skill deleted"}), 200


@skill_bp.route("/professional-skills", methods=["GET"])
def get_professional_skills():
    return list_skills(ProfessionalSkill)


@skill_bp.route("/professional-skills", methods=["POST"])
@jwt_required
def create_professional_skill():
    return create_skill(ProfessionalSkill, ProfessionalSkillSchema)


@skill_bp.route("/professional-skills/<int:id>", methods=["PATCH"])
@jwt_required
def update_professional_skill(id):
    return update_skill(ProfessionalSkill, ProfessionalSkillSchema, id)


@skill_bp.route("/professional-skills/<int:id>", methods=["DELETE"])
@jwt_required
def delete_professional_skill(id):
    return delete_skill(ProfessionalSkill, id)


@skill_bp.route("/technical-skills", methods=["GET"])
def get_technical_skills():
    return list_skills(TechnicalSkill)


@skill_bp.route("/technical-skills", methods=["POST"])
@jwt_required
def create_technical_skill():
    return create_skill(TechnicalSkill, TechnicalSkillSchema)


@skill_bp.route("/technical-skills/<int:id>", methods=["PATCH"])
@jwt_required
def update_technical_skill(id):
    return update_skill(TechnicalSkill, TechnicalSkillSchema, id)


@skill_bp.route("/technical-skills/<int:id>", methods=["DELETE"])
@jwt_required
def delete_technical_skill(id):
    return delete_skill(TechnicalSkill, id)
