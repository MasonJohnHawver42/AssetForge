import AssetForge

from amake import atlas, text

AssetForge.RegisterTool(atlas.AtlasTool(), 10)  
AssetForge.RegisterTool(text.TextTool(), 1)  
AssetForge.RegisterTool(AssetForge.common.General(), 0)  

AssetForge.Build("assets", "build")