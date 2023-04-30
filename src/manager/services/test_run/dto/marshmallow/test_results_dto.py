from marshmallow import Schema, fields

from src.manager.services.test_run.dto.marshmallow.request_dto import (
    RequestDto,
)
from src.manager.services.test_run.dto.marshmallow.response_dto import ResponseDto
from src.manager.services.test_run.dto.marshmallow.validation_result_dto import (
    ValidationResultDto,
)


# Opted to use own Dto mapping:
# src.manager.services.test_run.dto.test_results_dto.TestResultsDto
# Keeping this as reference
class TestResultsDto(Schema):
    test_run_id = fields.String()
    test_type = fields.String()
    test_value = fields.String()
    passed = fields.Boolean()
    request = fields.Nested(RequestDto)
    response = fields.Nested(ResponseDto)
    validations = fields.List(fields.Nested(ValidationResultDto))
    create_date = fields.DateTime()

    class Meta:
        ordered = True
        datetimeformat = "%Y-%m-%dT%H:%M:%S"
