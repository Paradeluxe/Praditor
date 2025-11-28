import os
import sys

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径，支持PyInstaller打包
    
    Args:
        relative_path: 资源文件的相对路径，相对于项目根目录
        
    Returns:
        资源文件的绝对路径
    """
    try:
        # PyInstaller打包后的临时目录
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境下的相对路径
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    
    return os.path.normpath(os.path.join(base_path, relative_path))

