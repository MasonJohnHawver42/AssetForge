from pathlib import Path
from typing import List, Optional, Dict, Set, Callable, Any

import uuid

import io
import sys

import threading

from .util import topological_sort, JobDict, ThreadPool

class AssetTool:
    def __init__(self):
        self.input_folder = Path().cwd()
        self.output_folder = Path().cwd()
        self.priority = 0

    def check_match(self, file_path: Path) -> bool:
        """
        Determines if a file is an input file to this tool.
        file_path : path to input file relative to input folder
        return : True/False
        """
        raise NotImplementedError("Subclasses should implement this.")

    def define_dependencies(self, file_path: Path) -> List[Path]:
        """
        Defines the dependencies of the input file relative to the input_folder
        file_path : path to input file relative to input folder
        return : List[Path] list of file paths that are relative to the input folder
        """
        raise NotImplementedError("Subclasses should implement this.")
    
    def define_outputs(self, file_path: Path) -> List[Path]:
        """
        Defines the output files of the input file relative to the input file.
        file_path : path to input file relative to input folder
        return : a list of paths relative to the input folder but will latter be made relative to the output folder
        """
        raise NotImplementedError("Subclasses should implement this.")

    def build(self, file_path: Path) -> None:
        """
        Uses the input file and its dependencies to build the output files.
        file_path : path to input file relative to input folder
        """
        raise NotImplementedError("Subclasses should implement this.")

    def relative_path(self, file_path: Path) -> Path:
        if file_path.is_relative_to(self.input_folder):
            return file_path.relative_to(self.input_folder)
        elif file_path.is_relative_to(self.output_folder):
            return file_path.relative_to(self.output_folder)

        raise ValueError(f"{file_path} isn't relative to {self.input_folder} or {self.output_folder}")

class AssetForge:
    """Singleton that maintains a registry of asset tools."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tools = []  # Initialize the tools list
            cls._instance.log_buf = io.StringIO()
            cls._instance.todo = 0
            cls._instance.done = 0
        return cls._instance

    def register_tool(self, tool: AssetTool) -> None:
        """Registers an asset tool."""
        self.tools.append(tool)

    def get_tools(self) -> List[AssetTool]:
        """Returns the list of registered tools."""
        return self.tools

def RegisterTool(tool: AssetTool, priority: int = 0) -> None:
    """Adds a tool to the AssetForge singleton."""
    forge = AssetForge()
    tool.priority = priority
    forge.register_tool(tool)

def __call_check_match(tool, file_path):
    tmp = tool.check_match(file_path)
    assert isinstance(tmp, bool), f"{tool.__class__.__name__}'s check_match didn't return a bool"
    return tmp

def _call_define_outputs(tool, file_path):
    tmp = tool.define_outputs(file_path)
    assert isinstance(tmp, list), f"{tool.__class__.__name__}'s define_outputs didn't return a list of Paths; it returned {type(tmp)}"
    assert all(isinstance(item, Path) for item in tmp), f"{tool.__class__.__name__}'s define_outputs didn't return a list with just Paths"
    return tmp

def _call_define_dependencies(tool, file_path):
    tmp = tool.define_dependencies(file_path)
    assert isinstance(tmp, list), f"{tool.__class__.__name__}'s define_dependencies didn't return a list of Paths"
    assert all(isinstance(item, Path) for item in tmp), f"{tool.__class__.__name__}'s define_dependencies didn't return a list with just Paths"
    return tmp

def _call_build(forge, tool, file_path):
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    sys.stdout = forge.log_buf
    sys.stderr = forge.log_buf
    try:
        tool.build(file_path)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    forge.done += 1
    progress_str = (str(int(100 * forge.done / forge.todo)) + "%").ljust(4)
    print(f"[{progress_str}] {tool.__class__.__name__} \"{file_path}\"")

def _call_build_parallel(forge, tool, file_path):
    tool.build(file_path)

    with forge.lock:
        forge.done += 1
        progress_str = (str(int(100 * forge.done / forge.todo)) + "%").ljust(4)
        forge.progress_buf.append(f"[{progress_str}] {tool.__class__.__name__} \"{file_path}\"")

def _pick_tools(tools : List[AssetTool], file_path : Path) -> List[AssetTool]:
    return [tool for tool in tools if __call_check_match(tool, file_path)]

def _run_job(job_func: Callable[..., Any], *args, **kwargs) -> None:
            job_func(*args, **kwargs)

def Build(input_folder: Path, output_folder: Path, recursive: bool = False, parallel: bool = False):
    print("[0%  ] building ... ")

    assert isinstance(input_folder, Path), "input_folder is not a Path"
    assert isinstance(output_folder, Path), "output_folder is not a Path"

    forge = AssetForge()

    for tool in forge.get_tools():
        tool.input_folder = input_folder
        tool.output_folder = output_folder

    root_files = set()
    
    for file in input_folder.rglob("*"):
        if file.is_file():
            root_files.add(file)
    
    delta = root_files
    output_files = set()

    graph: Dict[str, Set[str]] = {}
    jobs: JobDict = {}

    for file in root_files:
        graph[str(file)] = set()

    while len(delta) > 0:

        staged_files = set()

        matched_tools = []
        output_sets = []
        input_files = []

        for file in delta:
            tools = _pick_tools(forge.get_tools(), file)
            for tool in tools:
                outs = _call_define_outputs(tool, file)
                
                matched_tools.append(tool)
                output_sets.append(set(outs))
                input_files.append(file)
        
        while True:
            collisions = set()

            for i in range(len(output_sets)):
                for j in range(i + 1, len(output_sets)):
                    if output_sets[i] & output_sets[j]:
                        collisions.add(i)
                        collisions.add(j)
                
                if output_sets[i] & output_files:
                    collisions.add(i)
            
            if len(collisions) == 0:
                break

            to_remove = min(collisions, key = lambda i : matched_tools[i].priority)

            output_sets.pop(to_remove)
            matched_tools.pop(to_remove)
            input_files.pop(to_remove)
        
        for i, (tool, outs, file) in enumerate(zip(matched_tools, output_sets, input_files)):
            deps = _call_define_dependencies(tool, file)

            staged_files |= outs

            tool_id = f"{tool.__class__.__name__}_{uuid.uuid4().hex}"

            graph[tool_id] = set([str(d) for d in deps]) | set([str(file)])
            jobs[tool_id] = (_call_build_parallel if parallel else _call_build, forge, tool, file)

            for o in outs:
                graph[str(o)] = set([tool_id])
    
        output_files |= staged_files
        delta = staged_files

    bipartite_order = topological_sort(graph)
    order = bipartite_order[1::2]

    forge.todo = sum([len(b) for b in order])

    if parallel:
        forge.lock = threading.Lock()
        forge.progress_buf = []

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        

        thread_pool = ThreadPool(len(max(order, key=len)))
        for batch in order:
            sys.stdout = forge.log_buf
            sys.stderr = forge.log_buf

            for node in batch:
                thread_pool.submit_job(*jobs[node])
            
            thread_pool.wait_for_all_jobs()

            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            for p in forge.progress_buf:
                print(p)
            
            forge.progress_buf = []
        
        thread_pool.shutdown()

        sys.stdout = old_stdout
        sys.stderr = old_stderr
    else:
        for batch in order:
            for node in batch:
                _run_job(*jobs[node])

    with open(output_folder / Path("output.log"), "w") as log_file:
        log_file.write(forge.log_buf.getvalue())
    
    forge.log_buf.truncate(0)
    forge.log_buf.seek(0)

    # print("[100%] done")
