from marshmallow import Schema, fields
from marshmallow.validate import OneOf, Range


class TestRunParameterSchema(Schema):
    batch_id = fields.String(
        required=False,
        allow_none=True,
    )
    state = fields.String(
        validate=OneOf(
            ["PENDING", "GENERATING", "RUNNING", "COMPLETED", "CANCELLED", "FAILED"]
        ),
        required=False,
        allow_none=True,
    )
    passed = fields.Boolean(required=False, allow_none=True)
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
