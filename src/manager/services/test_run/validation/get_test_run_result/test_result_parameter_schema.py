from marshmallow import Schema, fields
from marshmallow.validate import Range, Length, OneOf


class TestResultParameterSchema(Schema):
    passed = fields.Boolean(
        required=False,
        allow_none=True,
    )
    test_run_id = fields.String(
        required=False, allow_none=True, validate=Length(max=70)
    )
    request_hash = fields.String(
        required=False, allow_none=True, validate=Length(max=70)
    )
    response_hash = fields.String(
        required=False, allow_none=True, validate=Length(max=70)
    )
    test_type = fields.String(
        required=False,
        allow_none=True,
        validate=[Length(max=45), OneOf(["INTEGER", "DOUBLE", "STRING", "REMOVE"])],
    )
    test_value = fields.String(
        required=False, allow_none=True, validate=Length(max=10000)
    )
    method = fields.String(
        required=False,
        allow_none=True,
        validate=OneOf(["GET", "POST", "PUT", "DELETE"]),
    )
    request_url = fields.Url(
        required=False,
        allow_none=True,
        validate=Length(max=2048),
        schemes=("http", "https"),
        require_tld=False,  # For internal lookups without any '.' like "manager"
    )
    response_status_code = fields.Integer(
        required=False, allow_none=True, validate=Range(min=0, max=65000)
    )
    validation_type = fields.String(required=False, allow_none=True)
    validation_passed = fields.Boolean(
        required=False,
        allow_none=True,
    )
    sort_order = fields.String(
        validate=OneOf(["asc", "ASC", "desc", "DESC"]),
        required=False,
        allow_none=True,
    )
    page = fields.Integer(
        required=False, allow_none=True, validate=Range(min=0, max=65000)
    )
    page_size = fields.Integer(
        required=False, allow_none=True, validate=Range(min=0, max=50)
    )
