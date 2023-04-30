import logging
from typing import Dict

from marshmallow import Schema, RAISE
from werkzeug.exceptions import BadRequest


def validate(item: Dict, schema: Schema):
    logging.debug(f"Validating inbound request item: {item}.")

    validated_object = schema.load(
        item, unknown=RAISE
    )  # Raise exception on invalid input
    if validated_object is None:
        raise BadRequest("There is no object in request.")
    logging.debug(f"Validated object: {validated_object}.")

    return validated_object
