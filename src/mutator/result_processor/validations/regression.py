import logging
from dataclasses import dataclass
from typing import Dict

from sqlalchemy.orm import Session

from src.common.database.validation_result import ValidationResult
from src.common.test_result.test_result import TestResult
from src.manager.services.test_run.dao import test_result_dao
from src.mutator.result_processor.validations.validator import Validator


@dataclass
class Regression(Validator):
    test_item: TestResult
    config: Dict
    session: Session = None
    current_response_hash = None
    previous_response_hash = None

    def __validate__(self) -> ValidationResult:
        logging.debug("Validating previous response.")
        validation_result = ValidationResult()
        current_request_hash = self.test_item.request.hash
        self.current_response_hash = self.test_item.response.hash

        self.previous_response_hash: str = test_result_dao.get_previous_response_hash(
            current_request_hash, self.session
        )

        if self.previous_response_hash is None:
            logging.debug(
                f"There is no previous test result for request {current_request_hash}, so it is a new request."
            )

            validation_result.type = self.__class__.__name__
            validation_result.passed = True
            validation_result.message = "Passed"
            return validation_result
        else:
            validation_result = self.process_previous_response_hash()
        return validation_result

    def process_previous_response_hash(self):
        validation_result = ValidationResult()
        validation_result.type = self.__class__.__name__
        if self.response_hashes_match(
            self.current_response_hash, self.previous_response_hash
        ):
            validation_result.passed = True
            validation_result.message = "Passed"
        else:
            validation_result.passed = False
            validation_result.message = (
                f"Regression occurred. Current response hash {self.current_response_hash}"
                f" is different from previous response hash {self.previous_response_hash}."
            )
        return validation_result

    def response_hashes_match(
        self, current_response_hash: str, previous_response_hash: str
    ) -> bool:
        if current_response_hash == previous_response_hash:
            logging.debug(
                f"For request hash {self.test_item.request.hash}"
                f"Current response hash {current_response_hash} "
                f"matches previous response hash {previous_response_hash}."
            )
            return True
        else:
            logging.debug(
                f"For request hash {self.test_item.request.hash} "
                f"current response hash {current_response_hash} "
                f"does not match previous response hash {previous_response_hash}. Regression Occurred."
            )
            return False
