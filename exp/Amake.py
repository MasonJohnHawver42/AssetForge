import AssetForge

from pathlib import Path

from amake import atlas, text, compress

AssetForge.RegisterTool(compress.CompressTool(), 3) 
AssetForge.RegisterTool(atlas.AtlasTool(), 2)  
AssetForge.RegisterTool(text.TextTool(), 1)  
AssetForge.RegisterTool(AssetForge.common.General(), 0)  

AssetForge.Build(Path("assets"), Path("build"), recursive=True, parallel=True)