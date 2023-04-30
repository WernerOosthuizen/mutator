from dataclasses import dataclass

from src.mutator.common.test_value_storage.test_repository import TestRepository


@dataclass(init=False)
class TestConfiguration:
    method = None
    headers = None
    url = None
    body = None
    test_type: str
    test_value: str
    test_count = None
    test_run_id = None
    test_repository: TestRepository
