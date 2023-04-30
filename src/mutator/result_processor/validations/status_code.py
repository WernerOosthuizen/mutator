import logging
from dataclasses import dataclass
from typing import List, Dict

from src.common.database.validation_result import ValidationResult
from src.common.test_result.test_result import TestResult
from src.mutator.result_processor.validations.validator import Validator


@dataclass
class StatusCode(Validator):
    test_item: TestResult
    config: Dict

    def __validate__(self) -> ValidationResult:
        try:
            response_status_code: int = self.test_item.response.status_code
            logging.debug(f"Validating response status code {response_status_code}.")

            invalid_status_code: List = self.config.get("invalid_status_codes")

            result = ValidationResult()
            result.type = self.__class__.__name__

            if response_status_code == 200:
                result.passed = True
            elif response_status_code >= 500:
                result.passed = False
            elif (
                invalid_status_code is not None
                and response_status_code in invalid_status_code
            ):
                result.passed = False
            else:
                result.passed = True

            if result.passed:
                logging.debug("Response status code is valid.")
                result.message = "Passed"
            else:
                f"Invalid response status code found: {response_status_code}"
                result.message = f"Found invalid response code: {response_status_code}"
            return result
        except Exception as e:
            logging.exception(f"Could not validate response status code: {e}")
