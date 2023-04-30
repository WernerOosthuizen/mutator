from dataclasses import dataclass, field
from typing import List

from src.mutator.runner.request.generic_request import GenericRequest
from src.mutator.runner.response.generic_response import GenericResponse


@dataclass(init=False)
class TestResult:
    test_run_id: int
    test_type: str
    test_value: str
    request = GenericRequest
    response = GenericResponse
    validations: List = field(default_factory=lambda: [])
