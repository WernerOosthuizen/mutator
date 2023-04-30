from abc import ABC, abstractmethod

from src.common.database.validation_result import ValidationResult


class Validator(ABC):
    pass

    @abstractmethod
    def __validate__(self) -> ValidationResult:
        pass
