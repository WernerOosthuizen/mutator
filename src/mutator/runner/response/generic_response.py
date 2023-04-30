from dataclasses import dataclass
from typing import Dict


@dataclass(init=False)
class GenericResponse:
    hash: str
    url: str
    headers: Dict
    body: Dict
    status_code: int
    elapsed_time: float
