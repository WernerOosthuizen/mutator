import logging
import multiprocessing
import os
import threading
from queue import Queue

from src.manager.app import app
from src.mutator.worker_loop import start_worker_loop

use_processes = os.getenv("USE_PROCESSES", False)
use_polling = os.getenv("USE_POLLING", False)


def get_queue():
    if use_processes:
        return multiprocessing.Queue() if not use_polling else None
    else:
        return Queue() if not use_polling else None


def get_workers(worker_count, queue):
    if use_processes:
        return [
            multiprocessing.Process(target=start_worker_loop, args=(queue,))
            for _ in range(background_worker_count)
        ]
    else:
        return [
            threading.Thread(target=start_worker_loop, args=(queue,))
            for _ in range(worker_count)
        ]


def start_workers(workers):
    logging.info(
        f"Starting background workers. Using {'processes' if use_processes else 'threads'}."
    )
    for worker in workers:
        worker.start()


queue = get_queue()

# Start mutator
# Use worker per CPU core else cap workers at 6
cpu_count = os.cpu_count()
background_worker_count = cpu_count if cpu_count < 6 else 6
workers = get_workers(background_worker_count, queue)
start_workers(workers)

# Start manager
app.config["test_run_notification_queue"] = queue

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", 8000)
    app.run(host=host, port=port)
