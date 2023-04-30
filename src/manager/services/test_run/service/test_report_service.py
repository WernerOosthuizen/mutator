import json
import logging
import pathlib
from os import path
from typing import List, Dict

from sqlalchemy import text
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session
from werkzeug.exceptions import NotFound, ServiceUnavailable, BadRequest

from src.manager.services.test_run.dao import (
    test_report_dao,
)

report_file_path = (
    pathlib.Path(path.abspath(__file__)).parents[3].__str__() + "/config/reports.json"
)


def get_reports():
    # Reports could probably be handled in another way,
    # but its nice and easy to add queries to a file, so keeping it there for now.
    # reports and their sql live here: src/manager/config/reports.json
    with open(report_file_path, "r") as reports_file:
        reports: list = list(json.load(reports_file).keys())
    logging.debug(f"Found reports: {reports}")
    return {"reports": reports}


def run_report(report: str, parameters: Dict, session: Session) -> List[Dict]:
    logging.debug(
        f"Fetching results for report: {report} with parameters: {parameters}"
    )
    with open(report_file_path, "r") as reports_file:
        reports_data = json.load(reports_file)
        if not reports_data:
            logging.error("Could not load report data.")
            raise ServiceUnavailable("Could not load reporting data.")
        reports: list = list(reports_data.keys())
        report_sql: str = reports_data.get(report)
        logging.debug(f"Found report sql to run: {report_sql}")
        if report not in reports or not report_sql:
            logging.error("Report data not found.")
            raise NotFound("Report not found.")

    try:
        report_result = test_report_dao.run_test_report(
            text(report_sql), parameters, session
        )
    except StatementError as e:
        logging.exception(e)
        raise BadRequest(str(e.orig))

    logging.debug(f"Report result: {report_result}")
    results = [dict(x) for x in report_result]
    logging.debug(f"Returning final results: {results}")
    return results
