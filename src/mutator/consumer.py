import logging
import threading
from queue import Queue, Empty
from typing import Dict

from requests import Session
from sqlalchemy.orm.scoping import ScopedSession

from src.common.test_result.test_result import TestResult
from src.mutator.generator.test import Test
from src.mutator.result_processor.service import result_processor_service
from src.mutator.runner import test_runner
from src.mutator.runner.hash_strategy import HashStrategy


def consumer(
    test_queue: Queue,
    consumer_worker_queue_blocking_seconds,
    new_validation_config,
    stop_threads: threading.Event,
    db_session: ScopedSession,
):
    test_run_counter = 0
    test_persisted_counter = 0
    logging.debug("Consumer: Pulling tests from worker queue.")
    request_session = Session()
    regression_config = new_validation_config.get("Regression")
    if regression_config:
        field_matcher = build_field_matcher(regression_config)
    else:
        field_matcher = None

    while not stop_threads.is_set():
        try:
            logging.debug("Pulling message from worker queue.")
            logging.debug(
                f"Worker queue size before consumer pulled item: {test_queue.qsize()}"
            )
            test: Test = test_queue.get(
                block=True, timeout=consumer_worker_queue_blocking_seconds
            )
            if test is None:
                logging.warning("Worker queue empty, no more tests to pull. ")
                break

            logging.debug(
                f"Worker queue size after consumer pulled item: {test_queue.qsize()} "
            )
            logging.debug(f"Consumer pulled raw message from queue: {test.__dict__} ")
            test_run_id = test.test_run_id
            logging.debug(f"Consumer: Running test for {test_run_id}.")
            test_result: TestResult = test_runner.run(
                test, field_matcher, request_session
            )
            test_run_counter += 1
            if test_result is not None:
                test_result.test_run_id = test_run_id
                test_result.test_type = test.test_type
                test_result.test_value = test.test_value
                try:
                    logging.debug(
                        f"Attempting to process test result: {test_result.__dict__}"
                    )

                    with db_session() as session:
                        result_processor_service.process_test_result(
                            test_result, new_validation_config, session
                        )
                    test_persisted_counter += 1
                except Exception as e:
                    logging.exception(
                        f"Issue while validating and persisting test result: {e}"
                    )
            else:
                logging.warning(
                    f"INVESTIGATE THIS: There is no test result for test: {test}. This should not happen."
                )
            logging.debug(f"Consumer: Finished running test for {test_run_id}")
        except Empty:
            logging.debug(
                "Caught Empty Exception in worker queue. No more tests to pull."
            )
            break
        except Exception as e:
            logging.exception(
                "General Exception in consumer. Exiting consumer and stopping test run.",
                e,
            )
            stop_threads.set()

    # End Consumer
    logging.info(
        f"Consumer Stats. Tests ran: {test_run_counter}. Tests persisted: {test_persisted_counter}"
    )
    request_session.close()
    if not stop_threads.is_set():
        stop_threads.set()


def build_field_matcher(hash_generation: Dict):
    field_names = hash_generation.get("field_names")
    hash_strategy = hash_generation.get("strategy")

    if hash_strategy == HashStrategy.INCLUDE_EXACT_MATCH.name:
        field_names_set = set(field_names)
        return lambda p, k, v: k in field_names_set
    elif hash_strategy == HashStrategy.EXCLUDE_EXACT_MATCH.name:
        field_names_set = set(field_names)
        return lambda p, k, v: k not in field_names_set
    elif hash_strategy == HashStrategy.EXCLUDE_PARTIAL_MATCH.name:
        return lambda p, k, v: not any(
            field_name in str(k) for field_name in field_names
        )
    else:
        return None
