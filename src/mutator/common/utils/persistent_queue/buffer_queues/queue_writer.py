import logging
from dataclasses import dataclass
from queue import Queue
from random import randint
from threading import Event
from time import sleep
from typing import List

from src.mutator.common.utils.persistent_queue.dao.queue_item import QueueItem
from src.mutator.common.utils.persistent_queue.persistent_queue import PersistentQueue


@dataclass
class QueueWriter:
    buffer_queue: Queue
    persistent_queue: PersistentQueue
    stop_threads: Event
    test_run_id: int

    def write_queue(self):
        progress_counter: int = 0
        # if max_empty_counter is reached exit the thread,
        # all generated tests have been pushed to persistent queue
        queue_empty_counter_max = 10
        queue_empty_counter_current = 0
        last_queue_size = 0

        logging.debug(
            "Starting to write generated tests from buffer queue into persistent queue."
        )
        logging.debug("Starting buffered writer.")
        sleep(1)
        while not self.stop_threads.is_set():
            try:
                logging.debug(f"Queue size: {self.buffer_queue.qsize()}")
                if queue_empty_counter_current >= queue_empty_counter_max:
                    logging.debug("Buffer is empty, exiting buffered writer.")
                    break
                if self.buffer_queue.empty() or self.buffer_queue.qsize() == 0:
                    logging.debug(
                        "Buffered queue is empty, incrementing empty counter."
                    )
                    queue_empty_counter_current += 1
                    continue

                buffer_full: bool = (
                    self.buffer_queue.qsize() >= self.buffer_queue.maxsize
                )
                # flush last few items in queue
                end_of_queue: bool = self.buffer_queue.qsize() == last_queue_size
                if buffer_full or end_of_queue:
                    logging.debug("Fetching items from buffer queue.")
                    queue_items: List[QueueItem] = []
                    for _ in range(self.buffer_queue.qsize()):
                        queue_items.append(self.buffer_queue.get())
                    queue_item_count = len(queue_items)
                    logging.debug(
                        f"Pushing {queue_item_count} tests to persistent queue."
                    )
                    self.persistent_queue.push_batch(queue_items)
                    progress_counter += queue_item_count
                    if randint(1, 3) == 2 or end_of_queue:  # nosec
                        logging.info(
                            f"Generated {progress_counter} tests for test run id {self.test_run_id}."
                        )
                last_queue_size = self.buffer_queue.qsize()
            except Exception as e:
                logging.exception(f"Error while populating persistent queue: {e}")
        logging.debug(f"Persisted {progress_counter} tests to queue.")
