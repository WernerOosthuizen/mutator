from unittest import TestCase

from src.mutator.worker_loop import update_config


class Test(TestCase):
    def test_hash_generation_config_merge_all_fields(self):
        default_config = {
            "field_names": ["id", "date"],
            "strategy": "EXCLUDE_PARTIAL_MATCH",
        }

        override_config = {"hash_generation": {"field_names": [], "strategy": "ALL"}}

        new_config = update_config(override_config, default_config, "hash_generation")
        self.assertEqual([], new_config.get("field_names"))
        self.assertEqual("ALL", new_config.get("strategy"))

    def test_hash_generation_config_merge_no_override(self):
        default_config = {
            "field_names": ["id", "date"],
            "strategy": "EXCLUDE_PARTIAL_MATCH",
        }

        new_config = update_config(None, default_config, "hash_generation")
        self.assertEqual(["id", "date"], new_config.get("field_names"))
        self.assertEqual("EXCLUDE_PARTIAL_MATCH", new_config.get("strategy"))

    def test_hash_generation_config_merge_only_field_names(self):
        default_config = {
            "field_names": ["id", "date"],
            "strategy": "EXCLUDE_PARTIAL_MATCH",
        }

        override_config = {"hash_generation": {"field_names": ["id"]}}

        new_config = update_config(override_config, default_config, "hash_generation")
        self.assertEqual(["id"], new_config.get("field_names"))
        self.assertEqual("EXCLUDE_PARTIAL_MATCH", new_config.get("strategy"))

    def test_hash_generation_config_merge_only_strategy(self):
        default_config = {
            "field_names": ["id", "date"],
            "strategy": "EXCLUDE_PARTIAL_MATCH",
        }

        override_config = {"hash_generation": {"strategy": "ALL"}}

        new_config = update_config(override_config, default_config, "hash_generation")
        self.assertEqual(["id", "date"], new_config.get("field_names"))
        self.assertEqual("ALL", new_config.get("strategy"))
