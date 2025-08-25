# project_routes.py
import os
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify
from modules.project.project_model import Project
from extensions import db
from decorators.jwt_required import jwt_required
from modules.schemas.project_schema import ProjectSchema
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
        image_url = None
        image_public_id = None

        if image:
            image_url, image_public_id = uploadImage(
                image, validated_data["title"])
            print(image_url)
        project = Project(**validated_data, image=image_url,
                          image_public_id=image_public_id)

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

    if project.image_public_id:
        cloudinary.uploader.destroy(project.image_public_id)

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 200
