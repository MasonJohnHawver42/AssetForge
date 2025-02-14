from .core import AssetTool
from .util import in_folder

from pathlib import Path
from typing import List

class General(AssetTool):
    """Simply takes every file in an input folder and makes an output file that just links the input file.
    
    The output file will be placed in the output folder preserving the relative path from the input folder.
    For example, if the input file is `imgs/penguin.png` (with `imgs/penguin.png` relative to the input folder),
    the output file will be created as `<output_folder>/imgs/penguin.png`.
    """
    def __init__(self):
        super().__init__() 
    
    def check_match(self, file_path: Path) -> bool:
        return in_folder(file_path, self.input_folder)

    def define_dependencies(self, file_path: Path) -> List[Path]:
        # No additional dependencies for linking.
        return []

    def define_outputs(self, file_path: Path) -> List[Path]:
        # Return the same relative path so that the output file in the output folder will have the same structure.
        return [self.output_folder / self.relative_path(file_path)]
    
    def build(self, file_path: Path) -> None:
        """
        Creates a symbolic link in the output folder that points to the input file.
        
        Assumes that the current working directory is the input folder.
        """
        # Resolve the full path of the input file by joining the current working directory (input folder) with file_path.
        input_file = file_path
        output_file = self.output_folder / self.relative_path(file_path)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            output_file.symlink_to(input_file.resolve())
            print(f"Created symlink: {output_file} -> {input_file.resolve()}")
        except Exception as e:
            print(f"Error creating symlink for {input_file} at {output_file}: {e}")