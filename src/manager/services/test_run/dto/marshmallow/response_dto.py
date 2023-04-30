from marshmallow import Schema, fields


class ResponseDto(Schema):
    hash = fields.String()
    headers = fields.Dict()
    body = fields.Raw()
    status_code = fields.Integer()

    class Meta:
        ordered = True
