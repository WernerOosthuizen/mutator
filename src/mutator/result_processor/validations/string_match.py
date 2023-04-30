import logging
from dataclasses import dataclass
from typing import Dict

from src.common.database.validation_result import ValidationResult
from src.common.test_result.test_result import TestResult
from src.mutator.result_processor.validations.validator import Validator


@dataclass
class StringMatch(Validator):
    test_item: TestResult
    config: Dict

    def __validate__(self) -> ValidationResult:
        # If string is found in response, fail validator
        try:
            result = ValidationResult()
            result.type = self.__class__.__name__

            match_string = self.config.get("match_string")
            if match_string in str(self.test_item.response.body):
                logging.debug(f"String found in response body: {match_string}")
                result.passed = False
                result.message = f"String found in response body: {match_string}"
            else:
                logging.debug(f"String not found in response body: {match_string}")
                result.passed = True
                result.message = f"String not found in response body: {match_string}"

            return result
        except Exception as e:
            logging.exception(f"Could not check if string is in response body: {e}")
