from typing import Tuple, Any

from flask import jsonify
from marshmallow import ValidationError

from src.manager.app import app


def create_error_response(error_message: Exception, status_code: int):
    response = jsonify(message=str(error_message))
    return response, status_code


@app.errorhandler(ValidationError)
def validation_error(error: ValidationError):
    return jsonify(error.messages), 400


@app.errorhandler(400)
def bad_request(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 400)


@app.errorhandler(401)
def unauthorised(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 401)


@app.errorhandler(403)
def forbidden(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 403)


@app.errorhandler(404)
def not_found(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 404)


@app.errorhandler(405)
def method_not_allowed(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 405)


@app.errorhandler(409)
def conflict(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 409)


@app.errorhandler(413)
def content_size_exceeded(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 413)


@app.errorhandler(429)
def too_many_requests(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 429)


@app.errorhandler(500)
def internal_server_error(e: Exception) -> Tuple[Any, int]:
    return create_error_response(e, 500)
