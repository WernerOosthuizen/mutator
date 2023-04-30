from typing import List, Dict

from sqlalchemy.orm import Session

from src.common.database.result import Result
from src.manager.services.test_run.dao import (
    test_result_dao,
)
from src.manager.services.test_run.dto.test_results_dto import TestResultsDto


def get_tests(filters: Dict, session: Session) -> List[Dict]:
    test_results: List[Result] = test_result_dao.get_test_results(filters, session)
    response_list: List[Dict] = []
    if test_results is not None:
        for test_result in test_results:
            response: Dict = TestResultsDto().dump(test_result)
            response_list.append(response)
    return response_list


def get_specific_test(test_data: Dict, session: Session) -> Dict:
    test_result: Result = test_result_dao.get_single_test(test_data, session)
    response = {}
    if test_result is not None:
        response: Dict = TestResultsDto().dump(test_result)
    return response


def delete_all_tests(test_run_id: int, session: Session):
    test_result_dao.delete_all_tests(test_run_id, session)
