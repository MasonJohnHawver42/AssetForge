import AssetForge

from pathlib import Path

from amake import atlas, svg

AssetForge.RegisterTool(AssetForge.common.CopyingTool(pattern=r"^.*\.txt$"),  priority=1)  
AssetForge.RegisterTool(AssetForge.common.CompressionTool(),                  priority=5) 
AssetForge.RegisterTool(AssetForge.common.IgnoreItToolDecorator(AssetForge.common.LinkingTool(), "linkignore"),                      priority=0)  
AssetForge.RegisterTool(atlas.AtlasTool(),                                    priority=3)  
AssetForge.RegisterTool(svg.SVGtoPNGTool(),                                   priority=3)  

AssetForge.Build(Path("assets"), Path("build"), recursive=True, parallel=False, debug=True, quiet=True)