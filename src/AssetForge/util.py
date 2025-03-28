from typing import List, Dict, Tuple, Set, Callable, Any, Optional, Iterable, Union
from pathlib import Path

from graphviz import Digraph

import threading
import queue
import re

import hashlib

def hash_file(file_path : Path) -> bytes:
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):  # Read in chunks to handle large files
            hasher.update(chunk)
    return hasher.digest()

def combine_hashes(items: Iterable[str], algorithm: str = "sha256") -> str:
    """Combines hashes from multiple sources and returns the final hex digest."""
    combined_hasher = hashlib.new(algorithm)

    for item in sorted(items):
        combined_hasher.update(item)

    return combined_hasher.hexdigest()

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

Graph = Dict[str, Set[str]]

def invert_graph(graph:Graph) -> Graph:
    inverted = {node: set() for node in graph}  # Initialize empty adjacency list
    
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            inverted[neighbor].add(node)  # Reverse the edge

    return inverted

JobDict = Dict[
    str,
    Tuple[
        Callable[..., Any],
        Optional[Tuple[Any, ...]],
        Optional[Dict[str, Any]],
    ],
]

Order = List[Set[str]]

def topological_sort(graph: Graph) -> Order:
    dependee_graph: Graph = {}
    in_degree: Dict[str, int] = {}

    for node in graph:
        dependee_graph[node] = set()
    
    for node in graph:
        for dependency in graph[node]:
            dependee_graph[dependency].add(node)
    
    for node in graph:
        in_degree[node] = len(graph[node])
    
    queue = [node for node in graph if in_degree[node] == 0]
    result: Order = []
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

def viz_dependency_graph(dependencies, topological_order, output_file="graph"):
    dot = Digraph(format="svg")
    dot.attr(rankdir="LR")

    dot.attr("graph", compound="true")
    dot.attr("node", shape="record", fontname="Courier")
    dot.attr("edge", style="dashed", arrowhead="vee", splines="curved", tailport="e", headport="w")

    # Create a subgraph (cluster) for each topological level to align nodes
    for level, nodes in enumerate(topological_order):
        with dot.subgraph(name=f"cluster_{level}") as sub:
            sub.attr(rank="same", label=(f"Files {int((level - 0) / 2)}" if level != 0 else "Root Files") if level % 2 == 0 else f"Funcs {int((level - 1) / 2)}", fontsize="12", fontname="Courier")
            sub.attr(align="left")
            for node in nodes:
                if re.match(r"^\w+_[a-fA-F0-9]{32}$", node):
                    sub.node(node, label=node[:-33], style="filled", fillcolor="lightgrey")
                else:
                    sub.node(node, style="filled", fillcolor="lightblue")

    # Add edges
    for node, deps in dependencies.items():
        for dep in deps:
            dot.edge(dep, node)

    # Save and render
    dot.render(output_file, format="svg", cleanup=True)
    # print(f"Graph saved as {output_file}.svg")

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

