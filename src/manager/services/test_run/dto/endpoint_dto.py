from marshmallow import Schema, fields


class EndpointDto(Schema):
    method = fields.String()
    headers = fields.Dict()
    url = fields.Url(
        require_tld=False,  # For internal lookups without any '.' like "manager"
    )
    body = fields.Raw()

    class Meta:
        ordered = True
