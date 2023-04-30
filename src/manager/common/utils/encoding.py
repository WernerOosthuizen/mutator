import base64
import json
from functools import lru_cache
from typing import Dict


def encode(dict_to_encode: Dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(dict_to_encode).encode()).decode()


@lru_cache
def decode(base64str: str) -> Dict:
    response = base64.urlsafe_b64decode(base64str).decode()
    return json.loads(response)
