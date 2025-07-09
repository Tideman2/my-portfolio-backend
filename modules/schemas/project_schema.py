from marshmallow import Schema, fields


class ProjectSchema(Schema):
    title = fields.Str(required=True)
    # Path to image file
    stack = fields.Str(required=True)  # e.g., "Python, Flask, HTML"
    goal = fields.Str(required=True)
    github_url = fields.Str(required=True)
    demo_url = fields.Str(required=True)  # Link to live demo
