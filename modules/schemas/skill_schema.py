from marshmallow import Schema, fields
from marshmallow.validate import Length, Range


class SkillSchema(Schema):
    name = fields.Str(required=True, validate=Length(min=1))
    description = fields.Str(required=True, validate=Length(min=1))
    proficiency = fields.Int(required=True, validate=Range(min=1, max=5))


class ProfessionalSkillSchema(SkillSchema):
    pass


class TechnicalSkillSchema(SkillSchema):
    pass
