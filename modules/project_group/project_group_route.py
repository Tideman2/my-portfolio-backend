import re

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from decorators.jwt_required import jwt_required
from extensions import db
from modules.project.project_model import Project
from modules.project_group.project_group_model import ProjectGroup
from modules.schemas.project_group_schema import ProjectGroupSchema

project_group_bp = Blueprint(
    "project_group", __name__, url_prefix="/api/project-groups"
)


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "group"


def serialize_group(group):
    return {
        "id": group.id,
        "name": group.name,
        "slug": group.slug,
    }


@project_group_bp.route("/", methods=["GET"], strict_slashes=False)
def get_project_groups():
    groups = ProjectGroup.query.order_by(ProjectGroup.id).all()
    return jsonify([serialize_group(group) for group in groups])


@project_group_bp.route("/", methods=["POST"], strict_slashes=False)
@jwt_required
def create_project_group():
    schema = ProjectGroupSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if ProjectGroup.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Group name already exists"}), 409

    slug = slugify(data["name"])
    if ProjectGroup.query.filter_by(slug=slug).first():
        return jsonify({"error": "Group slug already exists"}), 409

    group = ProjectGroup(name=data["name"], slug=slug)
    db.session.add(group)
    db.session.commit()
    return jsonify(serialize_group(group)), 201


@project_group_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required
def update_project_group(id):
    group = db.session.get(ProjectGroup, id)
    if not group:
        return jsonify({"error": "Project group not found"}), 404

    schema = ProjectGroupSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    duplicate = ProjectGroup.query.filter(
        ProjectGroup.name == data["name"], ProjectGroup.id != id
    ).first()
    if duplicate:
        return jsonify({"error": "Group name already exists"}), 409

    group.name = data["name"]
    db.session.commit()
    return jsonify(serialize_group(group))


@project_group_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required
def delete_project_group(id):
    group = db.session.get(ProjectGroup, id)
    if not group:
        return jsonify({"error": "Project group not found"}), 404

    if Project.query.filter_by(group_id=id).first():
        return jsonify(
            {"error": "Project group still has projects"}
        ), 409

    db.session.delete(group)
    db.session.commit()
    return jsonify({"message": "Project group deleted"}), 200
