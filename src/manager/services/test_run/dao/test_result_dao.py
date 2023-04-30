import logging
from typing import Union, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.common.database.database_utils import add_sorting, add_pagination
from src.common.database.result import Result
from src.common.database.validation_result import ValidationResult


def get_test_results(filters: Dict, session: Session):
    query = session.query(Result).join(ValidationResult)

    test_run_id = filters.get("test_run_id")
    if test_run_id is not None:
        query = query.filter(Result.test_run_id == test_run_id)

    request_hash = filters.get("request_hash")
    if request_hash is not None:
        query = query.filter(Result.request_hash == request_hash)

    passed = filters.get("passed")
    if passed is not None:
        query = query.filter(Result.passed == passed)

    test_type = filters.get("test_type")
    if test_type is not None:
        query = query.filter(Result.test_type == test_type)

    test_value = filters.get("test_value")
    if test_value is not None:
        query = query.filter(Result.test_value == test_value)

    method = filters.get("method")
    if method is not None:
        query = query.filter(Result.request_method == method)

    request_url = filters.get("request_url")
    if request_url is not None:
        query = query.filter(Result.request_url == request_url)

    response_status_code = filters.get("response_status_code")
    if response_status_code is not None:
        query = query.filter(Result.response_status_code == response_status_code)

    validation_type = filters.get("validation_type")
    if validation_type is not None:
        query = query.filter(ValidationResult.type == validation_type)

    validation_passed = filters.get("validation_passed")
    if validation_passed is not None:
        query = query.filter(ValidationResult.passed == validation_passed)

    query = add_sorting(query, Result.id, filters)
    query = add_pagination(query, filters)
    return query.all()


def get_single_test(test_data: Dict, session: Session):
    query = session.query(Result)
    test_run_id = test_data.get("test_run_id")
    if test_run_id is not None:
        query = query.filter(Result.test_run_id == test_run_id)

    request_hash = test_data.get("request_hash")
    if request_hash is not None:
        query = query.filter(Result.request_hash == request_hash)

    return query.first()


def get_previous_response_hash(request_hash: str, session: Session) -> Union[str, None]:
    logging.debug(f"Getting result for {request_hash} from Database.")
    result: Result = (
        session.query(Result)
        .filter(Result.request_hash == request_hash)
        .order_by(Result.create_date.desc())
        .first()
    )
    if result is not None:
        return result.response_hash
    else:
        return None


def delete_all_tests(test_run_id: int, session: Session):
    validation_sql = "delete from validation where test_result_id in (select id from test_result where test_run_id = :test_run_id);"
    session.execute(text(validation_sql), {"test_run_id": test_run_id})
    test_result_query = session.query(Result).filter(Result.test_run_id == test_run_id)
    test_result_query.delete()
    session.commit()
