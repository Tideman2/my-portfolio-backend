from marshmallow import Schema, fields


class MailSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    subject = fields.Str(required=True)
    message = fields.Str(required=True)
