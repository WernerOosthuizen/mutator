import logging
import os
import pathlib
from configparser import ConfigParser
from dataclasses import dataclass
from queue import Queue, Full
from threading import Event
from time import sleep
from typing import List

from ratelimit import sleep_and_retry, limits
from sqlalchemy.orm.scoping import ScopedSession

from src.common.database.test_run import TestRun
from src.manager.services.test_run.service import test_run_service
from src.mutator.common.utils.persistent_queue.dao.queue_item import QueueItem
from src.mutator.common.utils.persistent_queue.persistent_queue import PersistentQueue
from src.mutator.generator.test import Test

config = ConfigParser()
config.read(
    pathlib.Path(os.path.abspath(__file__)).parents[4].__str__() + "/config/config.ini"
)

throttle_test_run: bool = config.getboolean("throttle", "throttle_test_run")
throttle_tests_per_interval: int = config.getint(
    "throttle", "throttle_tests_per_interval"
)
throttle_interval_seconds: int = config.getint("throttle", "throttle_interval_seconds")
throttle_timeout: int = config.getint("throttle", "throttle_timeout")
throttle_timeout_max_retries: int = config.getint(
    "throttle", "throttle_timeout_max_retries"
)
throttle_timeout_retry_sleep_interval_seconds: int = config.getint(
    "throttle", "throttle_timeout_retry_sleep_interval_seconds"
)
worker_queue_batch_read_size: int = config.getint(
    "worker_queue", "worker_queue_batch_read_size"
)


@dataclass
class QueueReader:
    persistent_queue: PersistentQueue
    worker_queue: Queue
    stop_threads: Event
    test_run_id: int
    scoped_session: ScopedSession

    def read_queue(self):
        total_size = self.persistent_queue.size()
        progress_counter: int = 0

        logging.debug(
            f"Starting to populate {total_size} tests from local persisted queue into worker queue."
        )
        while not self.stop_threads.is_set():
            try:
                logging.debug("Fetch item from persisted queue.")
                queue_items: List[QueueItem] = self.persistent_queue.pop(
                    worker_queue_batch_read_size
                )
                if queue_items is None or len(queue_items) == 0:
                    logging.debug(
                        "No item found in persisted queue, exiting queue populator."
                    )
                    break
                for queue_item in queue_items:
                    test = self.create_test(queue_item)
                    logging.debug(
                        f"Fetched from persistent queue: {test.__dict__}. Pushing to worker queue."
                    )
                    # attempt to push to queue X times, but check if test run has ended between attempts
                    for i in range(throttle_timeout_max_retries):
                        try:
                            if not self.stop_threads.is_set():
                                self.push_to_consumer_queue(test, throttle_test_run)
                                break
                        except Full:
                            if i == throttle_timeout_max_retries:
                                logging.error(
                                    "Maximum attempts reached while trying to populate worker queue. "
                                    "Something went wrong. Stopping test run."
                                )
                                self.stop_threads.set()
                            logging.warning(
                                f"Queue Populator timed out while populating worker queue. "
                                f"Iteration {i} of {throttle_timeout_max_retries}. "
                                f"Sleeping {throttle_timeout_retry_sleep_interval_seconds} seconds then retrying."
                            )
                            sleep(throttle_timeout_retry_sleep_interval_seconds)
                progress_counter += len(queue_items)
                self.update_progress(progress_counter, total_size)
                if not self.persistent_queue.ack(queue_items):
                    logging.error("INVESTIGATE THIS: Did not ack queue items.")
            except Exception as e:
                logging.exception(f"Error while populating worker queue: {e}")
                self.stop_threads.set()

    def create_test(self, queue_item):
        test_data: dict = queue_item.test
        test: Test = Test()
        test.test_run_id = test_data.get("test_run_id")
        test.test_value = test_data.get("test_value")
        test.test_type = test_data.get("test_type")
        test.test_hash = test_data.get("test_hash")
        test.method = test_data.get("method")
        test.headers = test_data.get("headers")
        test.url = test_data.get("url")
        test.body = test_data.get("body")
        return test

    def push_to_consumer_queue(self, queue_item, throttle):
        if throttle:
            self.push_to_queue_throttled(queue_item)
        else:
            self.worker_queue.put(queue_item, timeout=throttle_timeout)

    def update_progress(self, progress_counter, total_size):
        logging.info(
            f"Test run id {self.test_run_id} progress: {progress_counter} of {total_size}"
        )
        with self.scoped_session() as session:
            test_run = TestRun()
            test_run.id = self.test_run_id
            test_run.test_result_count = progress_counter
            test_run_service.update_test_run(test_run, session)

    @sleep_and_retry
    @limits(calls=throttle_tests_per_interval, period=throttle_interval_seconds)
    def push_to_queue_throttled(self, queue_item):
        self.worker_queue.put(queue_item, timeout=throttle_timeout)
