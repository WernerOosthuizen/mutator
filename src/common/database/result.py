from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from src.common.database.database_base import Base
from src.common.database.validation_result import ValidationResult


class Result(Base):
    # Database Schema
    __tablename__ = "test_result"
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_run.id"))
    test_type = Column(String(255))
    test_value = Column(String(10000))
    passed = Column(Boolean)
    request_hash = Column(String(255))
    request_method = Column(String(45))
    request_headers = Column(JSON)
    request_url = Column(String(10000))
    request_body = Column(JSON)
    response_hash = Column(String(255))
    response_headers = Column(JSON)
    response_body = Column(JSON)
    response_status_code = Column(Integer)
    validations = relationship(ValidationResult, uselist=True, lazy="selectin")
    create_date = Column(TIMESTAMP)
