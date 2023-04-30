import logging
from datetime import datetime
from typing import Dict, List

from sqlalchemy.orm import Session
from werkzeug.exceptions import InternalServerError

from src.common.database.result import Result
from src.common.database.validation_result import ValidationResult
from src.common.test_result.test_result import TestResult

# If import all validations is removed, validators will not be automatically loaded from validations folder
from src.mutator.result_processor.validations import *  # noqa
from src.mutator.result_processor.validations.regression import Regression
from src.mutator.result_processor.validations.validator import Validator


def process_test_result(
    test_result: TestResult, validation_config: Dict, session: Session
) -> Dict:
    logging.debug("PROCESSING TEST RESULT")
    logging.debug(f"Received test result: {test_result.__dict__}")

    test_run_id = test_result.test_run_id
    logging.debug(f"Processing test result for test run id {test_run_id}.")
    logging.debug(f"Fetching test run info from DB if not cached: {test_run_id}")

    # Fetch and run enabled validations
    validations: List[Validator] = get_enabled_validators(
        test_result, validation_config
    )

    # Special case for Regression Validator for now as it needs Session for DB Interaction
    regression_config = validation_config.get("Regression")
    if regression_config.get("enabled"):
        regression_validator = Regression(test_result, regression_config, session)
        validations.append(regression_validator)
    logging.debug(f"FOUND ENABLED VALIDATORS: {validations}")

    validation_responses = perform_validations(validations)
    logging.debug(f"Validation Responses: {validation_responses}")
    test_result.validations = validation_responses

    try:
        persist_test_result(test_result, session)
    except Exception as e:
        logging.exception(
            f"Could not finish processing test {test_result}. " f"Exception: {e}"
        )
        session.rollback()
        raise InternalServerError(
            "A General Error Occurred while processing test results."
        )
    logging.debug(f"Finished processing test result for test run id {test_run_id}.")
    return {"message_persisted": True}


def get_enabled_validators(test_result: TestResult, validation_config: Dict):
    validators = Validator.__subclasses__()
    logging.debug(f"Validator subclasses: {validators}")

    enabled_validators = []
    for validator in validators:
        if (
            validator.__name__ == Regression.__name__
        ):  # Special case for now that is handled elsewhere
            continue
        validator_config = validation_config.get(validator.__name__)
        # Default to enabled if not configured
        enabled = (
            validator_config.get("enabled") if validator_config is not None else True
        )
        logging.debug(f"Validator: {validator}, enabled config: {enabled}")
        if enabled:
            logging.debug(
                f"Creating validator: {validator} and inject validator config: {validator_config}"
            )
            new_validator = validator(test_result, validator_config)  # noqa
            enabled_validators.append(new_validator)
    return enabled_validators


def perform_validations(validations: List) -> List[ValidationResult]:
    validation_responses: List[ValidationResult] = []

    for validation in validations:
        logging.debug(f"Performing validation: {validation}")
        try:
            validation_response: ValidationResult = validation.__validate__()
            validation_responses.append(validation_response)
        except Exception as e:
            logging.exception(
                f"INVESTIGATE THIS: Could not perform validation {validation}. Skipping for now. Exception {e}"
            )

    logging.debug("Done with validations.")
    return validation_responses


def persist_test_result(test_result: TestResult, session: Session):
    test_run_id = test_result.test_run_id
    request_hash = test_result.request.hash
    logging.debug(
        f"Persisting test results for test run {test_run_id} and request hash {request_hash}."
    )

    result: Result = build_result(test_result)

    validations: List[ValidationResult] = test_result.validations
    logging.debug(
        f"Processing {len(validations)} validation results "
        f"for request {request_hash} "
        f"for test run {test_run_id}"
    )

    if not validations_passed(validations):
        result.passed = False
    session.add(result)
    session.flush()
    logging.debug(f"RESULT ID IS: {result.id}")

    logging.debug(
        f"Finished processing {len(validations)} validation results "
        f"for request {request_hash} "
        f"for test run {test_run_id}"
    )
    for validation in validations:
        validation.test_result_id = result.id
        validation.create_date = datetime.utcnow()
    session.bulk_save_objects(validations)

    session.commit()
    logging.debug(
        f"Finished persisting test results for test run {test_run_id} and request hash {request_hash}."
    )


def validations_passed(validations: List[ValidationResult]) -> bool:
    valid = True
    if validations is not None:
        for validation in validations:
            logging.debug("Checking if validation Passed.")
            if not validation.passed:
                valid = False

    return valid


def build_result(test_result: TestResult) -> Result:
    result = Result()
    result.test_run_id = test_result.test_run_id
    result.test_type = test_result.test_type
    result.test_value = test_result.test_value
    result.passed = True  # Default
    result.request_hash = test_result.request.hash
    result.request_method = test_result.request.method
    result.request_headers = test_result.request.headers
    result.request_url = test_result.request.url
    result.request_body = test_result.request.body
    result.response_hash = test_result.response.hash
    result.response_headers = test_result.response.headers
    result.response_body = test_result.response.body
    result.response_status_code = test_result.response.status_code
    result.create_date = datetime.utcnow()
    logging.debug(f"Built result: {result.__dict__}")
    return result
