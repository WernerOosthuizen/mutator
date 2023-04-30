import logging
import threading
from time import sleep
from typing import Dict

from sqlalchemy.orm.scoping import ScopedSession

from src.common.database.test_run import TestRun
from src.manager.services.locking.service import locking_service
from src.manager.services.test_run.service import test_run_service


def refresh_lock(
    test_run: TestRun,
    lock_refresh_interval: int,
    lock_config: Dict,
    stop_threads: threading.Event,
    db_session: ScopedSession,
) -> None:
    while not stop_threads.is_set():
        logging.debug("Starting lock service with sleep.")
        sleep(lock_refresh_interval)
        try:
            test_run_id = test_run.id
            logging.debug(f"Attempting to refresh lock for test run: {test_run_id}.")
            with db_session() as session:
                test_run_info: TestRun = test_run_service.get_test_run(
                    test_run_id, session
                )
                locked = locking_service.refresh_lock(
                    test_run_info, lock_config, session
                )
            if not locked:
                logging.warning(
                    f"Could not refresh lock for test run {test_run_id}. Stopping test run."
                )
                stop_threads.set()
                break

            logging.debug(f"Lock refreshed for test run {test_run_id}.")
        except Exception as e:
            logging.exception(f"Exception occurred in main refresh lock loop: {e}")
    logging.debug("All tasks are completed, not refreshing lock for test run.")
