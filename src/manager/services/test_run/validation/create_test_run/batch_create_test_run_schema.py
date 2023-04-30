from marshmallow import Schema, fields
from marshmallow.validate import Length

from src.manager.services.test_run.validation.create_test_run.batch_create_test_run_common_schema import (
    BatchCreateTestRunCommonSchema,
)
from src.manager.services.test_run.validation.create_test_run.create_test_run_schema import (
    CreateTestRunSchema,
)


class BatchCreateTestRunSchema(Schema):
    common = fields.Nested(BatchCreateTestRunCommonSchema)
    endpoints = fields.List(
        fields.Nested(CreateTestRunSchema),
        required=True,
        allow_none=False,
        validate=Length(min=1, max=1000),
    )
