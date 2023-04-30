from unittest import TestCase

from src.common.test_result.test_result import TestResult
from src.mutator.result_processor.validations.status_code import StatusCode
from src.mutator.runner.response.generic_response import GenericResponse


class TestResponseCode(TestCase):
    def test_validate_200_status_code(self):
        test_result = TestResult()
        response = GenericResponse()
        response.status_code = 200
        test_result.response = response
        response_code_validator = StatusCode(test_result, {})
        validation_response = response_code_validator.__validate__()
        self.assertEqual("StatusCode", validation_response.type)
        self.assertEqual("Passed", validation_response.message)

    def test_validate_custom_status_code_401(self):
        test_result = TestResult()
        response = GenericResponse()
        response.status_code = 401
        test_result.response = response
        response_code_validator = StatusCode(
            test_result, {"invalid_status_codes": [401, 402]}
        )
        validation_response = response_code_validator.__validate__()
        self.assertEqual("StatusCode", validation_response.type)
        self.assertEqual(
            "Found invalid response code: 401", validation_response.message
        )

    def test_validate_404_status_code(self):
        test_result = TestResult()
        response = GenericResponse()
        response.status_code = 404
        test_result.response = response
        response_code_validator = StatusCode(test_result, {})
        validation_response = response_code_validator.__validate__()
        self.assertEqual("StatusCode", validation_response.type)
        self.assertEqual("Passed", validation_response.message)

    def test_validate_500_status_code(self):
        test_result = TestResult()
        response = GenericResponse()
        response.status_code = 500
        test_result.response = response
        response_code_validator = StatusCode(test_result, {})
        validation_response = response_code_validator.__validate__()
        self.assertEqual("StatusCode", validation_response.type)
        self.assertEqual(
            "Found invalid response code: 500", validation_response.message
        )

    def test_validate_555_status_code(self):
        test_result = TestResult()
        response = GenericResponse()
        response.status_code = 555
        test_result.response = response
        response_code_validator = StatusCode(test_result, {})
        validation_response = response_code_validator.__validate__()
        self.assertEqual("StatusCode", validation_response.type)
        self.assertEqual(
            "Found invalid response code: 555", validation_response.message
        )
