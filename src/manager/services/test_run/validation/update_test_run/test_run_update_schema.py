from marshmallow import Schema, fields
from marshmallow.validate import Length, Range


class TestRunUpdateSchema(Schema):
    id = fields.Integer(
        required=True, allow_none=False, validate=(Range(min=0, max=1000000))
    )
    state = fields.String(required=False, validate=Length(max=50))
    state_description = fields.String(required=False, validate=Length(max=255))
    passed = fields.Boolean()
    test_generated_count = fields.Integer(
        required=False, validate=(Range(min=0, max=100000))
    )
    run_attempts = fields.Integer(required=False, validate=(Range(min=0, max=1000)))
