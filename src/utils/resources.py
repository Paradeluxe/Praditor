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

def get_config_path(config_name):
    """
    获取配置文件的路径，优先从当前目录读取，否则使用打包内的默认配置
    
    Args:
        config_name: 配置文件名
        
    Returns:
        配置文件的路径
    """
    # 优先从当前目录读取
    local_path = os.path.join(os.getcwd(), config_name)
    if os.path.exists(local_path):
        return local_path
    # 否则使用打包内的默认配置
    return get_resource_path(f'config/{config_name}')
