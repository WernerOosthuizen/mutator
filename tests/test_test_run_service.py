from unittest import TestCase

from src.manager.services.test_run.service.test_run_service import (
    get_headers,
    get_config,
)


class Test(TestCase):
    def test_get_headers_both_exist(self):
        common = {
            "headers": {"Authorization": "Bearer supersecrettokenhere"},
            "config": {
                "invalid_status_codes": [404],
                "hash_generation": {
                    "field_names": ["id", "date"],
                    "strategy": "EXCLUDE_PARTIAL_MATCH",
                },
            },
        }

        endpoint = {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "url": "http://test-app:8010/v1/results",
            "body": {"modifiers": [1, 2, 3, 4, 5, 6, 7]},
        }

        expected = {
            "Content-Type": "application/json",
            "Authorization": "Bearer supersecrettokenhere",
        }
        headers = get_headers(common, endpoint)
        self.assertEqual(expected, headers)

    def test_get_headers_common_headers_dont_exist(self):
        common = {
            "config": {
                "invalid_status_codes": [404],
                "hash_generation": {
                    "field_names": ["id", "date"],
                    "strategy": "EXCLUDE_PARTIAL_MATCH",
                },
            }
        }

        endpoint = {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "url": "http://test-app:8010/v1/results",
            "body": {"modifiers": [1, 2, 3, 4, 5, 6, 7]},
        }

        expected = {"Content-Type": "application/json"}
        headers = get_headers(common, endpoint)
        self.assertEqual(expected, headers)

    def test_common_config_both_exist(self):
        common = {
            "headers": {"Authorization": "Bearer supersecrettokenhere"},
            "config": {
                "invalid_status_codes": [404],
                "hash_generation": {
                    "field_names": ["id", "date"],
                    "strategy": "EXCLUDE_PARTIAL_MATCH",
                },
            },
        }

        endpoint_config = {
            "invalid_status_codes": [501],
            "hash_generation": {
                "field_names": ["id", "date"],
                "strategy": "EXCLUDE_PARTIAL_MATCH",
            },
        }

        expected = {
            "invalid_status_codes": [404],
            "hash_generation": {
                "field_names": ["id", "date"],
                "strategy": "EXCLUDE_PARTIAL_MATCH",
            },
        }
        endpoint_config = get_config(common, endpoint_config)
        self.assertEqual(expected, endpoint_config)

    def test_common_config_common_config_doesnt_exist(self):
        common = {"headers": {"Authorization": "Bearer supersecrettokenhere"}}

        endpoint_config = {
            "invalid_status_codes": [501],
            "hash_generation": {
                "field_names": ["id", "date"],
                "strategy": "EXCLUDE_PARTIAL_MATCH",
            },
        }

        expected = {
            "invalid_status_codes": [501],
            "hash_generation": {
                "field_names": ["id", "date"],
                "strategy": "EXCLUDE_PARTIAL_MATCH",
            },
        }
        endpoint_config = get_config(common, endpoint_config)
        self.assertEqual(expected, endpoint_config)

    def test_common_config_endpoint_config_doesnt_exist(self):
        common = {
            "headers": {"Authorization": "Bearer supersecrettokenhere"},
            "config": {
                "invalid_status_codes": [404],
                "hash_generation": {
                    "field_names": ["id", "date"],
                    "strategy": "EXCLUDE_PARTIAL_MATCH",
                },
            },
        }

        expected = {
            "invalid_status_codes": [404],
            "hash_generation": {
                "field_names": ["id", "date"],
                "strategy": "EXCLUDE_PARTIAL_MATCH",
            },
        }
        endpoint_config = get_config(common, None)
        self.assertEqual(expected, endpoint_config)

    def test_common_config_both_dont_exist(self):
        endpoint_config = get_config(None, None)
        self.assertIsNone(endpoint_config)
