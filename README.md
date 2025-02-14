# Asset Forge

Cmake for video game asset. With this utility you will be able to preprocess your assets files which are human/tool readable/usable into binary files that can be directly streamed into a C/C++ struct/class. This process will stream line loading complex assets in small video game projects written in C/C++ or other systems languages. 

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

Note: `amake` is a folder of scripts that define the specific instructions for preprocessing .txt, .atlas, and .bin files.

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
```

```bash
ls -R output_folder

build:
atlases  output.log  test.txt

build/atlases:
atari_8bit_font.atlas (link)  atari_8bit_font.atlas.bin  atari_8bit_font.atlas.bin.z  atari_8bit_font.png (link)
```

check out `exp` for the full example of this.



