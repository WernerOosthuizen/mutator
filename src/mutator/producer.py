import logging
from queue import Queue
from time import sleep

from src.common.database.test_run import TestRun
from src.mutator.common.test_value_storage.test_repository import TestRepository
from src.mutator.generator import generator


def produce_tests(
    test_config: TestRepository, test: TestRun, buffer_queue: Queue
) -> int:
    logging.debug("Starting to produce tests")
    total_generated_tests = 0
    try:
        total_generated_tests += generator.generate(test_config, test, buffer_queue)
    except Exception as e:
        logging.exception(f"Exception occurred when generating tests: {e}")
        raise e

    # Give buffered writer time to finish, it flushes tests every 1 second
    while buffer_queue.qsize() > 0:
        sleep(2)
    logging.debug("Finished producing tests")
    return total_generated_tests
