import logging
import os
import pathlib
from configparser import ConfigParser
from typing import Dict

import requests
from boltons.iterutils import remap
from requests import Response, Session
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    stop_after_delay,
    retry_if_exception_type,
    after_log,
    before_sleep_log,
)

from src.common.test_result.test_result import TestResult
from src.mutator.common.utils.hash import hash_object
from src.mutator.generator.test import Test
from src.mutator.runner.request.generic_request import GenericRequest
from src.mutator.runner.response.generic_response import GenericResponse

log = logging.getLogger()

config_file_path = (
    pathlib.Path(os.path.abspath(__file__)).parents[1].__str__() + "/config/config.ini"
)
config = ConfigParser()

config.read(config_file_path)

request_timeout: int = config.getint("consumer", "request_timeout")


@retry(
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=(stop_after_delay(60) | stop_after_attempt(3)),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    before_sleep=before_sleep_log(logging.getLogger(), logging.WARNING),
    after=after_log(logging.getLogger(), logging.WARNING),
)
def run(test: Test, field_matcher, session: Session) -> TestResult:
    logging.debug(f"Building request from test {test}")
    request: GenericRequest = build_request(test)

    logging.debug(f"Performing Request: {request.__dict__}")
    response: GenericResponse = perform_request(request, session)
    logging.debug(f"Finished performing Request: {request.__dict__}")

    test_result = TestResult()
    test_result.request = request
    test_result.request.hash = test.test_hash
    if field_matcher:
        response.hash = build_response_hash(response, field_matcher)
    test_result.response = response
    test_result.validations = []
    return test_result


def build_request(test: Test) -> GenericRequest:
    request = GenericRequest()
    try:
        request.headers = test.headers
        request.method = test.method
        request.url = test.url
        request.body = test.body
    except Exception as e:
        logging.exception("Exception while building request.")
        raise e
    return request


def build_response_hash(test: GenericResponse, field_matcher) -> GenericResponse:
    logging.debug(f"creating response hash for response_json:{test.__dict__}")
    # Add field matching strategies to select which fields to use to create response hash
    # Response might include changing values like create_date or id
    response = {
        "url": test.url,
        "body": extract_response_fields(test.body, field_matcher),
        "status_code": test.status_code,
    }
    response_hash = hash_object(response)
    logging.debug(f"created hash {response_hash}")

    return response_hash


def extract_response_fields(body: Dict, field_matcher):
    if body is None or not isinstance(body, Dict):
        return None
    if field_matcher is None:
        # Using all fields, so don't alter
        return body
    new_body = remap(body, visit=field_matcher)
    return new_body


def perform_request(request: GenericRequest, session: Session) -> GenericResponse:
    url = request.url
    logging.debug(f"Performing request {request.method} to url: {url}.")

    content = request.body
    if content is None:
        logging.debug(f"performing request without content to url: {url}")
    else:
        logging.debug(f"performing request to url '{url}' with content: {request.body}")

    response: Response = session.request(
        headers=request.headers,
        method=request.method,
        url=url,
        json=content if content is not None else None,
        timeout=request_timeout,
    )

    logging.debug(f"Finished performing request to url: {url}")
    status = response.status_code
    if status == 429:
        raise requests.exceptions.RequestException(f"Response code {status} received")
    headers = dict(response.headers)

    generic_response = GenericResponse()
    generic_response.status_code = status
    generic_response.headers = dict(**headers)
    generic_response.url = str(url)

    content_type = headers.get("Content-Type")
    if content_type == "application/json":
        generic_response.body = response.json()
    else:
        generic_response.body = {"raw_response": str(response.text)}

    generic_response.elapsed_time = response.elapsed.total_seconds()
    logging.debug(f"Current response: {generic_response.__dict__}")
    return generic_response
