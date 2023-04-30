from enum import Enum


class HashStrategy(Enum):
    ALL = "Include all fields in response hash."
    INCLUDE_EXACT_MATCH = (
        "Include specific fields in response hash. Needs to be an exact match."
    )
    EXCLUDE_EXACT_MATCH = (
        "Exclude fields from response hash. Needs to be an exact match."
    )
    # E.g. if date is configured, create_date will be matched.
    EXCLUDE_PARTIAL_MATCH = "Exclude fields from response hash. Can be a partial match."
