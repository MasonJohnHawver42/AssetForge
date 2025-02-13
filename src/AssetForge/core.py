from pathlib import Path
from typing import List

class AssetTool:
    def __init__(self, p=0):
        self.priority = p

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

    def build(self, file_path: Path, input_folder: Path, output_folder: Path) -> None:
        """
        Uses the input file and its dependencies to build the output files.
        file_path : path to input file relative to input folder
        """
        raise NotImplementedError("Subclasses should implement this.")


class AssetForge:
    """Singleton that maintains a registry of asset tools."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tools = []  # Initialize the tools list
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

def Build(input_folder: Path, output_folder: Path):
    pass
