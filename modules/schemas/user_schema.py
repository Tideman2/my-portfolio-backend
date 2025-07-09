from marshmallow import Schema, fields
from marshmallow.validate import Length


class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, validate=Length(min=6))
