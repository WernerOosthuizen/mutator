from datetime import datetime
from typing import Dict, List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.common.database.database_utils import add_pagination, add_sorting
from src.common.database.test_run import TestRun
from src.common.state.states import State


def create_pending_test_run(test_run: TestRun, session: Session) -> TestRun:
    test_run.create_date = datetime.utcnow()
    test_run.last_update_date = datetime.utcnow()
    session.add(test_run)
    session.commit()
    return test_run


def create_pending_test_run_batch(
    test_runs: List[TestRun], session: Session
) -> List[TestRun]:
    date = datetime.utcnow()
    # Not using bulk_save_objects as I want to return id
    for test_run in test_runs:
        test_run.create_date = date
        test_run.last_update_date = date
        session.add(test_run)
    session.commit()
    return test_runs


def update_test_run(test_run_incoming: TestRun, session: Session) -> bool:
    test_run_update = {}
    if test_run_incoming.state is not None:
        test_run_update["state"] = test_run_incoming.state

    if test_run_incoming.state_description is not None:
        test_run_update["state_description"] = test_run_incoming.state_description

    if test_run_incoming.passed is not None:
        test_run_update["passed"] = test_run_incoming.passed

    if test_run_incoming.test_generated_count is not None:
        test_run_update["test_generated_count"] = test_run_incoming.test_generated_count

    if test_run_incoming.test_result_count is not None:
        test_run_update["test_result_count"] = test_run_incoming.test_result_count

    if test_run_incoming.run_attempts is not None:
        test_run_update["run_attempts"] = test_run_incoming.run_attempts

    test_run_update["last_update_date"] = datetime.utcnow()

    updated = (
        session.query(TestRun)
        .filter(TestRun.id == test_run_incoming.id)
        .update(test_run_update)
    )

    session.commit()
    return updated


def get_single_test_run(test_run_id: int, session: Session) -> TestRun:
    return session.query(TestRun).filter(TestRun.id == test_run_id).first()


def get_unprocessed_test_run(session: Session) -> [TestRun, None]:
    valid_states = [State.PENDING.value, State.GENERATING.value, State.RUNNING.value]

    # order by create date asc to process in order that they were created in
    return (
        session.query(TestRun)
        .filter(TestRun.state.in_(valid_states))
        .filter(
            or_(
                TestRun.lock_end_date < datetime.utcnow(),
                TestRun.lock_end_date.is_(None),
            )
        )
        .order_by(TestRun.create_date.asc())
        .first()
    )


def get_all_test_runs(filters: Dict, session: Session):
    query = session.query(TestRun)

    batch_id = filters.get("batch_id")
    if batch_id is not None:
        query = query.filter(TestRun.batch_id == batch_id)

    state = filters.get("state")
    if state is not None:
        query = query.filter(TestRun.state == state)

    passed = filters.get("passed")
    if passed is not None:
        query = query.filter(TestRun.passed == passed)

    query = add_sorting(query, TestRun.id, filters)
    query = add_pagination(query, filters)
    return query.all()
