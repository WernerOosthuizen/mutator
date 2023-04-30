import copy
import json
import logging
import os
import uuid
from datetime import datetime
from numbers import Number
from queue import Queue
from typing import Any, Dict, Union, Tuple, List
from urllib.parse import (
    parse_qs,
    unquote_plus,
    urlencode,
    urlparse,
    urlunparse,
    ParseResult,
    parse_qsl,
)

from boltons.iterutils import remap

from src.common.database.test_run import TestRun
from src.common.test_configuration import TestConfiguration
from src.mutator.common.test_value_storage.test_repository import TestRepository
from src.mutator.common.utils.hash import hash_object
from src.mutator.common.utils.persistent_queue.dao.queue_item import QueueItem
from src.mutator.generator.test import Test
from src.mutator.generator.test_types import TestType

log = logging.getLogger()


def generate(test_repository: TestRepository, test: TestRun, queue: Queue) -> int:
    logging.debug(
        f"Running generator for test run id: {test.id} for test: {test.__dict__}"
    )
    test_count = 0

    incoming_endpoint = test.endpoint
    test_run_id = test.id
    start_time = datetime.utcnow()
    try:
        base_test_configuration = TestConfiguration()
        base_test_configuration.method = incoming_endpoint.get("method", None)
        base_test_configuration.headers = incoming_endpoint.get("headers", None)
        base_test_configuration.url = incoming_endpoint.get("url", None)
        base_test_configuration.body = incoming_endpoint.get("body", None)
        base_test_configuration.test_run_id = test_run_id
        base_test_configuration.test_repository = test_repository

        test_count: int = process_test(base_test_configuration, queue)
    except Exception as e:
        logging.exception(f"Error with configured endpoint {incoming_endpoint}: {e}")
    end_time = datetime.utcnow()
    execution_time_seconds = (end_time - start_time).total_seconds()
    logging.info(f"Generated {test_count} tests for test run id {test_run_id}.")
    logging.debug(
        f"Test generation took {execution_time_seconds} seconds, "
        f"at a rate of {test_count/execution_time_seconds} tests/second."
    )
    return test_count


def process_test(base_test_configuration: TestConfiguration, queue: Queue) -> int:
    url = base_test_configuration.url
    parsed_url = urlparse(url)
    generated_test_count = 0
    test_repository: TestRepository = base_test_configuration.test_repository

    # Get each test type and test value from test_repository
    # Depending on the test type (INTEGER, STRING, DOUBLE),
    # use test value as substituted for each field and value in test
    # If test type is REMOVE then a field will be removed as part of the test
    for test_type, test_value in test_repository.get_test_value():  # type: ignore
        test_configuration: TestConfiguration = copy.deepcopy(base_test_configuration)
        test_configuration.test_type = test_type
        test_configuration.test_value = test_value
        logging.debug(f"Generating test using value {test_value}, of type {test_type}.")
        # Create tests for resources
        if should_process_resources(parsed_url.path.split("/")):
            generated_test_count += process_resources(test_configuration, queue)

        # Create tests for parameters
        query_parameters: dict[Any, list] = get_query_parameters(parsed_url)

        if query_parameters:
            for parameter_index, (key, val) in enumerate(query_parameters.items()):
                if should_remove_entity(
                    test_type
                ):  # Should decide if this is the correct location. Works for now.
                    for i, value in enumerate(val):
                        query_param = {key: value}
                        test_configuration.url = remove_query_parameter_key(
                            parsed_url, query_param
                        )
                        test_context = json.dumps(query_param)
                        test: Test = build_test(test_configuration, test_context)
                        if persist_test(test, queue):
                            generated_test_count += 1
                else:
                    # Route normal query parameters and different forms of query parameter array's
                    # to different methods
                    for value in val:
                        if is_comma_separated_parameter_array(value) is False:
                            # This will handle formats of type queryKey=1
                            # Object looks like "{'queryKey': ['queryValue1']}}
                            # Also handles ampersand separated arrays
                            # such as queryKey=1&queryKey=2&queryKey=3, one after the other
                            # Object looks like "{'queryKey': ['queryValue1', 'queryValue2']}"
                            query_parameter = {key: value}
                            generated_test_count += process_query_parameter(
                                query_parameter,
                                test_configuration,
                                queue,
                            )
                        else:
                            # Create test for each item in comma separated query parameter array
                            # e.g. queryParam=1,2,3
                            # Object looks like "{'queryParamOne': ['1,2,3']}"

                            # for v in value:
                            query_parameter = {key: value}
                            generated_test_count += process_query_parameter_array(
                                query_parameter,
                                test_configuration,
                                queue,
                            )

        # Create tests for body
        if test_configuration.body:
            generated_test_count += process_body(test_configuration, queue)

    return generated_test_count


def get_query_parameters(parsed_url):
    query_parameter_list = parse_qs(parsed_url.query)
    return query_parameter_list


def process_resources(test_configuration: TestConfiguration, queue: Queue) -> int:
    generated_tests = 0

    # You only want to test a single field at a time
    # Use original "happy case" but only perform test on single field, so need to create deep copy of object
    original_url = copy.deepcopy(test_configuration.url)

    parsed_url = urlparse(original_url)
    parsed_resources: list = parsed_url.path.split("/")
    del parsed_resources[0]  # remove empty item at front of list

    for i, resource_section in enumerate(parsed_resources):
        new_resource = copy.deepcopy(parsed_resources)

        if should_remove_entity(test_configuration.test_type):
            test_configuration.url = remove_resource(parsed_url, new_resource, i)
        else:
            test_configuration.url = replace_resource(
                parsed_url, new_resource, i, test_configuration.test_value
            )

        test_context = str(i) + resource_section
        test: Test = build_test(test_configuration, test_context)
        if persist_test(test, queue):
            generated_tests += 1
        # Reset original value
        test_configuration.url = original_url

    logging.debug(f"Generated {generated_tests} resource tests.")
    return generated_tests


def should_process_resources(parsed_resources: list) -> bool:
    return len(parsed_resources) > 1


def should_remove_entity(test_type: str) -> bool:
    return test_type == TestType.REMOVE.value


def replace_resource(
    parsed_url: ParseResult, resources: list, index: int, test_value: str
) -> str:
    resources[index] = test_value
    # https://stackoverflow.com/a/21629125 -> Can use replace
    final_url = parsed_url._replace(path="/".join(resources))  # noqa
    return urlunparse(final_url)


def remove_resource(parsed_url: ParseResult, resources: list, index: int) -> str:
    del resources[index]
    # https://stackoverflow.com/a/21629125 -> Can use replace
    final_url = parsed_url._replace(path="/".join(resources))  # noqa
    return urlunparse(final_url)


def process_query_parameter(
    query_parameter,
    test_configuration: TestConfiguration,
    queue: Queue,
):
    url = test_configuration.url
    original_url = copy.deepcopy(url)
    generated_tests = 0

    # Create test for query parameter key:
    test_configuration.url = replace_query_parameter_key(
        test_configuration.test_value, query_parameter, url
    )
    test_context = "key" + json.dumps(query_parameter)
    test: Test = build_test(test_configuration, test_context)

    if persist_test(test, queue):
        generated_tests += 1

    # Reset URL
    test_configuration.url = original_url

    # Create test for query parameter value
    test_configuration.url = replace_query_parameter_value(
        test_configuration.test_value, query_parameter, url
    )
    test_context = "value" + json.dumps(query_parameter)
    test: Test = build_test(test_configuration, test_context)

    if persist_test(test, queue):
        generated_tests += 1

    # Reset URL
    test_configuration.url = original_url
    logging.debug(f"Generated {generated_tests} query parameter tests.")
    return generated_tests


def process_query_parameter_array(
    query_parameter: Dict,
    test_configuration: TestConfiguration,
    queue: Queue,
):
    url = test_configuration.url
    generated_tests = 0

    # Deep copy because this object will be altered. Do not want to alter original query parameter
    # You only want to test a single field at a time
    # Use original "happy case" but only perform test on single field
    original_url = copy.deepcopy(url)

    # Create test for query parameter key(s):
    for k in query_parameter:
        test_configuration.url = replace_query_parameter_array_key(
            test_configuration.test_value, query_parameter, original_url
        )
        test_context = k + json.dumps(query_parameter)
        test: Test = build_test(test_configuration, test_context)

        if persist_test(test, queue):
            generated_tests += 1

        # Reset Url
        test_configuration.url = original_url

        # Create test for query parameter values(s)
        for key, values in query_parameter.items():
            for parameter_value_index, current_value in enumerate(values.split(",")):
                test_configuration.url = replace_query_parameter_array_value(
                    test_configuration.test_value,
                    query_parameter,
                    parameter_value_index,
                    original_url,
                )
                test_context = key + str(parameter_value_index) + current_value
                test: Test = build_test(test_configuration, test_context)

                if persist_test(test, queue):
                    generated_tests += 1

                # Reset Url
                test_configuration.url = original_url

    logging.debug(f"Generated {generated_tests} query parameter array tests.")
    return generated_tests


def is_comma_separated_parameter_array(value):
    # Check if query parameter contains comma separated array values: param=1,2,3
    # Object looks like "{'queryParamOne': ['1,2,3']}"
    for v in value:
        if len(v.split(",")) > 1:
            return True
    return False


def replace_query_parameter_key(
    test_value: Any, query_parameter: Dict, url: str
) -> str:
    original_query_parameter = copy.deepcopy(query_parameter)
    original_url = copy.deepcopy(url)

    parameter_key = None
    parameter_value = None
    for k, v in original_query_parameter.items():
        parameter_key = k
        parameter_value = v

    new_qs: Dict = {test_value: parameter_value}
    original_qs: Dict = {parameter_key: parameter_value}
    new_query_parameter: str = create_query_string(new_qs)
    old_query_parameter: str = create_query_string(original_qs)

    return original_url.replace(old_query_parameter, new_query_parameter, 1)


def remove_query_parameter_key(parsed_url: ParseResult, query_parameter: Dict) -> str:
    logging.debug(f"Remove query param key received query parameter: {query_parameter}")
    original_query_parameter: Dict = copy.deepcopy(query_parameter)
    original_parsed_url: ParseResult = copy.deepcopy(parsed_url)
    original_parsed_query_parameters = parse_qsl(original_parsed_url.query)

    parameter_key = None
    parameter_value = None
    for k, v in original_query_parameter.items():
        parameter_key = k
        parameter_value = v
    logging.debug(f"Parameter key: {parameter_key}")
    logging.debug(f"Parameter value: {parameter_value}")

    for i, (k, v) in enumerate(original_parsed_query_parameters):
        if k == parameter_key and v == parameter_value:
            original_parsed_query_parameters.pop(i)
            break

    url = original_parsed_url._replace(
        query=create_query_string(original_parsed_query_parameters, dosequence=True)
    )
    final_url = urlunparse(url)
    return final_url


def replace_query_parameter_value(test_value: str, query_parameter: Dict, url: str):
    parameter_key = list(query_parameter.keys())[0]
    new_qs: Dict = {parameter_key: test_value}
    new_query_parameter: str = create_query_string(new_qs)
    old_query_parameter: str = create_query_string(query_parameter)
    new_url = url.replace(old_query_parameter, new_query_parameter, 1)
    return new_url


def replace_query_parameter_array_key(
    test_value: str, query_parameter: Dict, url: str
) -> str:
    # Should probably look into whether using parse_qsl and passing a Tuple in here would be better
    # instead of using string replace
    original_query_parameter = copy.deepcopy(query_parameter)
    original_url = copy.deepcopy(url)
    parameter_key = list(original_query_parameter.keys())[0]
    parameter_list = query_parameter[parameter_key]
    new_qs: Dict = {test_value: parameter_list}
    old_qs: Dict = {parameter_key: original_query_parameter[parameter_key]}
    new_query_parameter: str = create_query_string(new_qs)
    old_query_parameter: str = create_query_string(old_qs)
    return original_url.replace(old_query_parameter, new_query_parameter, 1)


def replace_query_parameter_array_value(
    test_value: Any,
    query_parameter: Dict[str, str],
    parameter_value_index,
    url: str,
) -> str:
    original_query_parameter = copy.deepcopy(query_parameter)
    original_url = copy.deepcopy(url)
    parameter_key = list(original_query_parameter.keys())[0]
    parameter_values = original_query_parameter[parameter_key]  # type: ignore
    parameter_value_list = parameter_values.split(",")
    # Replace parameter value with test value
    parameter_value_list[parameter_value_index] = test_value
    new_qs: Dict = {parameter_key: ",".join(parameter_value_list)}
    new_query: str = create_query_string(new_qs)
    old_query: str = create_query_string(original_query_parameter)
    return original_url.replace(old_query, new_query)


def create_query_string(value: Union[Dict, List[Tuple[str, str]]], dosequence=False):
    return unquote_plus(
        # Dict to query string
        urlencode(value, doseq=dosequence),
        encoding="utf-8",
    )


def process_body(
    test_configuration: TestConfiguration,
    queue: Queue,
):
    body = test_configuration.body

    original_body = copy.deepcopy(body)
    generated_tests = 0
    test_type = test_configuration.test_type
    test_value = test_configuration.test_value
    converted_test_value = get_as_type(test_type, test_value)
    # Create key tests
    keysets: list = get_keyset(body)
    for keyset in keysets:
        if should_remove_entity(test_type):
            body_to_update = copy.deepcopy(original_body)
            test_configuration.body = remove_body_key(body_to_update, keyset)
            test_context = json.dumps(keyset)
            test: Test = build_test(test_configuration, test_context)
            if persist_test(test, queue):
                generated_tests += 1
            # Reset body
            test_configuration.body = copy.deepcopy(original_body)
        else:
            # Need to check if item is actually index of list.
            # Don't want "key test" for every item in list, but only once for the whole list.
            # e.g. { "key": [1,2,3,4,5,6] }
            keyset_key = keyset.get("key")
            # Limit to test type of STRING as JSON keys must be strings
            if not isinstance(keyset_key, Number) and test_type == "STRING":
                body_to_update = copy.deepcopy(original_body)
                test_configuration.body = replace_body_key(
                    body_to_update, keyset, converted_test_value
                )
                test_context = json.dumps(keyset)
                test: Test = build_test(test_configuration, test_context)
                if persist_test(test, queue):
                    generated_tests += 1
                # Reset body
                test_configuration.body = copy.deepcopy(original_body)

            body_to_update = copy.deepcopy(original_body)
            test_configuration.body = replace_body_value(
                body_to_update, keyset, converted_test_value
            )
            test_context = json.dumps(keyset)
            test: Test = build_test(test_configuration, test_context)
            if persist_test(test, queue):
                generated_tests += 1
            # Reset body
            test_configuration.body = copy.deepcopy(original_body)
    logging.debug(f"Generated {generated_tests} body tests.")
    return generated_tests


def get_keyset(d):
    items = []

    def visit(path, key, value):
        items.append({"path": path, "key": key, "value": value})
        return key, value

    remap(d, visit=visit)
    return items


def remove_body_key(d, keyset):
    # Will remap everything except matching key. Similar to:
    # https://sedimental.org/remap.html#drop-empty-values
    # return remap(d, visit=lambda p, k, v: k != keyset.get("key"))
    def visit(path, key, value):
        if (
            path == keyset.get("path")
            and key == keyset.get("key")
            and value == keyset.get("value")
        ):
            return False
        else:
            return True

    return remap(d, visit=visit, reraise_visit=False)


def replace_body_key(d, keyset, test_value):
    def visit(path, key, value):
        if (
            path == keyset.get("path")
            and key == keyset.get("key")
            and value == keyset.get("value")
        ):
            return test_value, value
        return key, value

    return remap(d, visit=visit)


def replace_body_value(d, keyset, test_value):
    def visit(path, key, value):
        if (
            path == keyset.get("path")
            and key == keyset.get("key")
            and value == keyset.get("value")
        ):
            return key, test_value
        return key, value

    return remap(d, visit=visit)


def build_test(test_configuration, test_context: str) -> Test:
    test = Test()
    test.test_run_id = test_configuration.test_run_id
    test.test_type = test_configuration.test_type
    test.test_value = test_configuration.test_value
    # should only use values that are constant between test runs to fingerprint a request
    # hash can be used to track responses between test runs
    test.test_hash = hash_object(
        json.dumps(
            {
                "test_type": test_configuration.test_type,
                "test_value": test_configuration.test_value,
                "test_context": test_context,
                "request": {
                    "method": test_configuration.method,
                    "url": test_configuration.url,
                    "body": test_configuration.body,
                },
            }
        )
    )
    test.method = test_configuration.method
    test.url = test_configuration.url
    if test_configuration.body is None:
        test.body = None
    else:
        test.body = test_configuration.body
    if test_configuration.headers is None:
        test.headers = None
    else:
        test.headers = test_configuration.headers
    return test


def persist_test(test: Test, queue: Queue) -> bool:
    try:
        queue_item = QueueItem()
        queue_item.id = uuid.uuid4().hex
        queue_item.test_run_id = test.test_run_id
        queue_item.test_hash = test.test_hash
        queue_item.test = test.__dict__
        queue_item.create_date = datetime.utcnow()
        if os.getenv("DRY_RUN"):
            logging.info(f"DRY_RUN: {json.dumps(test.__dict__)}")
        else:
            queue.put(queue_item)
        return True
    except Exception as e:
        logging.warning(f"Could not persist generated test {test.__dict__}.")
        logging.exception(e)
        return False


def get_as_type(test_type: str, test_object: str) -> Union[int, str, float]:
    if test_type == "INTEGER":
        object_type = int(test_object)
    elif test_type == "STRING":
        object_type = str(test_object)
    elif test_type == "DOUBLE":
        object_type = float(test_object)
    else:
        object_type = str(test_object)  # default

    return object_type
