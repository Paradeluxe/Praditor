import logging
import sys
from logging.handlers import RotatingFileHandler

# 全局GUI回调函数，用于更新GUI标签
gui_callback = None

class GUIHandler(logging.Handler):
    """自定义Handler，将日志消息发送到GUI"""
    def emit(self, record):
        if gui_callback:
            msg = self.format(record)
            gui_callback(msg)

def setup_logger(name='Praditor', level=logging.INFO):
    """设置日志记录器
    
    Args:
        name: 日志记录器名称，默认'Praditor'
        level: 日志级别，默认logging.INFO
        
    Returns:
        配置好的日志记录器对象
    """
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 定义日志格式（只包含消息内容）
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # 创建GUI处理器
    gui_handler = GUIHandler()
    gui_handler.setLevel(level)
    gui_handler.setFormatter(formatter)
    
    # 添加处理器到logger（仅保留控制台和GUI）
    logger.addHandler(console_handler)
    logger.addHandler(gui_handler)
    
    return logger

# 创建默认logger
logger = setup_logger()

# 为不同模块创建子logger
system_logger = logging.getLogger('Praditor.System')
player_logger = logging.getLogger('Praditor.Player')
params_logger = logging.getLogger('Praditor.Params')
file_logger = logging.getLogger('Praditor.File')
sot_logger = logging.getLogger('Praditor.SOT')