import logging
from dataclasses import dataclass
from typing import Dict

from src.common.database.validation_result import ValidationResult
from src.common.test_result.test_result import TestResult
from src.mutator.result_processor.validations.validator import Validator


@dataclass
class ElapsedTime(Validator):
    test_item: TestResult
    config: Dict

    def __validate__(self) -> ValidationResult:
        try:
            elapsed_time: float = self.test_item.response.elapsed_time
            logging.debug(f"Validating response elapsed time {elapsed_time}.")

            result = ValidationResult()
            result.type = self.__class__.__name__

            max_elapsed_time = self.config.get("max_elapsed_time")
            if elapsed_time >= max_elapsed_time:
                logging.debug(f"elapsed time failed, value: {elapsed_time}")
                result.passed = False
                result.message = f"Elapsed time of {elapsed_time} was slower than expected max time {max_elapsed_time}."
            else:
                logging.debug(f"elapsed time passed, value: {elapsed_time}")
                result.passed = True
                result.message = "Passed"

            return result
        except Exception as e:
            logging.exception(f"Could not process elapsed time: {e}")
