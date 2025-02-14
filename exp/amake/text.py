import AssetForge

from pathlib import Path
from typing import List

import shutil

class TextTool(AssetForge.AssetTool):    
    def check_match(self, file_path: Path) -> bool:
        # This tool accepts every file.
        return file_path.suffix.lower() == ".txt" and file_path.is_relative_to(self.input_folder)

    def define_dependencies(self, file_path: Path) -> List[Path]:
        # No additional dependencies for linking.
        return []

    def define_outputs(self, file_path: Path) -> List[Path]:
        # Return the same relative path so that the output file in the output folder will have the same structure.
        return [self.output_folder / self.relative_path(file_path)]
    
    def build(self, file_path: Path) -> None:
        input_file = file_path
        output_file = self.output_folder / self.relative_path(file_path)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(input_file, output_file)