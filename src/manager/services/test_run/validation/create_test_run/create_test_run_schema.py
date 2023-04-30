from marshmallow import Schema, fields

from src.manager.services.test_run.validation.create_test_run.config_schema import (
    ConfigSchema,
)
from src.manager.services.test_run.validation.create_test_run.endpoint_schema import (
    EndpointSchema,
)


class CreateTestRunSchema(Schema):
    endpoint = fields.Nested(EndpointSchema, required=True, allow_none=False)
    config = fields.Nested(ConfigSchema, required=False, allow_none=True)
