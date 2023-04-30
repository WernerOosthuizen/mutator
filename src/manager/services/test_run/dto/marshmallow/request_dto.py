from marshmallow import Schema, fields


class RequestDto(Schema):
    hash = fields.String()
    method = fields.String()
    headers = fields.Dict()
    url = fields.String()
    body = fields.Raw()

    class Meta:
        ordered = True
