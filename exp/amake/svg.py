import AssetForge

import cairosvg

from pathlib import Path
from typing import List, Dict, Tuple


class SVGtoPNGTool(AssetForge.AssetTool):
    """
    todo
    """

    def tool_name(self):
        return "SVGtoPNGTool"
    
    def check_match(self, file_path: Path) -> bool:
        # Accept files with the .atals extension.
        return file_path.suffixes.count(".svg") == 1 and file_path.is_relative_to(self.input_folder)

    def define_dependencies(self, file_path: Path) -> List[Path]:
        return []

    def define_outputs(self, file_path: Path) -> List[Path]:
        return [self.output_folder / self.relative_path(file_path.with_suffix(".png"))] if file_path != Path(self.input_folder / Path("output.svg")) else [self.input_folder / self.relative_path(file_path.with_suffix(".png"))]
    
    def build(self, file_path: Path) -> None:
        # Read the atlas JSON data.
        svg_file = file_path
        output_path = self.define_outputs(file_path)[0]

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Convert SVG to PNG
            cairosvg.svg2png(url=str(svg_file), write_to=str(output_path))
            print(f"Successfully converted {svg_file} to {output_path}")
        except Exception as e:
            print(f"Error converting {svg_file} to PNG: {e}")