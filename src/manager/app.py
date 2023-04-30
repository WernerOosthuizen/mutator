import csv
import logging.config
import os
import pathlib
from configparser import ConfigParser
from io import StringIO
from os import path
from time import gmtime
from typing import Any

from flask import Flask, g, jsonify, request, make_response
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session

from src.manager.common.validate_request.request_validator import (
    validate_request_params,
    validate_request_body,
    validate_request_path,
)
from src.manager.services.test_run.service import test_report_service
from src.manager.services.test_run.service.test_result_service import (
    get_tests,
    get_specific_test,
)
from src.manager.services.test_run.service.test_run_service import (
    create_test_run,
    get_test_run_external,
    get_all_test_runs,
    cancel_test_run,
    create_test_run_batch,
)
from src.manager.services.test_run.validation.create_test_run.batch_create_test_run_schema import (
    BatchCreateTestRunSchema,
)
from src.manager.services.test_run.validation.create_test_run.create_test_run_schema import (
    CreateTestRunSchema,
)
from src.manager.services.test_run.validation.get_test_run.test_run_id_schema import (
    TestRunIdSchema,
)
from src.manager.services.test_run.validation.get_test_run.test_run_parameter_schema import (
    TestRunParameterSchema,
)
from src.manager.services.test_run.validation.get_test_run_result.test_result_parameter_schema import (
    TestResultParameterSchema,
)
from src.manager.services.test_run.validation.get_test_run_result.test_result_test_schema import (
    TestResultTestSchema,
)

log_file_path = (
    pathlib.Path(path.abspath(__file__)).parents[1].__str__()
    + "/common/config/logging.ini"
)
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
logging.Formatter.converter = gmtime

# General Config
config = ConfigParser()
config_file_path = (
    pathlib.Path(path.abspath(__file__)).parents[0].__str__() + "/config/config.ini"
)
config.read(config_file_path)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

database_url_env = os.environ.get("DATABASE")
if database_url_env is None:
    database_url = config.get("database", "database_url")
else:
    database_url = database_url_env

latest_api_version = "v1"

try:
    test_results_engine = create_engine(
        url=database_url,
        echo=config.getboolean("database", "echo"),
        connect_args={"timeout": config.getint("database", "timeout")}
        if "sqlite" in database_url
        else {},
    )
    if (
        database_url_env is None
        and "sqlite" in database_url
        and config.get("database", "database_mode") == "WAL"
    ):

        @event.listens_for(test_results_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):  # noqa
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    test_results_session = scoped_session(sessionmaker(bind=test_results_engine))

    @app.before_request
    def create_session():
        g.session = test_results_session()

    @app.teardown_appcontext
    def shutdown_session(exception=None):  # noqa
        test_results_session.remove()

except AttributeError as e:
    logging.error(f"Could not connect to DB: {e}")


@app.get("/health")
def health_check():
    return {"health": "OK"}


@app.post(f"/{latest_api_version}/testruns")
@validate_request_body(CreateTestRunSchema())
def create_new_test_run() -> Any:
    return (
        jsonify(
            create_test_run(
                g.validated_request,
                app.config.get("test_run_notification_queue"),
                g.session,
            )
        ),
        201,
    )


@app.post(f"/{latest_api_version}/batch/testruns")
@validate_request_body(BatchCreateTestRunSchema())
def create_new_test_run_batch() -> Any:
    return (
        jsonify(
            create_test_run_batch(
                g.validated_request,
                app.config.get("test_run_notification_queue"),
                g.session,
            )
        ),
        201,
    )


@app.delete(f"/{latest_api_version}/testruns/<test_run_id>")
@validate_request_path(TestRunIdSchema())
def cancel_selected_test_run(test_run_id: int) -> Any:  # noqa
    return jsonify(cancel_test_run(g.validated_request.get("test_run_id"), g.session))


@app.get(f"/{latest_api_version}/testruns")
@validate_request_params(TestRunParameterSchema())
def get_test_runs() -> Any:
    return jsonify(get_all_test_runs(g.validated_request, g.session))


@app.get(f"/{latest_api_version}/testruns/<test_run_id>")
@validate_request_path(TestRunIdSchema())
def get_specific_test_run(test_run_id: int) -> Any:  # noqa
    return jsonify(
        get_test_run_external(g.validated_request.get("test_run_id"), g.session)
    )


@app.get(f"/{latest_api_version}/testruns/<test_run_id>/tests")
@validate_request_path(TestRunIdSchema())
@validate_request_params(TestResultParameterSchema())
def get_all_test_run_tests(test_run_id: int) -> Any:  # noqa
    return jsonify(get_tests(g.validated_request, g.session))


@app.get(f"/{latest_api_version}/testruns/<test_run_id>/tests/<request_hash>")
@validate_request_path(TestResultTestSchema())
def get_single_test_run_test(test_run_id: int, request_hash: str) -> Any:  # noqa
    return jsonify(get_specific_test(g.validated_request, g.session))


@app.get(f"/{latest_api_version}/tests")
@validate_request_params(TestResultParameterSchema())
def get_all_test_results() -> Any:
    return jsonify(get_tests(g.validated_request, g.session))


@app.get(f"/{latest_api_version}/reports")
def get_all_test_run_reports() -> Any:  # noqa
    return jsonify(test_report_service.get_reports())


@app.get(f"/{latest_api_version}/reports/<report>")
def run_test_run_report(report: str) -> Any:  # noqa
    request_args = request.args
    logging.debug(f"Request args: {request_args}")
    results = test_report_service.run_report(report, request_args, g.session)
    if request_args.get("format") == "csv":
        # https://stackoverflow.com/a/26998089
        si = StringIO()
        if results:
            cw = csv.writer(si)
            cw.writerow(results[0].keys())
            for row in results:
                cw.writerow(row.values())

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename={report}.csv"
        output.headers["Content-type"] = "text/csv"
        if not results:
            output.status_code = 404
        return output
    return jsonify(results)
