from marshmallow import Schema, fields

from src.manager.services.test_run.validation.create_test_run.config_schema import (
    ConfigSchema,
)


class BatchCreateTestRunCommonSchema(Schema):
    headers = fields.Dict()
    config = fields.Nested(ConfigSchema)
