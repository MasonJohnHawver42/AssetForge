# Asset Forge

<div style="display: flex; align-items: top;">
  <img src="icon.png" alt="credit: Dalle3" title="Icon" width="220px" style="margin-right: 15px; aspect-ratio: 1; height: auto;">
  <span>
    <p>
        <strong>Asset Forge</strong>: CMake for video game assets. With this utility, you will be able to preprocess your asset files, which are human and tool-readable/usable, into binary files that can be directly streamed into C/C++ structs and classes. This process will streamline loading complex assets in small video game projects written in C/C++ or other systems languages.
    </p>
    <p style="margin-bottom: 0px">
        Instead of linking several libraries dedicated to loading different types of files: meshes, animations, sprite sheets, and etc. Now you can just write a simple python script that loads in any complicated mesh/assimp file, optimize the mesh, do some precalculations for vertex normals and tangent vectors, then package it into a binary file that can be easily loaded in C/C++ by streaming the data into a struct or class that has a mirror structure to the binary file.
    </p>
  </span>
</div>

<br>

First define a Amake.py file:
```python
import AssetForge
from amake import atlas, text, compress

from pathlib import Path

AssetForge.RegisterTool(compress.CompressTool(), 3) 
AssetForge.RegisterTool(atlas.AtlasTool(), 2)  
AssetForge.RegisterTool(text.TextTool(), 1)  
AssetForge.RegisterTool(AssetForge.common.General(), 0)  

AssetForge.Build(input_folder=Path("assets"), output_folder=Path("build"), recursive=True, parallel=True)
```

Then run:
```bash
python Amake.py
```

Note: `amake` in `from amake import atlas, text, compress` is a folder of scripts that define the specific instructions for preprocessing .txt, .atlas, and .bin files:

 - AtlasTool takes in a .atlas file which is just a json which defines the aabb of sprites in an image in a human readable json format, and outputs a .atlas.bin file which is binary that can be directly loaded into a `std::vector` of aabbs and a `std::unordered_map<std::string, unsigned int>` in C++
 - CompressTool takes .bin files (like .atlas.bin) and compresses them into .bin.z files 
 - TextTool just copies all .txt files from  input dir to the output dir
 - General is a base case which links every other file not captured by the other tools into the output dir from the input dir

The result of `python Amake.py`:

```bash
ls -R input_folder

assets/:
atlases  test.txt

assets/atlases:
atari_8bit_font.atlas  atari_8bit_font.png

python Amake.py
[0%  ] building ... 
[20% ] General "assets/atlases/atari_8bit_font.atlas"
[40% ] TextTool "assets/test.txt"
[60% ] General "assets/atlases/atari_8bit_font.png"
[80% ] AtlasTool "assets/atlases/atari_8bit_font.atlas"
[100%] CompressTool "build/atlases/atari_8bit_font.atlas.bin"
```

```bash
ls -R output_folder

build:
atlases  output.log  test.txt

build/atlases:
atari_8bit_font.atlas (link)  atari_8bit_font.atlas.bin  atari_8bit_font.atlas.bin.z (60% compression) atari_8bit_font.png (link)
```

check out `exp` for the full example of this.



