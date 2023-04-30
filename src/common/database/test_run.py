from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON, Boolean

from src.common.database.database_base import Base


class TestRun(Base):
    __tablename__ = "test_run"
    id = Column(Integer, primary_key=True)
    endpoint = Column(JSON)
    config = Column(JSON)
    batch_id = Column(String(45))
    state = Column(String(45))
    state_description = Column(String(255))
    passed = Column(Boolean)
    test_generated_count = Column(Integer)
    test_result_count = Column(Integer)
    owner = Column(String(255))
    run_attempts = Column(Integer)
    lock_start_date = Column(TIMESTAMP)
    lock_end_date = Column(TIMESTAMP)
    create_date = Column(TIMESTAMP)
    last_update_date = Column(TIMESTAMP)
    version = Column(Integer, nullable=False)

    __mapper_args__ = {"version_id_col": version}
