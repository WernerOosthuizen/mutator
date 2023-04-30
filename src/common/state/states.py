from enum import Enum


class State(Enum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
