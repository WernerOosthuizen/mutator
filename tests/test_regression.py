from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.common.test_result.test_result import TestResult
from src.mutator.result_processor.validations.regression import Regression
from src.mutator.runner.request.generic_request import GenericRequest
from src.mutator.runner.response.generic_response import GenericResponse


class TestRegression(TestCase):
    def test_response_hashes_match(self):
        test_result = TestResult()
        request = GenericRequest()
        request.hash = "1234"
        test_result.request = request
        response = GenericResponse()
        response.hash = "1234"
        test_result.response = response
        regression = Regression(test_result, {})
        hashed_match: bool = regression.response_hashes_match("1234", "1234")
        self.assertTrue(hashed_match)

    def test_response_hashes_do_not_match(self):
        test_result = TestResult()
        request = GenericRequest()
        request.hash = "1234"
        test_result.request = request
        response = GenericResponse()
        response.hash = "1234"
        test_result.response = response
        regression = Regression(test_result, {})
        hashed_match: bool = regression.response_hashes_match("1233", "1234")
        self.assertFalse(hashed_match)

    @patch(
        "src.manager.services.test_run.dao.test_result_dao.get_previous_response_hash",
        MagicMock(return_value="1234"),
    )
    def test_process_previous_response_hash_same_value(self):
        test_result = TestResult()
        request = GenericRequest()
        request.hash = "1234"
        test_result.request = request
        response = GenericResponse()
        response.hash = "1234"
        test_result.response = response
        regression = Regression(test_result, {})
        regression.current_response_hash = "1234"
        validation_response = regression.__validate__()
        self.assertEqual("Regression", validation_response.type)
        self.assertEqual("Passed", validation_response.message)

    @patch(
        "src.manager.services.test_run.dao.test_result_dao.get_previous_response_hash",
        MagicMock(return_value="4321"),
    )
    def test_process_previous_response_hash_different_value(self):
        test_result = TestResult()
        request = GenericRequest()
        request.hash = "1234"
        test_result.request = request
        response = GenericResponse()
        response.hash = "1234"
        test_result.response = response
        regression = Regression(test_result, {})
        regression.current_response_hash = "1234"
        validation_response = regression.__validate__()
        self.assertEqual("Regression", validation_response.type)
        self.assertEqual(
            "Regression occurred. Current response hash 1234 is different from previous response hash 4321.",
            validation_response.message,
        )

    @patch(
        "src.manager.services.test_run.dao.test_result_dao.get_previous_response_hash",
        MagicMock(return_value=None),
    )
    def test_process_previous_response_hash_none(self):
        test_result = TestResult()
        request = GenericRequest()
        request.hash = "1234"
        test_result.request = request
        response = GenericResponse()
        response.hash = "1234"
        test_result.response = response
        regression = Regression(test_result, {})
        regression.current_response_hash = "1234"
        validation_response = regression.__validate__()
        self.assertEqual("Regression", validation_response.type)
        self.assertEqual("Passed", validation_response.message)
