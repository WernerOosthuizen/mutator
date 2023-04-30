from dataclasses import dataclass


@dataclass(init=False)
class Test:
    test_run_id: int
    test_value: str
    test_type: str
    test_hash: str
    method: str
    headers: str
    url: str
    body: str
