from marshmallow import Schema, fields


class ValidationResultDto(Schema):
    type = fields.String()
    passed = fields.Boolean()
    message = fields.String()

    class Meta:
        ordered = True
