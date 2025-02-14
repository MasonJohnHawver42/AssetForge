from typing import List, Dict, Tuple, Set, Callable, Any, Optional
from pathlib import Path

import threading
import queue

def full_suffix(file_path: Path) -> str:
    return "".join(file_path.suffixes)

def in_folder(file_path: Path, folder: Path) -> bool:
    try:
        file_path.relative_to(folder)
        return True
    except ValueError:
        return False

def add_suffix(file_path: Path, extra_suffix: str) -> Path:
    """
    Appends extra_suffix to the filename.
    
    For example:
        Path("name.xyz") with extra_suffix ".bin" -> Path("name.xyz.bin")
    """
    return file_path.with_name(file_path.name + extra_suffix)

def topological_sort(graph: Dict[str, Set[str]]) -> List[Set[str]]:
    dependee_graph: Dict[str, Set[str]] = {}
    in_degree: Dict[str, int] = {}

    for node in graph:
        dependee_graph[node] = set()
    
    for node in graph:
        for dependency in graph[node]:
            dependee_graph[dependency].add(node)
    
    for node in graph:
        in_degree[node] = len(graph[node])
    
    queue = [node for node in graph if in_degree[node] == 0]
    result: List[Set[str]] = []
    nodes_added = set() 

    while len(queue) > 0:
        batch: Set[str] = set()

        for node in queue:
            batch.add(node)
            nodes_added.add(node)
            
            for dependency in dependee_graph[node]:
                in_degree[dependency] -= 1
        
        result.append(batch)
        queue = [node for node in graph if in_degree[node] == 0 and node not in nodes_added]

    if len(nodes_added) != len(graph):
        raise ValueError("Graph contains a cycle")

    return result

JobDict = Dict[
    str,
    Tuple[
        Callable[..., Any],
        Optional[Tuple[Any, ...]],
        Optional[Dict[str, Any]],
    ],
]

class ThreadPool:
    def __init__(self, num_threads: int):
        self.num_threads = num_threads
        self.job_queue = queue.Queue()  # Queue to hold jobs
        self.threads = []  # List to hold thread objects
        self.job_events = {}  # Dictionary to map job IDs to their completion events
        self._shutdown = False  # Flag to signal shutdown
        self._condition = threading.Condition()  # Condition variable for thread synchronization

        # Create and start threads
        for _ in range(num_threads):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self.threads.append(thread)

    def _worker(self):
        """Worker function that runs in each thread."""
        while True:
            with self._condition:
                # Wait until there's a job in the queue or shutdown is signaled
                while self.job_queue.empty() and not self._shutdown:
                    self._condition.wait()

                # If shutdown is signaled and the queue is empty, exit the thread
                if self._shutdown and self.job_queue.empty():
                    return

                # Get a job from the queue
                job_id, job_func, args, kwargs = self.job_queue.get()

            try:
                # Execute the job
                job_func(*args, **kwargs)
            finally:
                # Mark the job as completed
                self.job_events[job_id].set()
                self.job_queue.task_done()

    def submit_job(self, job_func: Callable[..., Any], *args, **kwargs) -> int:
        """Submit a job to the thread pool."""
        with self._condition:
            if self._shutdown:
                raise RuntimeError("Cannot submit job: ThreadPool is shut down")

            job_id = len(self.job_events)  # Unique ID for the job
            event = threading.Event()  # Event to track job completion
            self.job_events[job_id] = event

            # Add the job to the queue
            self.job_queue.put((job_id, job_func, args, kwargs))
            self._condition.notify()  # Notify one waiting thread

        return job_id

    def wait_for_job(self, job_id: int):
        """Wait for a specific job to complete."""
        if job_id in self.job_events:
            self.job_events[job_id].wait()

    def wait_for_all_jobs(self):
        """Wait for all jobs in the queue to complete."""
        self.job_queue.join()

    def shutdown(self):
        """Shutdown the thread pool."""
        with self._condition:
            self._shutdown = True  # Signal threads to stop
            self._condition.notify_all()  # Notify all waiting threads

        # Wait for all threads to finish
        for thread in self.threads:
            thread.join()

        # Clear the job queue and events
        self.job_queue = queue.Queue()
        self.job_events.clear()

