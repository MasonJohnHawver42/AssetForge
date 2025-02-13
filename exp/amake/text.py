import AssetForge

from pathlib import Path
from typing import List

import shutil

class General(AssetForge.AssetTool):
    def __init__(self):
        super().__init__() 
    
    def check_match(self, file_path: Path) -> bool:
        # This tool accepts every file.
        return file_path.suffix.lower() == ".txt"

    def define_dependencies(self, file_path: Path) -> List[Path]:
        # No additional dependencies for linking.
        return []

    def define_outputs(self, file_path: Path) -> List[Path]:
        # Return the same relative path so that the output file in the output folder will have the same structure.
        return [file_path]
    
    def build(self, file_path: Path, input_folder: Path, output_folder: Path) -> None:
        input_file: Path = input_folder / file_path
        output_file: Path = output_folder / file_path

        output_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(input_file, output_file)