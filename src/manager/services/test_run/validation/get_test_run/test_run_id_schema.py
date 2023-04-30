from marshmallow import Schema, fields
from marshmallow.validate import Range


class TestRunIdSchema(Schema):
    test_run_id = fields.Integer(
        required=True, allow_none=False, validate=(Range(min=0, max=1000000))
    )
