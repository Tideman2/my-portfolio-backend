from marshmallow import Schema, fields
from marshmallow.validate import Length


class ProjectGroupSchema(Schema):
    name = fields.Str(required=True, validate=Length(min=1, max=100))
