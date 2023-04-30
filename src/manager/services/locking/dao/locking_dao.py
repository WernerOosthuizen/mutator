import logging
from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from src.common.database.test_run import TestRun

log = logging.getLogger()


# Use optimistic locking with "version" column
# Looked into pessimistic locking with "select for update", but it's not supported in sqlite.
def create_lock(test_run: TestRun, lock_config: Dict, session: Session) -> bool:

    test_run.owner = lock_config.get("owner")
    test_run.lock_start_date = datetime.utcnow()
    test_run.lock_end_date = datetime.utcnow() + timedelta(
        seconds=lock_config.get("lock_interval")
    )
    session.add(test_run)

    test_run_id = test_run.id
    try:
        # This will fail with StaleDataError is the version column has been incremented by another process
        # Should not happen often, only during concurrent updates.
        session.commit()
    except StaleDataError:
        logging.error(
            f"Error getting lock for test run {test_run_id}. "
            f"It has most likely been locked by another worker."
        )
        session.rollback()
        return False
    return True
