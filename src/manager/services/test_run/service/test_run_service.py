import logging
import uuid
from queue import Queue
from typing import List, Dict

from sqlalchemy.orm import Session
from werkzeug.exceptions import (
    BadRequest,
    NotFound,
)

from src.common.database.test_run import TestRun
from src.common.state.state_descriptions import StateDescription
from src.common.state.states import State
from src.common.test_run_dto import TestRunDto
from src.manager.services.locking.service import locking_service
from src.manager.services.test_run.dao import (
    test_run_dao,
)


def create_test_run(
    test_run_incoming: Dict, test_run_notification_queue: Queue, session: Session
) -> Dict:
    test_run = TestRun()
    test_run.endpoint = test_run_incoming.get("endpoint")
    test_run.config = test_run_incoming.get("config")
    test_run.state = State.PENDING.value
    test_run.state_description = StateDescription.PENDING.value
    persisted_test_run: TestRun = test_run_dao.create_pending_test_run(
        test_run, session
    )
    if test_run_notification_queue is not None:
        test_run_notification_queue.put(persisted_test_run.id)
    return TestRunDto().dump(persisted_test_run)


def create_test_run_batch(
    test_run_batch: Dict, test_run_notification_queue: Queue, session: Session
) -> List[Dict]:
    test_runs: List[TestRun] = []
    batch_id: str = uuid.uuid4().hex
    common_values = test_run_batch.get("common")

    for endpoint in test_run_batch.get("endpoints"):
        current_endpoint = endpoint.get("endpoint")
        current_config = endpoint.get("config")
        test_run: TestRun = TestRun()
        current_endpoint["headers"] = get_headers(common_values, current_endpoint)
        test_run.endpoint = current_endpoint
        test_run.config = get_config(common_values, current_config)
        test_run.batch_id = batch_id
        test_run.state = State.PENDING.value
        test_run.state_description = StateDescription.PENDING.value
        test_runs.append(test_run)
    persisted_test_runs: List[TestRun] = test_run_dao.create_pending_test_run_batch(
        test_runs, session
    )
    test_run_batch_response: List[Dict] = []
    for persisted_test_run in persisted_test_runs:
        test_run_batch_response.append(TestRunDto().dump(persisted_test_run))
        test_run_notification_queue.put(persisted_test_run.id)

    return test_run_batch_response


def get_headers(common_values, current_endpoint):
    current_headers = current_endpoint.get("headers")

    if common_values is None:
        return current_headers

    common_headers = common_values.get("headers")
    headers = {}
    if current_headers is not None and common_headers is None:
        headers = current_headers
    elif current_headers is None and common_headers is not None:
        headers = common_headers
    elif current_headers is not None and common_headers is not None:
        headers = current_headers | common_headers
    return headers


def get_config(common_config_values, current_config):
    if common_config_values is None:
        return current_config
    common_config = common_config_values.get("config")
    if current_config is not None and common_config is None:
        current_config = current_config
    elif current_config is None and common_config is not None:
        current_config = common_config
    elif current_config is not None and common_config is not None:
        current_config = current_config | common_config
    return current_config


def update_test_run(test_run_incoming: TestRun, session: Session) -> bool:
    return test_run_dao.update_test_run(test_run_incoming, session)


def get_unprocessed_test_run(lock_config: Dict, session: Session) -> [TestRun, None]:
    test_run: TestRun = test_run_dao.get_unprocessed_test_run(session)
    if test_run is None:
        return None

    if not locking_service.create_lock(test_run, lock_config, session):
        return None
    else:
        return TestRunDto().dump(test_run)


def get_test_run_external(test_run_id: int, session: Session) -> Dict:
    test_run: TestRun = test_run_dao.get_single_test_run(test_run_id, session)
    if test_run is None:
        raise NotFound()

    logging.debug(f"Found testrun info in DB: {test_run.__dict__}")
    return TestRunDto().dump(test_run)


def get_test_run(test_run_id: int, session: Session) -> TestRun:
    return test_run_dao.get_single_test_run(test_run_id, session)


def get_all_test_runs(filters: Dict, session: Session) -> List[Dict]:
    test_runs = test_run_dao.get_all_test_runs(filters, session)
    response_list = []
    if test_runs is not None:
        for test_run in test_runs:
            logging.debug(f"Found in DB: {test_run.__dict__}")
            response_list.append(TestRunDto().dump(test_run))

    return response_list


def cancel_test_run(test_run_id: int, session: Session):
    final_test_run: TestRun = test_run_dao.get_single_test_run(test_run_id, session)

    if final_test_run is None:
        raise NotFound()

    logging.debug(f"TestRun state is {final_test_run.state}")

    valid_states = [State.PENDING.value, State.GENERATING.value, State.RUNNING.value]
    if final_test_run.state in valid_states:
        final_test_run.state = State.CANCELLED.value
        final_test_run.state_description = StateDescription.CANCELLED.value
        if test_run_dao.update_test_run(final_test_run, session) is not None:
            logging.info(
                f"Updated test run {test_run_id} state to {State.CANCELLED.value}."
            )
        else:
            logging.error(
                f"Could NOT update test run {test_run_id} state to {State.CANCELLED.value}."
            )
    else:
        raise BadRequest(
            f"Can only cancel a test run with states: {valid_states}. "
            f"Current state is {final_test_run.state}."
        )

    test_run_response = test_run_dao.get_single_test_run(final_test_run.id, session)
    return TestRunDto().dump(test_run_response)
