# __init__.py
"""Bing 壁纸获取和设置工具包"""

# 包版本信息
__version__ = "1.0.0"

# 定义公共接口
__all__ = ["WallpaperApp"]

# 从主模块导入主要的类
from .bing_wallpaper import WallpaperApp
