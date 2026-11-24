"""
A small in-memory job queue so long builds can run in the background
(one at a time).
"""
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from src.core.issues import DesignError

Status = Literal['queued', 'running', 'done', 'failed']


@dataclass
class Job:
    id: str
    status: Status = 'queued'
    result: Any = None
    error: str | None = None
    issues: list = field(default_factory=list)


class JobStore:
    def __init__(self, workers: int = 1):
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=workers)

    def submit(self, fn: Callable, *args, **kwargs) -> Job:
        job = Job(uuid.uuid4().hex[:12])
        with self._lock:
            self._jobs[job.id] = job
        self._pool.submit(self._run, job, fn, args, kwargs)
        return job

    def _run(self, job: Job, fn, args, kwargs):
        job.status = 'running'
        try:
            job.result = fn(*args, **kwargs)
            job.status = 'done'
        except DesignError as err:
            job.status, job.error, job.issues = 'failed', str(err), [i.to_dict() for i in err.issues]
        except Exception as err:  # noqa: BLE001 - report anything to the caller
            job.status, job.error = 'failed', f'{type(err).__name__}: {err}'
            traceback.print_exc()

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def shutdown(self):
        self._pool.shutdown(wait=True)
