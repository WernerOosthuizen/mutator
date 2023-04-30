from marshmallow import Schema, fields
from marshmallow.validate import Range, Length


class TestResultTestSchema(Schema):
    test_run_id = fields.Integer(
        required=True, allow_none=False, validate=Range(min=0, max=1000000)
    )
    request_hash = fields.String(
        required=False, allow_none=True, validate=Length(max=70)
    )
