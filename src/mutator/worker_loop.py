import json
import logging
import os
import pathlib
import random
import threading
import uuid
from configparser import ConfigParser
from queue import Queue
from time import sleep
from typing import Dict, List, Union

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.scoping import ScopedSession

from src.common.database.test_run import TestRun
from src.common.state.state_descriptions import StateDescription
from src.common.state.states import State
from src.common.test_run_dto import TestRunDto
from src.manager.services.locking.service import locking_service
from src.manager.services.test_run.service import test_run_service, test_result_service
from src.mutator.background_jobs.locking.refresh_lock import refresh_lock
from src.mutator.background_jobs.monitors.test_run_state import check_if_cancelled
from src.mutator.common.test_value_storage.test_repository import TestRepository
from src.mutator.common.utils.persistent_queue.buffer_queues.queue_reader import (
    QueueReader,
)
from src.mutator.common.utils.persistent_queue.buffer_queues.queue_writer import (
    QueueWriter,
)
from src.mutator.common.utils.persistent_queue.persistent_queue import PersistentQueue
from src.mutator.consumer import consumer
from src.mutator.producer import produce_tests

base_config_dir = (
    pathlib.Path(os.path.abspath(__file__)).parents[0].__str__() + "/config"
)
config_file_path = base_config_dir + "/config.ini"
config = ConfigParser()
config.read(config_file_path)

worker_queue_blocking_size: int = config.getint(
    "worker_queue", "worker_queue_blocking_size"
)
max_test_run_attempts: int = config.getint("worker_loop", "max_test_run_attempts")
consumer_count: int = os.getenv("CONSUMERS", config.getint("consumer", "count"))
consumer_request_timeout: int = config.getint("consumer", "request_timeout")
consumer_worker_queue_blocking_seconds: int = config.getint(
    "worker_queue", "worker_queue_blocking_seconds"
)
worker_queue_batch_write_size: int = config.getint(
    "worker_queue", "worker_queue_batch_write_size"
)
cancellation_listener_interval_seconds: int = config.getint(
    "background_jobs", "cancellation_listener_interval_seconds"
)
worker_loop_interval_seconds: int = config.getint(
    "worker_loop", "worker_loop_interval_seconds"
)
lock_interval = config.getint("background_jobs", "lock_interval_seconds")
lock_refresh_interval = config.getint("background_jobs", "refresh_interval_seconds")

if lock_interval < lock_refresh_interval:
    logging.error(
        "Config for lock_refresh_interval cannot be larger than lock_interval "
        "as the lock will run out before it is refreshed."
    )
    exit(1)
throttle_interval_seconds: int = config.getint("throttle", "throttle_interval_seconds")

# If consumers time out before throttle finishes,
# test producer throttle will finish, fill up worker queue
# and block on a full worker queue, and there will be no consumers
# to pull from the worker queue, causing a stall
if throttle_interval_seconds > consumer_worker_queue_blocking_seconds:
    logging.error(
        "Config for throttle_interval_seconds cannot be larger than consumer_worker_queue_blocking_seconds "
        "as that can potentially cause a stall in the program."
    )
    exit(1)

test_repository = TestRepository(base_config_dir, "/test_config.json")
database_url_env = os.environ.get("DATABASE")
if database_url_env is None:
    database_url = config.get("database", "database_url")
else:
    database_url = database_url_env
mutator_db_engine = create_engine(
    url=database_url,
    echo=config.getboolean("database", "echo"),
    connect_args={"timeout": config.getint("database", "timeout")}
    if "sqlite" in database_url
    else {},
)
if (
    database_url_env is None
    and "sqlite" in database_url
    and config.get("database", "database_mode") == "WAL"
):

    @event.listens_for(mutator_db_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # noqa
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


if database_url_env is None and "sqlite" in database_url:

    @event.listens_for(mutator_db_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # noqa
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


logging = logging.getLogger()


# Each validation config item must match respective class name exactly.
with open(base_config_dir + "/validator_config.json") as validation_config_file:
    default_validation_config = json.load(validation_config_file)

use_polling = os.getenv("USE_POLLING", False)


# Need to pull some of this out into its own classes
def start_worker_loop(test_run_notification_queue: Queue):
    mutator_db_session = scoped_session(sessionmaker(bind=mutator_db_engine))
    worker_name: str = uuid.uuid4().hex
    logging.info(f"STARTING MUTATOR WORKER: {worker_name}.")
    while True:
        try:
            if use_polling:
                sleep_with_jitter(0.1, 5.0)

            logging.info("Fetching test run to process.")
            stop_threads = threading.Event()

            lock_config = {
                "lock_interval": lock_interval,
                "lock_refresh_interval": lock_refresh_interval,
                "owner": worker_name,
            }

            new_test_run = get_test(
                lock_config, test_run_notification_queue, mutator_db_session
            )
            if not new_test_run:
                continue
            test_run: TestRun = TestRun(**new_test_run)

            run_attempts = 0 if not test_run.run_attempts else test_run.run_attempts
            logging.debug(f"Run attempts: {run_attempts}")
            if reached_max_test_run_attempts(run_attempts, max_test_run_attempts):
                logging.info(
                    f"Test reached max run attempts. Updating test run {test_run.id} state to {State.FAILED.value}."
                )
                update_test_run_state(
                    test_run,
                    State.FAILED,
                    StateDescription.MAXIMUM_RUN_ATTEMPTS,
                    mutator_db_session,
                    False,
                )
                continue

            logging.debug(f"Incrementing test run {test_run.id} run attempts by 1.")

            test_run_update = TestRun()
            test_run_update.id = test_run.id
            test_run_update.run_attempts = run_attempts + 1
            with mutator_db_session() as session:
                test_run_service.update_test_run(test_run_update, session)

            logging.info("Starting test generation.")
            # keep lock updated
            lock_refresher_thread = start_lock_refresher(
                test_run, lock_config, stop_threads, mutator_db_session
            )
            logging.debug(f"Creating local worker queue for test run {test_run.id}.")
            worker_queue: Queue = Queue(maxsize=worker_queue_blocking_size)
            remove_old_tests(mutator_db_session, test_run)

            persistent_queue: PersistentQueue = PersistentQueue(
                test_run.id, mutator_db_session
            )
            # Remove any old tests for test run id to start fresh
            persistent_queue.remove_all()
            update_test_run_state(
                test_run,
                State.GENERATING,
                StateDescription.GENERATING,
                mutator_db_session,
            )

            # Setup and start buffered test run writer to batch save tests to persistent queue
            buffer_queue = Queue(maxsize=worker_queue_batch_write_size)
            queue_writer = QueueWriter(
                buffer_queue, persistent_queue, stop_threads, test_run.id
            )
            queue_writer_thread = threading.Thread(target=queue_writer.write_queue)
            queue_writer_thread.start()

            test_count: int = produce_tests(test_repository, test_run, buffer_queue)
            update_test_count(test_run, test_count, mutator_db_session)
            if test_count == 0:
                update_test_run_state(
                    test_run,
                    State.FAILED,
                    StateDescription.TEST_GENERATION_FAILURE,
                    mutator_db_session,
                    False,
                )
                stop_threads.set()
                continue

            if os.getenv("DRY_RUN"):
                logging.info("DRY RUN: Finished generating tests for the dry run.")
                update_test_run_state(
                    test_run,
                    State.COMPLETED,
                    StateDescription.SUCCESS_DRY_RUN,
                    mutator_db_session,
                )
                stop_threads.set()
                continue

            update_test_run_state(
                test_run, State.RUNNING, StateDescription.RUNNING, mutator_db_session
            )

            # Incrementally load persisted tests into in-memory queue for test runners
            test_queue_reader_thread = start_test_queue_reader(
                test_run,
                persistent_queue,
                worker_queue,
                stop_threads,
                mutator_db_session,
            )

            # Run test runners
            logging.info("Running tests.")
            # Get Overridden configs
            validation_config = update_config(
                test_run.config, default_validation_config, "validation"
            )

            consumers = start_consumers(
                mutator_db_session, stop_threads, validation_config, worker_queue
            )
            canceller_thread = start_cancellation_monitoring(
                test_run, stop_threads, mutator_db_session
            )
            # Wait for threads to stop
            # Consumers first in case they time out
            for consumer_thread in consumers:
                consumer_thread.join()
            test_queue_reader_thread.join()

            logging.info(f"Finished running tests for test run {test_run.id}.")
            logging.info("Processing test results to see if test run passed.")
            with mutator_db_session() as session:
                final_test_run: TestRun = test_run_service.get_test_run(
                    test_run.id, session
                )

            if can_process_test_results(final_test_run):
                test_result_failures = get_failed_tests(test_run, mutator_db_session)
                logging.debug(f"Finalizing state for test: {final_test_run.__dict__}")
                test_run_final_update = create_final_test_run_state(
                    test_run, final_test_run, test_result_failures
                )
                with mutator_db_session() as session:
                    test_run_service.update_test_run(test_run_final_update, session)
            else:
                logging.info(
                    f"Test run already in state {final_test_run.state}. Not processing test results"
                )

            logging.info("Test run is finished. Performing clean up.")
            logging.info("Stopping background threads.")
            if not stop_threads.is_set():
                stop_threads.set()
            lock_refresher_thread.join()
            canceller_thread.join()
            logging.info("Background threads stopped.")
            clean_up_test_queue(persistent_queue)
            logging.info("Cleanup complete.")
            logging.info("Finished with test run.")
        except Exception as e:
            logging.exception(f"INVESTIGATE THIS: General error in worker loop: {e}")
            # This might error out if test_run has been not been instantiated, but exception is logged already.
            update_test_run_state(
                test_run,
                State.FAILED,
                StateDescription.GENERAL_FAILURE,
                mutator_db_session,
                False,
            )


def can_process_test_results(final_test_run):
    return final_test_run.state != (State.CANCELLED.value or State.FAILED.value)


def clean_up_test_queue(persistent_queue: PersistentQueue):
    if persistent_queue.size() != 0:
        logging.warning("Test queue is not empty, removing old tests.")
        persistent_queue.remove_all()
        logging.warning(
            f"Test queue size after old test removal: {persistent_queue.size()}."
        )


def get_failed_tests(test_run: TestRun, mutator_db_session: ScopedSession):
    with mutator_db_session() as session:
        test_result_failures: List[Dict] = test_result_service.get_tests(
            {"test_run_id": test_run.id, "passed": 0}, session
        )
    return test_result_failures


def create_final_test_run_state(
    test_run: TestRun, final_test_run: TestRun, test_result_failures: List[Dict]
) -> TestRun:
    test_run_final_update = TestRun()
    test_run_final_update.id = test_run.id
    if final_test_run.test_generated_count == final_test_run.test_result_count:
        # All tests completed
        test_run_final_update.state = State.COMPLETED.value
        test_run_final_update.state_description = StateDescription.SUCCESS.value
        test_run_final_update.passed = False if test_result_failures else True
    else:
        test_run_final_update.state = State.FAILED.value
        test_run_final_update.passed = False
        test_run_final_update.state_description = (
            StateDescription.TEST_COUNT_MISMATCH.value
        )
    return test_run_final_update


def get_test(
    lock_config: Dict,
    test_run_notification_queue: Queue,
    mutator_db_session: ScopedSession,
) -> Union[Dict, None]:
    try:
        # First check DB to pick up any stragglers
        with mutator_db_session() as session:
            new_test_run: Dict = test_run_service.get_unprocessed_test_run(
                lock_config, session
            )
        if not new_test_run:
            # Wait for notification for new test run
            if use_polling or not test_run_notification_queue:
                return None
            logging.info("No test run found. Waiting for new test run.")
            test_run_id: int = test_run_notification_queue.get()
            with mutator_db_session() as session:
                test_run_to_lock: TestRun = test_run_service.get_test_run(
                    test_run_id, session
                )
                if locking_service.create_lock(test_run_to_lock, lock_config, session):
                    new_test_run: Dict = TestRunDto().dump(test_run_to_lock)
                else:
                    return None

        logging.debug(f"Pulled test run off queue: {new_test_run}")
        return new_test_run

    except Exception as e:
        logging.exception(f"Could not pull test off queue due to exception: {e}.")
        return None


def start_lock_refresher(
    test_run: TestRun,
    lock_config: Dict,
    stop_threads: threading.Event,
    mutator_db_session: ScopedSession,
):
    lock_refresher_thread = threading.Thread(
        target=refresh_lock,
        args=(
            test_run,
            lock_refresh_interval,
            lock_config,
            stop_threads,
            mutator_db_session,
        ),
    )
    lock_refresher_thread.start()
    return lock_refresher_thread


def start_test_queue_reader(
    test_run: TestRun,
    persistent_queue: PersistentQueue,
    worker_queue: Queue,
    stop_threads: threading.Event,
    mutator_db_session: ScopedSession,
):
    queue_reader: QueueReader = QueueReader(
        persistent_queue,
        worker_queue,
        stop_threads,
        test_run.id,
        mutator_db_session,
    )
    queue_reader_thread = threading.Thread(target=queue_reader.read_queue)
    queue_reader_thread.start()
    return queue_reader_thread


def start_cancellation_monitoring(
    test_run: TestRun, stop_threads: threading.Event, mutator_db_session: ScopedSession
):
    # listen for test run cancellation notices
    canceller_thread = threading.Thread(
        target=check_if_cancelled,
        args=(
            test_run,
            State.CANCELLED,
            cancellation_listener_interval_seconds,
            stop_threads,
            mutator_db_session,
        ),
    )
    canceller_thread.start()
    return canceller_thread


def start_consumers(
    mutator_db_session: ScopedSession,
    stop_threads: threading.Event,
    validation_config: Dict,
    worker_queue: Queue,
):
    consumers: List[threading.Thread] = [
        threading.Thread(
            target=consumer,
            args=(
                worker_queue,
                consumer_worker_queue_blocking_seconds,
                validation_config,
                stop_threads,
                mutator_db_session,
            ),
        )
        for _ in range(consumer_count)
    ]
    for consumer_thread in consumers:
        consumer_thread.start()
    return consumers


def update_test_run_state(
    test_run: TestRun,
    state: State,
    state_description: StateDescription,
    mutator_db_session: ScopedSession,
    passed=None,
):
    test_run_update = TestRun()
    test_run_update.id = test_run.id
    test_run_update.state = state.value
    test_run_update.state_description = state_description.value
    if passed is not None:
        test_run_update.passed = passed
    logging.info(f"Updating test run {test_run.id} state to {state}.")
    with mutator_db_session() as session:
        test_run_service.update_test_run(test_run_update, session)


def update_test_count(
    test_run: TestRun, test_count: int, mutator_db_session: ScopedSession
):
    logging.debug(f"Updating test run {test_run.id} test count to {test_count}.")
    test_run_update = TestRun()
    test_run_update.id = test_run.id
    test_run_update.test_generated_count = test_count
    with mutator_db_session() as session:
        test_run_service.update_test_run(test_run_update, session)


def remove_old_tests(mutator_db_session: ScopedSession, test_run: TestRun):
    # If not running test run for first time, clean out old tests
    if test_run.state != State.PENDING.value:
        logging.warning(
            f"Test run {test_run.id} is not in a {State.PENDING.value} state. Removing old tests and running again."
        )
        with mutator_db_session() as session:
            test_result_service.delete_all_tests(test_run.id, session)


def sleep_with_jitter(add_time_lower: float, add_time_upper: float):
    final_sleep_value = worker_loop_interval_seconds + random.uniform(  # nosec
        add_time_lower, add_time_upper
    )
    sleep(final_sleep_value)


def update_config(test_run_config: Dict, default_config: Dict, config_type: str):
    if test_run_config is None:
        return default_config

    overridden_config = test_run_config.get(config_type)
    if overridden_config is None:
        return default_config
    else:
        return default_config | overridden_config


def reached_max_test_run_attempts(run_attempts: int, max_attempts: int) -> bool:
    logging.debug(f"Test run has been attempted {run_attempts} times.")
    if run_attempts >= max_attempts:
        logging.warning(
            f"Test run has been attempted more than {max_attempts} times. "
            f"Failing test run."
        )
        return True
    else:
        return False
