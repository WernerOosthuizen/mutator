from enum import Enum


class StateDescription(Enum):
    PENDING = "The test run is queued for processing."
    GENERATING = "The tests are being generated."
    RUNNING = "The tests are being executed."
    SUCCESS = "The test run completed successfully."
    SUCCESS_DRY_RUN = "DRY RUN: The test run completed successfully."
    CANCELLED = "The test run was cancelled."
    TEST_GENERATION_FAILURE = "An error occurred while generating the tests."
    GENERAL_FAILURE = "A general system error occurred."
    TEST_COUNT_MISMATCH = "The generated test count and the test result count do not match. Some tests are missing."
    MAXIMUM_RUN_ATTEMPTS = "The test run reached its maximum run attempts."
