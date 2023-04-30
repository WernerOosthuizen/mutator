from dataclasses import dataclass
from datetime import datetime

from src.common.database.result import Result


@dataclass
class TestResultsDto:
    def dump(self, test_result: Result):
        return {
            "test_run_id": test_result.test_run_id,
            "test_type": test_result.test_type,
            "test_value": test_result.test_value,
            "passed": test_result.passed,
            "request": {
                "hash": test_result.request_hash,
                "method": test_result.request_method,
                "headers": test_result.request_headers,
                "url": test_result.request_url,
                "body": test_result.request_body,
            },
            "response": {
                "hash": test_result.response_hash,
                "headers": test_result.response_headers,
                "body": test_result.response_body,
                "status_code": test_result.response_status_code,
            },
            "validations": [
                {
                    "type": validation.type,
                    "passed": validation.passed,
                    "message": validation.message,
                }
                for validation in test_result.validations
            ],
            "create_date": datetime.strftime(
                test_result.create_date, "%Y-%m-%dT%H:%M:%S"
            ),
        }
