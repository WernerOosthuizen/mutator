from sqlalchemy import Integer, Column, JSON, TIMESTAMP, String

from src.common.database.database_base import Base


class QueueItem(Base):
    __tablename__ = "test_queue"
    id = Column("id", String(45), primary_key=True)
    test_run_id = Column("test_run_id", Integer, primary_key=True)
    test_hash = Column("test_hash", String(255), primary_key=True)
    test = Column("test", JSON)
    create_date = Column("create_date", TIMESTAMP)
