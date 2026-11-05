from marshmallow import Schema, fields
from marshmallow.validate import Length


class ProfileSchema(Schema):
    name = fields.Str()
    date_of_birth = fields.Date()
    country = fields.Str()
    bio = fields.Str()


class SocialSchema(Schema):
    platform_name = fields.Str(required=True, validate=Length(min=1))
    url = fields.Str(required=True, validate=Length(min=1))
