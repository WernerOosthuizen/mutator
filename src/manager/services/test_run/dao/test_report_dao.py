from typing import Dict

from sqlalchemy.orm import Session


def run_test_report(sql: str, parameters: Dict, session: Session):
    return session.execute(sql, parameters).fetchall()
