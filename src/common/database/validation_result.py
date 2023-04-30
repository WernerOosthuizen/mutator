from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean

from src.common.database.database_base import Base


class ValidationResult(Base):
    # Database Schema
    __tablename__ = "validation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(255))
    passed = Column(Boolean)
    message = Column(String(255))
    test_result_id = Column(Integer, ForeignKey("test_result.id"))
    create_date = Column(TIMESTAMP)
