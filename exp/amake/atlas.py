import AssetForge

import json
import struct
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image

class AtlasTool(AssetForge.AssetTool):
    """
    AtlasTool implements AssetTool.

    Binary format:
    - Unsigned int (4 bytes): number of entries.
    - Unsigned int (4 bytes): size of text blob.
    - UV data block: Each entry has 4 floats (16 bytes per entry).
    - Text blob: Null-terminated strings for each entry id.

    C++ Loading Code:
    ------------------------------------------------------
    /*
    struct AtlasEntry {
        float uv_min[2]; // [x, y] scaled to 0 - 1
        float uv_max[2]; // [x + w, y + h] scaled to 0 - 1
    };

    struct Atlas {
        std::vector<AtlasEntry> entries;
        std::unordered_map<std::string, unsigned int> name_to_index;
    };

    Atlas loadAtlas(const void* data) {
        const unsigned char* bytes = static_cast<const unsigned char*>(data);
        
        unsigned int numEntries;
        unsigned int textBlobSize;
        memcpy(&numEntries, bytes, sizeof(unsigned int));
        memcpy(&textBlobSize, bytes + sizeof(unsigned int), sizeof(unsigned int));

        Atlas atlas;
        atlas.entries.resize(numEntries);

        // UV data block
        size_t uvDataOffset = 2 * sizeof(unsigned int);
        size_t uvDataSize = numEntries * 16; // 16 bytes per entry (4 floats)
        memcpy(atlas.entries.data(), bytes + uvDataOffset, uvDataSize);

        // Text blob
        const char* textBlob = reinterpret_cast<const char*>(bytes + uvDataOffset + uvDataSize);
        size_t pos = 0;
        unsigned int index = 0;
        while (pos < textBlobSize) {
            std::string name(textBlob + pos);
            atlas.name_to_index[name] = index++;
            pos += name.length() + 1; // Skip null terminator
        }

        return atlas;
    }
    */
    ------------------------------------------------------
    """
    
    def check_match(self, file_path: Path) -> bool:
        # Accept files with the .atals extension.
        return file_path.suffixes.count(".atlas") == 1 and file_path.is_relative_to(self.input_folder)

    def define_dependencies(self, file_path: Path) -> List[Path]:
        # The JSON atlas file references an image.
        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if data["type"] == "single_image":
                return [file_path.parent / Path(data["image"])]
            else:
                raise NotImplementedError("Haven't implemented that type of atlas yet")
        except Exception as e:
            print(f"Atlas Error reading {file_path}: {e}")
        
        return []

    def define_outputs(self, file_path: Path) -> List[Path]:
        return [self.output_folder / self.relative_path(file_path.with_suffix(".atlas.bin"))]
    
    def build(self, file_path: Path) -> None:
        # Read the atlas JSON data.
        json_path = file_path

        try:
            with json_path.open("r", encoding="utf-8") as f:
                atlas_data = json.load(f)
        except Exception as e:
            print(f"Error reading atlas JSON file {file_path}: {e}")
            return

        image_filename = atlas_data.get("image")
        
        if not image_filename:
            print(f"No image specified in {file_path}")
            return

        # Resolve the image path relative to the atlas file.
        image_path = file_path.parent / Path(image_filename)

        # Open the image to determine its dimensions.
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            return

        entries = atlas_data.get("entries", [])
        uv_data = bytearray()

        # For each atlas entry, compute UV coordinates (as floats scaled to 0–1)
        for entry in entries:
            x = entry.get("x", 0)
            y = entry.get("y", 0)
            width = entry.get("width", 0)
            height = entry.get("height", 0)
            uv_min_x = x / img_width
            uv_min_y = y / img_height
            uv_max_x = (x + width) / img_width
            uv_max_y = (y + height) / img_height
            uv_data += struct.pack("ffff", uv_min_x, uv_min_y, uv_max_x, uv_max_y)

        # Build the text blob: each entry's id is null-terminated.
        text_blob = bytearray()
        for entry in entries:
            name = entry.get("id", "")
            text_blob += name.encode("utf-8") + b'\0'

        text_blob_size = len(text_blob)
        header = struct.pack("II", len(entries), text_blob_size)

        output_bytes = header + uv_data + text_blob

        output_bin_file = self.output_folder / self.relative_path(file_path.with_suffix(".atlas.bin"))

        # Ensure the output folder exists.
        output_bin_file.parent.mkdir(parents=True, exist_ok=True)

        # Write the binary file.
        try:
            with output_bin_file.open("wb") as f:
                f.write(output_bytes)
            print(f"Atlas binary written to {output_bin_file}")
        except Exception as e:
            print(f"Error writing binary file {output_bin_file}: {e}")