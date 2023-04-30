from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List

from sqlalchemy import func, asc
from sqlalchemy.orm.scoping import ScopedSession

from src.mutator.common.utils.persistent_queue.dao.queue_item import QueueItem


@dataclass
class PersistentQueue:
    test_run_id: int
    scoped_session: ScopedSession

    def push(self, queue_item: QueueItem) -> None:
        with self.scoped_session() as session:
            session.add(queue_item)
            session.commit()

    def push_batch(self, queue_items: List[QueueItem]) -> None:
        with self.scoped_session() as session:
            session.bulk_save_objects(queue_items)
            session.commit()

    def pop(self, batch_size=10) -> List[QueueItem]:
        with self.scoped_session() as session:
            queue_items: List[QueueItem] = (
                session.query(QueueItem)
                .filter(QueueItem.test_run_id == self.test_run_id)
                .order_by(asc(QueueItem.create_date))
                .limit(batch_size)
            ).all()
        return queue_items

    def ack(self, queue_items: List[QueueItem]) -> bool:
        with self.scoped_session() as session:
            ids: List[str] = []
            test_hashes: List[str] = []

            for queue_item in queue_items:
                ids.append(queue_item.id)
                test_hashes.append(queue_item.test_hash)

            query = (
                session.query(QueueItem)
                .filter(QueueItem.id.in_(ids))
                .filter(QueueItem.test_run_id == self.test_run_id)
                .filter(QueueItem.test_hash.in_(test_hashes))
            )
            query.delete()
            session.commit()
        return True

    def remove_all(self) -> bool:
        with self.scoped_session() as session:
            query = session.query(QueueItem).filter(
                QueueItem.test_run_id == self.test_run_id
            )
            query.delete()

            # Remove any old tests from queue that somehow were not deleted
            trim_query = session.query(QueueItem).filter(
                QueueItem.create_date < (datetime.utcnow() - timedelta(days=7))
            )
            trim_query.delete()
            session.commit()
        return True

    def size(self) -> int:
        with self.scoped_session() as session:
            size = (
                session.query(func.count(QueueItem.test_run_id))
                .filter(QueueItem.test_run_id == self.test_run_id)
                .first()[0]
            )
        return size
