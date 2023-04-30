import json
import logging
from dataclasses import dataclass
from typing import Generator, Optional, Dict


# The Test Repository are the flat files that are bundled with this project that contain the tests.
# Location: src/mutator/config/test_repository


@dataclass
class TestRepository:
    test_configurations: Dict

    def __init__(self, location: str, test_file: str):
        self.test_configurations = {}
        with open(location + test_file) as test_config_file:
            configs = json.load(test_config_file)
            for test_type, test_value_file in configs.items():
                test_file_dir = location + test_value_file
                self.test_configurations[test_type] = test_file_dir

    def get_test_value(self) -> Optional[Generator[str, None, None]]:
        configured_test = None

        # open file containing tests, and return generator so that contents are not all read into memory at once
        for test_type, test_value_location in self.test_configurations.items():
            logging.debug(f"Generating {test_type} test from {test_value_location}")

            with open(test_value_location, "r") as file:
                try:
                    for line in file:
                        if line[0] != "#" and line[0] != "\n":
                            return_field = str(line.strip("\n"))
                            logging.debug(f"File reader returning:{return_field}")
                            yield test_type, return_field
                except StopIteration:
                    logging.exception(f"Could not read line from file {file}")

        return configured_test
