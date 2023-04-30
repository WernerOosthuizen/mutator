import json

from marshmallow import Schema, fields, ValidationError, validates
from marshmallow.validate import Length, OneOf


class EndpointSchema(Schema):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
    method = fields.String(
        required=True,
        allow_none=False,
        validate=OneOf(["GET", "POST", "PUT", "DELETE", "PATCH"]),
    )
    headers = fields.Dict(required=True, allow_none=False)
    url = fields.Url(
        required=True,
        allow_none=False,
        validate=Length(max=2048),
        schemes=("http", "https"),
        require_tld=False,  # For internal lookups without any '.' like "manager"
    )
    body = fields.Raw(required=False, allow_none=True)

    @validates("body")
    def process_json_load(self, value):
        self.is_valid_json(value)
        self.check_max_size(value)

    def check_max_size(self, value):
        if isinstance(value, list):
            if len(value) > 10:
                raise ValidationError(
                    "Exceeded maximum list size of 10.", field_name="body"
                )

    def is_valid_json(self, value):
        error_message = "If the body field is populated, valid JSON is expected."
        if isinstance(value, list) or isinstance(value, dict):
            try:
                json.dumps(value)
            except json.decoder.JSONDecodeError:
                raise ValidationError(error_message)
        else:
            raise ValidationError(error_message)
