from marshmallow import Schema, fields

from src.manager.services.test_run.dto.endpoint_dto import (
    EndpointDto,
)


class TestRunDto(Schema):
    id = fields.Integer()
    endpoint = fields.Nested(EndpointDto)
    config = fields.Dict()
    batch_id = fields.String()
    state = fields.String()
    state_description = fields.String(allow_none=True)
    passed = fields.Boolean(allow_none=True)
    test_generated_count = fields.Integer(allow_none=True)
    test_result_count = fields.Integer(allow_none=True)
    run_attempts = fields.Integer(allow_none=True)
    create_date = fields.DateTime()
    last_update_date = fields.DateTime()

    class Meta:
        ordered = True
        datetimeformat = "%Y-%m-%dT%H:%M:%S"
