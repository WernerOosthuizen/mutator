import logging
import threading
from time import sleep

from sqlalchemy.orm.scoping import ScopedSession

from src.common.database.test_run import TestRun
from src.common.state.states import State
from src.manager.services.test_run.service import test_run_service


def check_if_cancelled(
    test_run: TestRun,
    monitored_state: State,
    sleep_interval,
    stop_threads: threading.Event,
    db_session: ScopedSession,
):
    logging.debug("Starting test run state monitor.")
    required_state: str = monitored_state.value
    while not stop_threads.is_set():
        try:
            with db_session() as session:
                current_test: TestRun = test_run_service.get_test_run(
                    test_run.id, session
                )

            logging.debug(f"Checking test state to see if it matches {required_state}.")
            logging.debug(f"Incoming test_state response: {current_test}")

            if current_test.state == required_state:
                logging.warning(
                    f"Test run {current_test.id} is now in a state of {required_state}. Stopping test run."
                )
                stop_threads.set()
                logging.warning("Stopped test run.")
                break
            else:
                logging.debug(
                    f"Test run {current_test.id} is in state {current_test.state}. "
                    f"Not cancelling."
                )

        except Exception as e:
            logging.exception(f"Error during cancellation notice check: {e}")
        finally:
            logging.debug(
                f"Sleeping for {sleep_interval} seconds before checking cancellation queue again."
            )
            sleep(sleep_interval)
            continue
    logging.debug(
        "All tasks have been completed. Exiting cancellation notification listener."
    )
