from dataclasses import dataclass
from typing import Dict


@dataclass(init=False)
class GenericRequest:
    hash: str
    headers: Dict
    method: str
    url: str
    body: Dict
