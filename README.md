# Asset Forge

<!-- <div style="display: flex; align-items: top;">
  <img src="icon.png" alt="[icon image]" title="Icon" width="220px" style="margin-right: 15px; margin-bottom: 15px; aspect-ratio: 1; height: auto;">
  <span>
    <p>
        <strong>Asset Forge</strong>: CMake for video game assets. With this utility, you will be able to preprocess your asset files, which are human and tool-readable/usable, into binary files that can be directly streamed into C/C++ structs and classes. This process will streamline loading complex assets in small video game projects written in C/C++ or other systems languages.
    </p>
    <p style="margin-bottom: 0px">
        Instead of linking several libraries dedicated to loading different types of files: meshes, animations, sprite sheets, and etc. Now you can just write a simple python script that loads in any complicated mesh/assimp file, optimize the mesh, do some precalculations for vertex normals and tangent vectors, then package it into a binary file that can be easily loaded in C/C++ by streaming the data into a struct or class that has a mirror structure to the binary file.
    </p>
  </span>
</div> -->

<!-- <br> -->

![Icon](https://raw.githubusercontent.com/MasonJohnHawver42/AssetForge/refs/heads/master/icon.png)

**Asset Forge**: CMake for video game assets. With this utility, you will be able to preprocess your asset files, which are human and tool readable or usable, into binary files that can be directly streamed into C/C++ structs and classes. This process will streamline loading complex assets in small video game projects written in C/C++ or other systems languages.

Instead of linking several libraries dedicated to loading different types of files: meshes, animations, sprite sheets, etc., now you can just write a simple Python script that loads any complicated mesh/assimp file, optimizes the mesh, does some pre-calculations for vertex normals and tangent vectors, then packages it into a binary file that can be easily loaded in C/C++ by streaming the data into a struct or class that has a mirror structure to the binary file.

Preprocessing assets into binary files also has the benefit of compression. In the example a human editable plaintext `json` is **3689** bytes, preprocessing it into a `.bin` file compresses it to **1273** bytes, then compressing that with zlib results in a `.bin.z` that is **468** bytes; **An 88% compression!**

**Author**: Mason Hawver\
**Version**: v0.2.3

[pypi package page](https://pypi.org/project/AssetForge/)

## Example Usage and Result:

```bash
pip install AssetForge

cd exp  
pip install -r requirements.txt # these are packages needed for the custom tools used in the example (PIL and cariosvg)

ls -R assets

assets/:
atlases  test.txt

assets/atlases:
atari_8bit_font.atlas  atari_8bit_font.png

python Amake.py

[0%  ] building ... 
[11% ] LinkingTool "assets/output.log"
[22% ] CopyingTool "assets/test.txt"
[33% ] LinkingTool "assets/atlases/atari_8bit_font.png"
[44% ] LinkingTool "assets/atlases/atari_8bit_font.atlas"
[55% ] LinkingTool "assets/output.svg"
[66% ] AtlasTool "assets/atlases/atari_8bit_font.atlas"
[77% ] SVGtoPNGTool "assets/output.svg"
[88% ] LinkingTool "assets/output.png"
[100%] CompressionTool "build/atlases/atari_8bit_font.atlas.bin"

ls -R build

build/:
atlases  output.log (link)  output.png (link)  output.svg (link)  test.txt # Note debug=True writes a output.log output.svg and output.png to assets and they are linked to the build dir

build/atlases:
atari_8bit_font.atlas (link)  atari_8bit_font.atlas.bin  atari_8bit_font.atlas.bin.z (88% compression) atari_8bit_font.png (link)


feh build/output.png
```
![Bipartite Graph of files and tools](https://raw.githubusercontent.com/MasonJohnHawver42/AssetForge/refs/heads/master/exp/assets/output.png)

**Note:** the debug graph of the flow of files as inputs and output to tools also includes itself - **meta!**

## Getting Started

1. **Create an `Amake.py` file:**

```python
import AssetForge

from pathlib import Path

from amake import atlas, svg

AssetForge.RegisterTool(AssetForge.common.CopyingTool(pattern=r"^.*\.txt$"),  priority=1)  
AssetForge.RegisterTool(AssetForge.common.CompressionTool(),                  priority=5) 
AssetForge.RegisterTool(AssetForge.common.LinkingTool(),                      priority=0)  
AssetForge.RegisterTool(atlas.AtlasTool(),                                    priority=3)  
AssetForge.RegisterTool(svg.SVGtoPNGTool(),                                   priority=3)  


AssetForge.Build(Path("assets"), Path("build"), recursive=True, parallel=True, debug=True)
```

2. **Add/write scripts in `amake`:**

Read the documentation for more information on this. But all you need to do to create a tool is implement `AssetTool`.

3. **Run the build:**

```bash
python Amake.py
```

## Tools Overview

Example/Custom:

- **AtlasTool**:  
  Processes a `.atlas` file (a JSON describing sprite bounds in a human-readable format) into a `.atlas.bin` binary file. This binary file can then be loaded directly into C++ containers (e.g., a `std::vector` of AABBs and a `std::unordered_map<std::string, unsigned int>`).

- **SVGtoPNGTool**:  
  Converts `.svg` files into `.png` files, using CairoSVG for the conversion.

General:

- **CompressionTool**:  
  Compresses `.bin` files (such as `.atlas.bin`) into `.bin.z` files.

- **CopyingTool**:  
  Copies files (that match the given pattern) from the input to the output directory, often used when simple duplication is sufficient.

- **LinkingTool**:  
  Creates symbolic links for files from the input directory to the output directory, avoiding data duplication.



