import logging
from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session

from src.common.database.test_run import TestRun
from src.common.state.states import State
from src.manager.services.locking.dao import locking_dao


def create_lock(test_run: TestRun, lock_config: Dict, session: Session) -> bool:
    # Test run is owned and locked by someone else
    if test_run.owner is not None and test_run.lock_end_date >= datetime.utcnow():
        logging.debug(f"Test run {test_run.id} already has an owner")
        return False

    if not _in_correct_state(test_run):
        logging.debug(
            f"Test run is not in correct state: {test_run.state}. Not creating lock."
        )
        return False
    return locking_dao.create_lock(test_run, lock_config, session)


def refresh_lock(test_run: TestRun, lock_config: Dict, session: Session):
    lock_end_date = test_run.lock_end_date
    test_run_owner = test_run.owner
    required_owner = lock_config.get("owner")

    # Still owned and locked by someone else
    if test_run_owner != required_owner and test_run.lock_end_date >= datetime.utcnow():
        logging.warning(f"Not owner of test run {test_run.id}, cannot refresh lock.")
        return False

    # We are the owner, but lock expired. Can't refresh lock that is not valid.
    if (
        test_run_owner == required_owner
        and lock_end_date is not None
        and lock_end_date <= datetime.utcnow()
    ):
        logging.warning("Lock has expired. Cannot refresh.")
        return False

    return locking_dao.create_lock(test_run, lock_config, session)


def _in_correct_state(test_run: TestRun):
    if test_run.state in [
        State.PENDING.value,
        State.GENERATING.value,
        State.RUNNING.value,
    ]:
        return True
