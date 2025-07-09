# project_routes.py
import os
from modules.project.project_model import Project
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from werkzeug.utils import secure_filename
from decorators.jwt_required import jwt_required
from modules.schemas.project_schema import ProjectSchema
from marshmallow import ValidationError


project_bp = Blueprint("project", __name__, url_prefix="/api/projects")


@project_bp.route("/", methods=["GET"])
def get_projects():
    projects = Project.query.all()
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
        image_path = None

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

        project = Project(**validated_data, image=image_path)
        db.session.add(project)
        db.session.commit()
        return jsonify({"message": "Project created"}), 201
    except ValidationError as err:
        return jsonify({
            "errors": err.messages
        }, 400)


@project_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required
def delete_project(id):
    project = Project.query.get(id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    image_path = project.image
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 200
