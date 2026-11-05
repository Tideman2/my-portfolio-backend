# project_routes.py
import os
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify
from modules.project.project_model import Project
from modules.project_group.project_group_model import ProjectGroup
from extensions import db
from decorators.jwt_required import jwt_required
from modules.schemas.project_schema import ProjectSchema, ProjectUpdateSchema
from marshmallow import ValidationError


project_bp = Blueprint("project", __name__, url_prefix="/api/projects")


def uploadImage(img, img_id):
    try:
        upload_result = cloudinary.uploader.upload(
            img,
            public_id=img_id,
            unique_filename=True,
            overwrite=False
        )
        return upload_result["secure_url"], upload_result["public_id"]
    except Exception as e:
        print("Cloudinary upload error:", e)
        return None, None


@project_bp.route("/", methods=["GET"])
def get_projects():
    query = Project.query

    group_id = request.args.get("group_id")
    group_slug = request.args.get("group")

    if group_id:
        try:
            group_id = int(group_id)
        except ValueError:
            return jsonify({"error": "Invalid group_id"}), 400

        if not db.session.get(ProjectGroup, group_id):
            return jsonify({"error": "Project group not found"}), 404
        query = query.filter_by(group_id=group_id)
    elif group_slug:
        group = ProjectGroup.query.filter_by(slug=group_slug).first()
        if not group:
            return jsonify({"error": "Project group not found"}), 404
        query = query.filter_by(group_id=group.id)

    projects = query.order_by(Project.id).all()
    holder = []
    for project in projects:
        holder.append({
            "id": project.id,
            "title": project.title,
            "image": project.image,
            "stack": project.stack,
            "goal": project.goal,
            "github_url": project.github_url,
            "demo_url": project.demo_url
        })
    return jsonify(holder)


@project_bp.route("/", methods=["POST"])
@jwt_required
def create_project():
    try:
        schema = ProjectSchema()
        validated_data = schema.load(request.form)
        image = request.files.get("image")
        image_url = None
        image_public_id = None

        if not db.session.get(ProjectGroup, validated_data["group_id"]):
            return jsonify({"error": "Project group not found"}), 400

        if image:
            image_url, image_public_id = uploadImage(
                image, validated_data["title"])
        project = Project(**validated_data, image=image_url,
                          image_public_id=image_public_id)

        db.session.add(project)
        db.session.commit()
        return jsonify({"message": "Project created"}), 201
    except ValidationError as err:
        return jsonify({
            "errors": err.messages
        }), 400


@project_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required
def update_project(id):
    project = db.session.get(Project, id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    schema = ProjectUpdateSchema()
    try:
        data = schema.load(request.form, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if "group_id" in data and not db.session.get(ProjectGroup, data["group_id"]):
        return jsonify({"error": "Project group not found"}), 400

    old_public_id = project.image_public_id
    image = request.files.get("image")
    if image:
        image_url, image_public_id = uploadImage(
            image, data.get("title", project.title)
        )
        if image_url:
            project.image = image_url
            project.image_public_id = image_public_id

    for field, value in data.items():
        setattr(project, field, value)

    db.session.commit()

    if image and old_public_id and project.image_public_id != old_public_id:
        cloudinary.uploader.destroy(old_public_id)

    return jsonify({"message": "Project updated"}), 200


@project_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required
def delete_project(id):
    project = db.session.get(Project, id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    if project.image_public_id:
        cloudinary.uploader.destroy(project.image_public_id)

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 200
