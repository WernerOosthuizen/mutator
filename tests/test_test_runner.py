import random
from datetime import datetime
from unittest import TestCase

from src.mutator.consumer import build_field_matcher
from src.mutator.runner.hash_strategy import HashStrategy
from src.mutator.runner.test_runner import extract_response_fields


class Test(TestCase):
    create_date = datetime.utcnow()

    body = {
        "id": random.random(),  # nosec
        "hello": "test",
        "value1": "test",
        "value2": "test",
        "value3": "test",
        "value4": "test",
        "value5": "test",
        "value6": "test",
        "value7": "test",
        "value8": "test",
        "value9": "test",
        "value10": "test",
        "value11": "test",
        "value12": "test",
        "value13": "test",
        "value14": "test",
        "value15": "test",
        "value16": "test",
        "value17": "test",
        "value18": "test",
        "value19": "test",
        "value20": "test",
        "create_date": create_date,
    }

    def test_extract_response_fields_dont_alter_fields(self):
        expected_response = self.body

        hash_generation = {
            "field_names": ["id", "create_date"],
            "strategy": HashStrategy.ALL.name,
        }

        field_matcher = build_field_matcher(hash_generation)
        extracted_response = extract_response_fields(self.body, field_matcher)
        self.assertEqual(expected_response, extracted_response)

    def test_extract_response_fields_exclude_fields_partial_match(self):
        expected_response = {"hello": "test"}

        hash_generation = {
            "field_names": [
                "aaa",
                "bbb",
                "ccc",
                "ddd",
                "eee",
                "value",
                "fff",
                "ggg",
                "hhh",
                "id",
                "date",
            ],
            "strategy": HashStrategy.EXCLUDE_PARTIAL_MATCH.name,
        }

        field_matcher = build_field_matcher(hash_generation)
        extracted_response = extract_response_fields(self.body, field_matcher)
        self.assertEqual(expected_response, extracted_response)

    def test_extract_response_fields_include_fields(self):
        expected_response = {"value1": "test"}

        hash_generation = {
            "field_names": [
                "aaa",
                "bbb",
                "ccc",
                "ddd",
                "value1",
                "eee",
                "fff",
                "ggg",
                "hhh",
            ],
            "strategy": HashStrategy.INCLUDE_EXACT_MATCH.name,
        }

        field_matcher = build_field_matcher(hash_generation)
        extracted_response = extract_response_fields(self.body, field_matcher)
        self.assertEqual(expected_response, extracted_response)

    def test_extract_response_fields_exclude_fields(self):
        expected_response = {"value1": "test"}

        hash_generation = {
            "field_names": [
                "id",
                "aaa",
                "bbb",
                "ccc",
                "ddd",
                "hello",
                "aaa",
                "bbb",
                "ccc",
                "ddd",
                "eee",
                "value2",
                "value3",
                "value4",
                "value5",
                "value6",
                "value7",
                "value8",
                "value9",
                "value10",
                "value11",
                "value12",
                "value13",
                "value14",
                "value15",
                "value16",
                "value17",
                "value18",
                "value19",
                "value20",
                "fff",
                "ggg",
                "hhh",
                "eee",
                "fff",
                "ggg",
                "hhh",
                "create_date",
            ],
            "strategy": HashStrategy.EXCLUDE_EXACT_MATCH.name,
        }

        field_matcher = build_field_matcher(hash_generation)
        extracted_response = extract_response_fields(self.body, field_matcher)
        self.assertEqual(expected_response, extracted_response)

    def test_extract_response_fields_text_response(self):
        hash_generation = {
            "field_names": ["timestamp"],
            "strategy": HashStrategy.EXCLUDE_PARTIAL_MATCH.name,
        }

        text_body = f"timestamp: {datetime.utcnow()}"

        field_matcher = build_field_matcher(hash_generation)
        extracted_response = extract_response_fields(text_body, field_matcher)
        self.assertEqual(None, extracted_response)

    def test_extract_response_fields_none(self):
        hash_generation = {
            "field_names": ["timestamp"],
            "strategy": HashStrategy.EXCLUDE_PARTIAL_MATCH.name,
        }

        field_matcher = build_field_matcher(hash_generation)
        extracted_response = extract_response_fields(None, field_matcher)
        self.assertEqual(None, extracted_response)

    def test_extract_response_fields_list_body(self):
        expected_new_body = {
            "test_run_id": [
                "Must be greater than or equal to 0 and less than or equal to "
                "1000000."
            ]
        }
        hash_generation = {
            "field_names": ["abc"],
            "strategy": HashStrategy.EXCLUDE_PARTIAL_MATCH.name,
        }

        body = {
            "test_run_id": [
                "Must be greater than or equal to 0 and less than or equal to 1000000."
            ]
        }

        field_matcher = build_field_matcher(hash_generation)
        extracted_response = extract_response_fields(body, field_matcher)
        self.assertEqual(expected_new_body, extracted_response)
