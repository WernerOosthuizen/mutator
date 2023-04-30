import functools

import flask
from flask import g
from marshmallow import Schema

from src.manager.common.validate_request.request_validation import validate


def validate_request_params(schema: Schema):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            create_validated_request(validate(flask.request.args, schema))
            return function(*args, **kwargs)

        return wrapper

    return decorator


def validate_request_path(schema: Schema):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            create_validated_request(validate(flask.request.view_args, schema))
            return function(*args, **kwargs)

        return wrapper

    return decorator


def validate_request_body(schema: Schema):
    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            create_validated_request(validate(flask.request.json, schema))
            return function(*args, **kwargs)

        return wrapper

    return decorator


def create_validated_request(validated_request):
    if "validated_request" not in g:
        g.validated_request = validated_request
    else:
        g.validated_request.update(validated_request)
