import ctypes
import os
import sys
import webbrowser
import io

plat = os.name.lower()

if plat == 'nt':  # Windows
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'Praditor') # arbitrary string
elif plat == 'posix':  # Unix-like systems (Linux, macOS)
    pass
else:
    pass



# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtCore import Qt, QUrl, Signal, QPoint, QRectF, QRunnable, QThreadPool, QObject, QThread, QTimer
from PySide6.QtGui import QAction, QIcon, QCursor, QPainterPath, QPainter, QColor
from PySide6.QtMultimedia import QAudioOutput, QAudio, \
    QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog, QWidget, QToolBar, QPushButton, QSizePolicy, QMessageBox, QLabel
)

from src.gui.styles import *
from src.core.detection import detectPraditor, create_textgrid_with_time_point, stop_flag
from src.gui.plots import AudioViewer
from src.gui.sliders import MySliders
from src.utils.audio import isAudioFile, get_frm_points_from_textgrid, get_frm_intervals_from_textgrid
from src.utils.resources import get_resource_path

# 自定义输出流类，用于捕获print语句
class ConsoleOutput(io.StringIO):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.buffer = ""
    
    def write(self, text):
        self.buffer += text
        # 当遇到换行符时，发送完整行
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            # 发送所有完整行
            for line in lines[:-1]:
                if line.strip():
                    self.callback(line.strip())
            # 保留最后一个不完整行
            self.buffer = lines[-1]
    
    def flush(self):
        # 确保所有缓冲内容都被发送
        if self.buffer.strip():
            self.callback(self.buffer.strip())
            self.buffer = ""

# 异步检测任务类
class DetectPraditorThread(QThread):
    finished = Signal(list, list)  # 参数：onset_results, offset_results
    
    def __init__(self, params, audio_obj, mode):
        super().__init__()
        self.params = params
        self.audio_obj = audio_obj
        self.mode = mode
        self.setTerminationEnabled(True)  # 启用线程终止
    
    def stop(self):
        """安全停止线程"""

        # 设置全局停止标志
        from src.core import detection
        detection.stop_flag = True

        # 如果线程正在运行，尝试优雅终止
        if self.isRunning():
            self.terminate()
            # 限制等待时间，避免无限阻塞
            if not self.wait(1000):  # 1秒超时
                self.terminate()
                print(f"Thread termination timed out")

        
    
    def run(self):
        from src.core import detection
        try:

            onset_results, offset_results = [], []

            if self.params["onset"]:
                onset_results = detectPraditor(self.params, self.audio_obj, "onset", self.mode)
            else:
                onset_results = []


            if self.params["offset"]:
                offset_results = detectPraditor(self.params, self.audio_obj, "offset", self.mode)
            else:
                offset_results = []


            self.finished.emit(onset_results, offset_results)


            
        except Exception as e:
            if not detection.stop_flag:
                print(f"Thread error: {e}")
                self.finished.emit([], [])



class CustomTitleBar(QWidget):
    """自定义Windows风格标题栏，类似Trae样式"""
    
    # 定义信号
    close_signal = Signal()
    minimize_signal = Signal()
    maximize_signal = Signal()
    file_menu_clicked = Signal()
    help_menu_clicked = Signal()
    run_signal = Signal()
    run_all_signal = Signal()
    test_signal = Signal()
    trash_signal = Signal()
    read_signal = Signal()
    onset_signal = Signal()
    offset_signal = Signal()
    prev_audio_signal = Signal()
    next_audio_signal = Signal()
    stop_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化拖拽变量
        self.drag_position = QPoint()
        
        # 设置标题栏样式，确保完全覆盖默认菜单栏区域
        # 移除固定高度，改为随内容自适应
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #FFFFFF;
                border-width: 2px 2px 0px 2px;
                border-style: solid;
                border-color: #E9EDF1;
                margin: 0px;
                padding: 4px 0;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        
        # 确保背景完全填充，没有任何间隙
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        
        # 创建布局，设置垂直居中对齐
        layout = QHBoxLayout(self)  # 直接将布局应用到当前部件
        layout.setContentsMargins(8, 1, 8, 1)  # 左右各8px边距，上下无边距
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignVCenter)  # 垂直居中对齐

        
        self.help_menu_btn = QPushButton()
        self.help_menu_btn.setIcon(QIcon(get_resource_path('resources/icons/question.svg')))
        self.help_menu_btn.setFixedSize(32, 32)
        self.help_menu_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.help_menu_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        # 通用提示框样式
        self.tooltip_style = """
            QLabel {
                background-color: #FFFFE1;
                color: #000000;
                padding: 4px 6px;
                border: 1px solid #D4D4D4;
                border-radius: 3px;
                font-size: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        """
        
        # 通用提示框创建函数
        def create_tooltip(text):
            tooltip = QLabel()
            tooltip.setText(text)
            tooltip.setStyleSheet(self.tooltip_style)
            tooltip.setAlignment(Qt.AlignLeft)
            tooltip.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
            tooltip.hide()
            return tooltip
        
        # 通用hover事件处理函数
        def create_hover_handlers(btn, tooltip):
            def show_tooltip(event):
                # 只有当控件不是title_label、onset_btn和offset_btn时才应用hover样式
                if btn != self.title_label and btn != self.onset_btn and btn != self.offset_btn:
                    # 保存原始样式
                    original_style = btn.styleSheet()
                    # 应用hover样式
                    btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
                # 计算提示框位置：按钮右下角
                btn_pos = btn.mapToGlobal(QPoint(0, 0))
                # 先调整大小以确保size准确
                tooltip.adjustSize()
                # 位置：按钮右下角，提示框左上角与按钮右下角完全对齐
                x = btn_pos.x() + btn.width()
                y = btn_pos.y() + btn.height()
                tooltip.move(x, y)
                tooltip.show()
                event.accept()
            
            def hide_tooltip(event):
                # 只有当控件不是title_label、onset_btn和offset_btn时才恢复原始样式
                if btn != self.title_label and btn != self.onset_btn and btn != self.offset_btn:
                    # 恢复原始样式
                    btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
                tooltip.hide()
                event.accept()
            
            return show_tooltip, hide_tooltip
        
        # 连接菜单按钮信号
        self.help_menu_btn.clicked.connect(self.help_menu_clicked.emit)
        
        # 为help按钮添加提示框
        self.help_tooltip = create_tooltip("Open help documentation")
        show_help_tooltip, hide_help_tooltip = create_hover_handlers(self.help_menu_btn, self.help_tooltip)
        self.help_menu_btn.enterEvent = show_help_tooltip
        self.help_menu_btn.leaveEvent = hide_help_tooltip
        
        # 添加设置按钮到布局左侧
        layout.addWidget(self.help_menu_btn)
        
        # 添加标题标签，设置居左显示（Windows风格）
        self.title_label = QLabel("Praditor")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 居左垂直居中
        self.title_label.setStyleSheet("font-size: 13px; border: none; font-weight: bold; color: #333333; padding: 5px 10px 5px 5px;")
        # 设置标题标签为可点击，鼠标指针为手形
        self.title_label.setCursor(QCursor(Qt.PointingHandCursor))
        # 将标题点击事件连接到file_menu_clicked信号
        self.title_label.mousePressEvent = lambda event: self.file_menu_clicked.emit()

        # 为prev_audio_btn添加提示框
        self.title_label_tooltip = create_tooltip("Select an audio file")
        show_title_label_tooltip, hide_title_label_tooltip = create_hover_handlers(self.title_label, self.title_label_tooltip)
        self.title_label.enterEvent = show_title_label_tooltip
        self.title_label.leaveEvent = hide_title_label_tooltip
        layout.addWidget(self.title_label)
 
        
        # 添加伸缩空间，将按钮推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setStyleSheet("border: none;")
        layout.addWidget(spacer)
          

        # 添加前一个音频按钮
        self.prev_audio_btn = QPushButton()
        self.prev_audio_btn.setIcon(QIcon(get_resource_path('resources/icons/prev_audio.svg')))
        self.prev_audio_btn.setFixedSize(32, 32)
        self.prev_audio_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.prev_audio_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.prev_audio_btn.setStatusTip("Previous Audio")
        # 为prev_audio_btn添加提示框
        self.prev_audio_tooltip = create_tooltip("Previous Audio")
        show_prev_tooltip, hide_prev_tooltip = create_hover_handlers(self.prev_audio_btn, self.prev_audio_tooltip)
        self.prev_audio_btn.enterEvent = show_prev_tooltip
        self.prev_audio_btn.leaveEvent = hide_prev_tooltip
        layout.addWidget(self.prev_audio_btn)
        
        # 添加后一个音频按钮
        self.next_audio_btn = QPushButton()
        self.next_audio_btn.setIcon(QIcon(get_resource_path('resources/icons/next_audio.svg')))
        self.next_audio_btn.setFixedSize(32, 32)
        self.next_audio_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.next_audio_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_audio_btn.setStatusTip("Next Audio")
        # 为next_audio_btn添加提示框
        self.next_audio_tooltip = create_tooltip("Next Audio")
        show_next_tooltip, hide_next_tooltip = create_hover_handlers(self.next_audio_btn, self.next_audio_tooltip)
        self.next_audio_btn.enterEvent = show_next_tooltip
        self.next_audio_btn.leaveEvent = hide_next_tooltip
        layout.addWidget(self.next_audio_btn)


        layout.addSpacing(8)  # 添加按钮之间的空格


        # 添加onset和offset按钮
        self.onset_btn = QPushButton("Onset")
        self.onset_btn.setStatusTip("Extract Onsets")
        self.onset_btn.setFixedSize(80, 25)
        onset_color = "#1991D3"
        self.onset_btn.setStyleSheet(f"QPushButton {{ background: {onset_color}; color: white; font-weight: bold; border: 2px solid {onset_color}; border-radius: 5px; margin: 0px; font-size: 13px; }} QPushButton:pressed {{ background: #666666; color: {onset_color}; font-weight: bold; border: 2px solid {onset_color}; border-radius: 5px; margin: 0px; }} QPushButton:checked {{ background-color: white; color: {onset_color}; border: 2px solid {onset_color}; font-weight: bold; border-radius: 5px; margin: 0px; }}")
        self.onset_btn.setCheckable(True)
        self.onset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 为onset_btn添加提示框
        self.onset_tooltip = create_tooltip("Extract Onsets")
        show_onset_tooltip, hide_onset_tooltip = create_hover_handlers(self.onset_btn, self.onset_tooltip)
        self.onset_btn.enterEvent = show_onset_tooltip
        self.onset_btn.leaveEvent = hide_onset_tooltip
        layout.addWidget(self.onset_btn)
        
        layout.addSpacing(8)  # 添加按钮之间的空格
        
        self.offset_btn = QPushButton("Offset")
        self.offset_btn.setStatusTip("Extract Offsets")
        self.offset_btn.setFixedSize(80, 25)
        offset_color = "#2AD25E"
        self.offset_btn.setStyleSheet(f"QPushButton {{ background: {offset_color}; color: white; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; font-size: 13px; }} QPushButton:pressed {{ background: #666666; color: {offset_color}; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; }} QPushButton:checked {{ background-color: white; color: {offset_color}; border: 2px solid {offset_color}; font-weight: bold; border-radius: 5px; margin: 0px; }}")
        self.offset_btn.setCheckable(True)
        self.offset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 为offset_btn添加提示框
        self.offset_tooltip = create_tooltip("Extract Offsets")
        show_offset_tooltip, hide_offset_tooltip = create_hover_handlers(self.offset_btn, self.offset_tooltip)
        self.offset_btn.enterEvent = show_offset_tooltip
        self.offset_btn.leaveEvent = hide_offset_tooltip
        layout.addWidget(self.offset_btn)
        
        layout.addSpacing(8)  # 添加按钮之间的空格
        
        # 连接onset和offset按钮信号
        self.onset_btn.pressed.connect(self.onset_signal.emit)
        self.offset_btn.pressed.connect(self.offset_signal.emit)
        
        # 添加trash按钮（用于清除onsets和offsets）
        self.trash_btn = QPushButton()
        self.trash_btn.setIcon(QIcon(get_resource_path('resources/icons/trash.svg')))
        self.trash_btn.setFixedSize(32, 32)
        self.trash_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.trash_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 为trash_btn添加提示框
        self.trash_tooltip = create_tooltip("Clear onsets and offsets")
        show_trash_tooltip, hide_trash_tooltip = create_hover_handlers(self.trash_btn, self.trash_tooltip)
        self.trash_btn.enterEvent = show_trash_tooltip
        self.trash_btn.leaveEvent = hide_trash_tooltip
        layout.addWidget(self.trash_btn)
        
        # 添加read按钮（用于显示onsets和offsets）
        self.read_btn = QPushButton()
        self.read_btn.setIcon(QIcon(get_resource_path('resources/icons/read.svg')))
        self.read_btn.setFixedSize(32, 32)
        self.read_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.read_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 为read_btn添加提示框
        self.read_tooltip = create_tooltip("Display onsets and offsets")
        show_read_tooltip, hide_read_tooltip = create_hover_handlers(self.read_btn, self.read_tooltip)
        self.read_btn.enterEvent = show_read_tooltip
        self.read_btn.leaveEvent = hide_read_tooltip
        layout.addWidget(self.read_btn)
        
        # 添加运行按钮（类似IDE中的播放键）
        self.run_btn = QPushButton()
        self.run_btn.setIcon(QIcon(get_resource_path('resources/icons/play.svg')))
        self.run_btn.setFixedSize(32, 32)
        self.run_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.run_btn.setCursor(QCursor(Qt.PointingHandCursor))

        # 为run_btn添加提示框
        self.run_tooltip = create_tooltip("Run Praditor on audio")
        show_run_tooltip, hide_run_tooltip = create_hover_handlers(self.run_btn, self.run_tooltip)
        self.run_btn.enterEvent = show_run_tooltip
        self.run_btn.leaveEvent = hide_run_tooltip
        layout.addWidget(self.run_btn)
        
        # 添加run-all按钮
        self.run_all_btn = QPushButton()
        self.run_all_btn.setIcon(QIcon(get_resource_path('resources/icons/run-all.svg')))
        self.run_all_btn.setFixedSize(32, 32)
        self.run_all_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.run_all_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 为run_all_btn添加提示框
        self.run_all_tooltip = create_tooltip("Run Praditor on all audio files")
        show_run_all_tooltip, hide_run_all_tooltip = create_hover_handlers(self.run_all_btn, self.run_all_tooltip)
        self.run_all_btn.enterEvent = show_run_all_tooltip
        self.run_all_btn.leaveEvent = hide_run_all_tooltip
        layout.addWidget(self.run_all_btn)
        
        # 添加停止按钮
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon(get_resource_path('resources/icons/stop.svg')))
        self.stop_btn.setFixedSize(32, 32)
        self.stop_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.stop_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 为stop_btn添加提示框
        self.stop_tooltip = create_tooltip("Stop Praditor detection")
        show_stop_tooltip, hide_stop_tooltip = create_hover_handlers(self.stop_btn, self.stop_tooltip)
        self.stop_btn.enterEvent = show_stop_tooltip
        self.stop_btn.leaveEvent = hide_stop_tooltip
        layout.addWidget(self.stop_btn)
        
        # 添加测试按钮
        self.test_btn = QPushButton()
        self.test_btn.setIcon(QIcon(get_resource_path('resources/icons/test.svg')))
        self.test_btn.setFixedSize(32, 32)
        self.test_btn.setStyleSheet("background-color: transparent; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.test_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 为test_btn添加提示框
        self.test_tooltip = create_tooltip("Test Praditor on audio")
        show_test_tooltip, hide_test_tooltip = create_hover_handlers(self.test_btn, self.test_tooltip)
        self.test_btn.enterEvent = show_test_tooltip
        self.test_btn.leaveEvent = hide_test_tooltip
        layout.addWidget(self.test_btn)
        
        # 创建窗口控制按钮（Windows风格）
        self.close_btn = QPushButton()
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        
        # 设置按钮样式和大小（Windows风格：方形按钮，较大尺寸）
        btn_size = 32
        for btn in [self.close_btn, self.minimize_btn, self.maximize_btn]:
            btn.setFixedSize(btn_size, btn_size)
            btn.setStyleSheet("background-color: white; border: none; color: #333333;")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        # 使用SVG图标
        self.minimize_btn.setIcon(QIcon(get_resource_path('resources/icons/minimize.svg')))
        self.maximize_btn.setIcon(QIcon(get_resource_path('resources/icons/maximize.svg')))
        self.close_btn.setIcon(QIcon(get_resource_path('resources/icons/close.svg')))
        
        # 按钮颜色配置（Windows风格）
        self.btn_colors = {
            'close': {
                'normal': 'transparent',
                'hover': '#FF5F57',
                'pressed': '#FF453A'
            },
            'minimize': {
                'normal': 'transparent',
                'hover': '#E8E8E8',
                'pressed': '#D5D5D5'
            },
            'maximize': {
                'normal': 'transparent',
                'hover': '#E8E8E8',
                'pressed': '#D5D5D5'
            }
        }
        
        # 设置初始按钮颜色
        self.update_button_style(self.close_btn, 'close', 'normal')
        self.update_button_style(self.minimize_btn, 'minimize', 'normal')
        self.update_button_style(self.maximize_btn, 'maximize', 'normal')
        
        # 移除窗口控制按钮的提示框
        
        # 连接按钮信号
        self.trash_btn.clicked.connect(self.trash_signal.emit)
        self.read_btn.clicked.connect(self.read_signal.emit)
        self.run_btn.clicked.connect(self.run_signal.emit)
        self.run_all_btn.clicked.connect(self.run_all_signal.emit)
        self.stop_btn.clicked.connect(self.stop_signal.emit)
        self.test_btn.clicked.connect(self.test_signal.emit)
        self.prev_audio_btn.clicked.connect(self.prev_audio_signal.emit)
        self.next_audio_btn.clicked.connect(self.next_audio_signal.emit)
        self.close_btn.clicked.connect(self.close_signal.emit)
        self.minimize_btn.clicked.connect(self.minimize_signal.emit)
        self.maximize_btn.clicked.connect(self.maximize_signal.emit)
        
        # 连接按钮事件
        self.connect_button_events()
        
        # 将按钮添加到布局右侧（顺序：最小化、最大化、关闭，Windows风格）
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
    
    def connect_button_events(self):
        """连接按钮事件"""
        # 关闭按钮
        def close_enter_event(event):
            self.update_button_style(self.close_btn, 'close', 'hover')
            event.accept()
        
        def close_leave_event(event):
            self.update_button_style(self.close_btn, 'close', 'normal')
            event.accept()
        
        self.close_btn.enterEvent = close_enter_event
        self.close_btn.leaveEvent = close_leave_event
        self.close_btn.pressed.connect(lambda: self.update_button_style(self.close_btn, 'close', 'pressed'))
        self.close_btn.released.connect(lambda: self.update_button_style(self.close_btn, 'close', 'hover'))
        
        # 最小化按钮
        def minimize_enter_event(event):
            self.update_button_style(self.minimize_btn, 'minimize', 'hover')
            event.accept()
        
        def minimize_leave_event(event):
            self.update_button_style(self.minimize_btn, 'minimize', 'normal')
            event.accept()
        
        self.minimize_btn.enterEvent = minimize_enter_event
        self.minimize_btn.leaveEvent = minimize_leave_event
        self.minimize_btn.pressed.connect(lambda: self.update_button_style(self.minimize_btn, 'minimize', 'pressed'))
        self.minimize_btn.released.connect(lambda: self.update_button_style(self.minimize_btn, 'minimize', 'hover'))
        
        # 最大化按钮
        def maximize_enter_event(event):
            self.update_button_style(self.maximize_btn, 'maximize', 'hover')
            event.accept()
        
        def maximize_leave_event(event):
            self.update_button_style(self.maximize_btn, 'maximize', 'normal')
            event.accept()
        
        self.maximize_btn.enterEvent = maximize_enter_event
        self.maximize_btn.leaveEvent = maximize_leave_event
        self.maximize_btn.pressed.connect(lambda: self.update_button_style(self.maximize_btn, 'maximize', 'pressed'))
        self.maximize_btn.released.connect(lambda: self.update_button_style(self.maximize_btn, 'maximize', 'hover'))
        
        # 运行按钮、测试按钮、trash按钮和read按钮的hover事件已在__init__方法中设置
    
    def update_button_style(self, btn, btn_type, state):
        """更新按钮样式（现代Windows风格）"""
        # 当状态为normal时，使用透明背景，否则使用配置的颜色
        if state == 'normal':
            color = 'transparent'
        else:
            color = self.btn_colors[btn_type][state]
        
        # 为不同按钮设置不同的字体大小，确保图标比例协调
        font_sizes = {
            'minimize': 18,
            'maximize': 14,
            'close': 20
        }
        font_size = font_sizes.get(btn_type, 16)
        
        # 对于关闭按钮，悬停和按下时文字颜色变为白色
        if btn_type == 'close' and (state == 'hover' or state == 'pressed'):
            btn.setStyleSheet(f"background-color: {color}; border: none; color: white; font-size: {font_size}px; font-weight: normal; text-align: center; padding: 0px; margin: 0px;")
        else:
            # 其他按钮保持默认文字颜色
            btn.setStyleSheet(f"background-color: {color}; border: none; color: #333333; font-size: {font_size}px; font-weight: normal; text-align: center; padding: 0px; margin: 0px;")
    
    def mousePressEvent(self, event):
        """实现拖拽功能"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """实现拖拽功能"""
        if event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def set_title(self, title):
        """设置标题，确保Praditor部分加粗"""
        if "Praditor" in title:
            # 将Praditor部分加粗，其他部分保持正常
            parts = title.split("Praditor")
            formatted_title = f"<b>Praditor</b>{parts[1] if len(parts) > 1 else ''}"
            self.title_label.setText(formatted_title)
        else:
            # 如果标题中没有Praditor，直接设置
            self.title_label.setText(title)
        # 确保标签支持HTML格式
        self.title_label.setTextFormat(Qt.RichText)
    
    def update_maximize_button(self, is_maximized):
        """更新最大化按钮状态"""
        # macOS风格下，最大化按钮样式不变，只改变功能
        pass
    
    def _setButtonEnabled(self, button, icon_name, enabled):
        """设置按钮是否可用，并自动切换图标
        
        Args:
            button (QPushButton): 要设置的按钮
            icon_name (str): 图标名称（不带.svg后缀）
            enabled (bool): 是否可用
        """
        # 设置按钮可用性
        button.setEnabled(enabled)
        
        # 根据状态切换图标
        if enabled:
            button.setIcon(QIcon(get_resource_path(f'resources/icons/{icon_name}.svg')))
        else:
            button.setIcon(QIcon(get_resource_path(f'resources/icons/{icon_name}_gray.svg')))


class MainWindow(QMainWindow):
    run_current_done = Signal()

    def __init__(self):
        super().__init__()

        # 隐藏默认标题栏，使用自定义标题栏
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        
        # 设置窗口属性，实现带有抗锯齿的圆角
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_StyledBackground, False)
        
        # load window icon
        # self.setWindowIcon(QIcon(QPixmap(resource_path('icon.png'))))
        # 将param_sets改为字典，分别存储默认模式和VAD模式的参数
        self.param_sets = {
            "default": [],  # 默认模式参数集
            "vad": []      # VAD模式参数集
        }
        # 分别为两种模式维护当前索引
        self.current_param_index = {
            "default": -1,  # 默认模式当前索引
            "vad": -1       # VAD模式当前索引
        }
        self.audio_sink = None
        self.buffer = None
        self.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.ico')))
        self.file_paths = []
        self.file_path = None
        self.which_one = 0
        self.setWindowTitle("Praditor")
        self.setMinimumSize(1000, 750)
        
        # 初始化线程池
        self.thread_pool = QThreadPool.globalInstance()
        self.detection_results = {"onset": [], "offset": []}
        self.detection_count = 0
        self.total_detections = 0
        self.current_runnables = []
        
        # run-all模式状态跟踪
        self.is_running_all = False
        self.run_all_current_index = 0
        # 存储按钮原始状态
        self._button_original_states = {}


        # 初始化媒体播放器和音频输出
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)

        self.player.setAudioOutput(self.audio_output)


        # MENU
        # --------------------------------------


        file_menu = self.menuBar().addMenu("&File")
        button_action = QAction("&Read file...", self)
        button_action.setStatusTip("Read audio files HERE!")
        button_action.triggered.connect(self.openFileDialog)
        file_menu.addAction(button_action)


        file_menu = self.menuBar().addMenu("&Help")
        button_action = QAction("&Instructions", self)
        button_action.setStatusTip("Folder to store target audios")
        button_action.triggered.connect(self.browseInstruction)
        file_menu.addAction(button_action)
        # file_menu.setStyleSheet("""
        #
        # """)
        self.menuBar().setStyleSheet("""            
        QMenuBar {
            background-color: #E9EDF1;
            font-size: 10px;
            color: black;
        }

        QMenu {
            color: black; 
            background-color: #EFEFEF;
            border: 1px solid #676767;
            height: 25px;

        }

        """)
        
        # 隐藏默认菜单栏，我们将在自定义标题栏中集成菜单功能
        self.menuBar().setVisible(False)
        
        # --------------------------------------



        # 创建自定义标题栏并设置为菜单栏部件，使其显示在工具栏上方
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)
        
        # 连接标题栏信号
        self.title_bar.close_signal.connect(self.close)
        self.title_bar.minimize_signal.connect(self.showMinimized)
        self.title_bar.maximize_signal.connect(self.toggleMaximize)
        self.title_bar.trash_signal.connect(self.clearXset)
        self.title_bar.read_signal.connect(self.readXset)
        self.title_bar.run_signal.connect(self.on_run_signal)
        self.title_bar.run_all_signal.connect(self.runAllAudioFiles)
        self.title_bar.test_signal.connect(self.on_test_signal)
        self.title_bar.stop_signal.connect(self.stopDetection)
        self.title_bar.onset_signal.connect(self.turnOnset)
        self.title_bar.offset_signal.connect(self.turnOffset)
        # 连接前后音频按钮信号
        self.title_bar.prev_audio_signal.connect(lambda: self.prevnext_audio("prev"))
        self.title_bar.next_audio_signal.connect(lambda: self.prevnext_audio("next"))
        
        # 更新run_onset和run_offset属性，使其指向标题栏中的按钮
        self.run_onset = self.title_bar.onset_btn
        self.run_offset = self.title_bar.offset_btn
        
        # 连接菜单按钮信号到相应方法
        self.title_bar.file_menu_clicked.connect(self.openFileDialog)
        self.title_bar.help_menu_clicked.connect(self.browseInstruction)
        
        # 创建主部件和布局
        main_widget = QWidget()
        main_widget.setObjectName("centralwidget")
        self.setCentralWidget(main_widget)
        
        # 创建垂直布局，包含内容
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        
        # 创建内容部件和布局
        central_widget = QWidget()
        layout = QVBoxLayout()  # 创建一个垂直布局
        central_widget.setLayout(layout)

        # ---------------------------------------------------
        self.AudioViewer = AudioViewer()
        self.AudioViewer.setMinimumHeight(200)
        layout.addWidget(self.AudioViewer, 1)  # 添加拉伸因子1，让AudioViewer占据更多空间
        
        # ---------------------------------------------------

        # ---------------------------------------------------
        # self.ParamButtons = ParamButtons()
        # layout.addWidget(self.ParamButtons)
        # ---------------------------------------------------

        # ---------------------------------------------------
        self.MySliders = MySliders()
        self.MySliders.setFixedHeight(320)  # 设置固定高度，避免过度拉伸
        self.MySliders.amp_slider_onset.setStatusTip(" Onset  |  A coef for determining actual threshold (baseline × coefficient = actual threshold)")
        self.MySliders.numValid_slider_onset.setStatusTip(" Onset  |  Accumulated net count of above-threshold frames")
        self.MySliders.penalty_slider_onset.setStatusTip(" Onset  |  Penalty for below-threshold frames")
        self.MySliders.ref_len_slider_onset.setStatusTip(" Onset  |  Length of the reference segment used to generate baseline (useful in detecting in-utterance silent pause)")
        self.MySliders.ratio_slider_onset.setStatusTip(r" Onset  |  % of frames retained in the kernel")
        self.MySliders.win_size_slider_onset.setStatusTip(" Onset  |  Size of the kernel (in frames)")
        self.MySliders.eps_ratio_slider_onset.setStatusTip(" Onset  |  Neighborhood radius in DBSCAN clustering (useful in detecting in-utterance silent pause)")
        self.MySliders.cutoff1_slider_onset.setStatusTip(" Onset  |  Higher cutoff frequency of bandpass filter")
        self.MySliders.cutoff0_slider_onset.setStatusTip(" Onset  |  Lower cutoff frequency of bandpass filter")


        self.MySliders.amp_slider_offset.setStatusTip(" Offset  |  A coef for determining actual threshold (baseline × coefficient = actual threshold)")
        self.MySliders.numValid_slider_offset.setStatusTip(" Offset  |  Accumulated net count of above-threshold frames")
        self.MySliders.penalty_slider_offset.setStatusTip(" Offset  |  Penalty for below-threshold frames")
        self.MySliders.ref_len_slider_offset.setStatusTip(" Offset  |  Length of the reference segment used to generate baseline (useful in detecting in-utterance silent pause)")
        self.MySliders.ratio_slider_offset.setStatusTip(" Offset  |  % of frames retained in the kernel")
        self.MySliders.win_size_slider_offset.setStatusTip(" Offset  |  Size of the kernel (in frames)")
        self.MySliders.eps_ratio_slider_offset.setStatusTip(" Offset  |  Neighborhood radius in DBSCAN clustering (useful in detecting in-utterance silent pause)")
        self.MySliders.cutoff1_slider_offset.setStatusTip(" Offset  |  Higher cutoff frequency of bandpass filter")
        self.MySliders.cutoff0_slider_offset.setStatusTip(" Offset  |  Lower cutoff frequency of bandpass filter")


        layout.addWidget(self.MySliders)
        # ---------------------------------------------------
        layout.setContentsMargins(50, 15, 50, 30)  # 调整左右边距为15px，上下保持不变
        # 将内容部件添加到主布局
        main_layout.addWidget(central_widget)
        
        # TOOLBAR
        # ---------------------

        toolbar = QToolBar("My main toolbar")

        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
        QToolBar {
            background-color:white;
            spacing: 0px;
            border-width: 0px 2px 2px 2px;
            border-style: solid;
            border-color: #E9EDF1;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            margin: 0px;
        }

        QToolBar::separator {
            background-color: #DBDBDB;
            width: 1px;
            margin: 8px;
        }
        """)
        # 使用对象名称设置样式
        

        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        # 保存工具栏引用，以便在resizeEvent中使用
        self.toolbar = toolbar
        # ---------------------------------------------------------------

        # 添加自定义长度的spacer到最左侧
        left_spacer = QWidget()
        left_spacer.setFixedWidth(10)  # 自定义宽度为20px
        toolbar.addWidget(left_spacer)
        
        # Default按钮
        self.default_btn = QPushButton("Default", self)
        self.default_btn.setCheckable(True)
        self.default_btn.setChecked(False)  # 初始不选中
        self.default_btn.setEnabled(False)  # 刚载入GUI时无法选中
        self.default_btn.setStyleSheet(qss_save_location_button)
        self.default_btn.setCursor(QCursor(Qt.PointingHandCursor))
        toolbar.addWidget(self.default_btn)
        
        # Folder按钮
        self.folder_btn = QPushButton("Folder", self)
        self.folder_btn.setCheckable(True)
        self.folder_btn.setStyleSheet(qss_save_location_button)
        self.folder_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.folder_btn.setEnabled(False)  # 初始不可用，无音频时
        toolbar.addWidget(self.folder_btn)
        
        # File按钮
        self.file_btn = QPushButton("File", self)
        self.file_btn.setCheckable(True)
        self.file_btn.setStyleSheet(qss_save_location_button)
        self.file_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.file_btn.setEnabled(False)  # 初始不可用，无音频时
        toolbar.addWidget(self.file_btn)
                
        toolbar.addSeparator()
        
        # 保存按钮
        self.save_btn = QPushButton("Save", self)
        self.save_btn.setIcon(QIcon(get_resource_path('resources/icons/save.svg')))
        self.save_btn.setStatusTip("Save params to the selected location")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 13px; 
                text-align: center; 
                padding: 8px 12px; 
                margin: 0;
            }
            QPushButton:disabled {
                color: #CCCCCC;
            }
        """)
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_btn.clicked.connect(self.saveParams)
        toolbar.addWidget(self.save_btn)
        
        # Reset按钮
        self.reset_svg_btn = QPushButton("Reset", self)
        self.reset_svg_btn.setIcon(QIcon(get_resource_path('resources/icons/reset.svg')))
        self.reset_svg_btn.setStatusTip("Reset to params that has been saved")
        self.reset_svg_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 13px; 
                text-align: center; 
                padding: 8px 12px; 
                margin: 0;
            }
            QPushButton:disabled {
                color: #CCCCCC;
            }
        """)
        self.reset_svg_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_svg_btn.clicked.connect(self.resetParams)
        toolbar.addWidget(self.reset_svg_btn)

        
        # Backward按钮
        self.backward_btn = QPushButton("Backward", self)
        self.backward_btn.setIcon(QIcon(get_resource_path('resources/icons/backward.svg')))
        self.backward_btn.setStatusTip("Load previous params")
        self.backward_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 13px; 
                text-align: center; 
                padding: 8px 12px; 
                margin: 0;
            }
            QPushButton:disabled {
                color: #CCCCCC;
            }
        """)
        self.backward_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.backward_btn.clicked.connect(self.loadPreviousParams)
        toolbar.addWidget(self.backward_btn)
        
        # Forward按钮
        self.forward_btn = QPushButton("Forward", self)
        self.forward_btn.setIcon(QIcon(get_resource_path('resources/icons/forward.svg')))
        self.forward_btn.setStatusTip("Load next params")
        self.forward_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 13px; 
                text-align: center; 
                padding: 8px 12px; 
                margin: 0;
            }
            QPushButton:disabled {
                color: #CCCCCC;
            }
        """)
        self.forward_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.forward_btn.clicked.connect(self.loadNextParams)
        toolbar.addWidget(self.forward_btn)
        
        # 添加伸缩空间，将参数索引标签推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # 添加VAD切换按钮
        self.vad_btn = QPushButton("VAD", self)
        self.vad_btn.setCheckable(True)
        self.vad_btn.setChecked(False)  # 初始状态：未选中
        self.vad_btn.setStyleSheet(qss_button_small_black)
        self.vad_btn.setFixedHeight(25)  # 固定高度，宽度自适应
        self.vad_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 宽度自适应，高度固定
        self.vad_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # 连接按钮点击事件
        self.vad_btn.clicked.connect(self.onVadButtonClicked)
        toolbar.addWidget(self.vad_btn)
        
        # 添加print输出显示label
        self.print_label = QLabel(self)
        self.print_label.setText("Print output: ")
        self.print_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 12px;
                border: 1px solid #E9EDF1;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: #F8F9FA;
                max-width: 300px;
            }
        """)
        self.print_label.setToolTip("显示最近的print输出")
        # 设置文本截断方式
        self.print_label.setMaximumWidth(300)
        self.print_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.print_label.setTextFormat(Qt.PlainText)
        toolbar.addWidget(self.print_label)
        
        # 合并参数图标和索引标签为一个按钮
        self.params_btn = QPushButton(self)
        self.params_btn.setIcon(QIcon(get_resource_path('resources/icons/parameters.svg')))
        self.params_btn.setText("0/0")
        self.params_btn.setFixedHeight(24)  # 固定高度
        self.params_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 12px;
                text-align: left;
                padding: 0px 10px;
            }
            QPushButton:disabled {
                color: #CCCCCC;
            }
        """)
        self.params_btn.setCursor(QCursor(Qt.ArrowCursor))  # 鼠标指针为箭头，不是手形
        toolbar.addWidget(self.params_btn)
        
        # 添加自定义长度的spacer到最右侧
        right_spacer = QWidget()
        right_spacer.setFixedWidth(8)  # 自定义宽度为20px，与左侧保持一致
        toolbar.addWidget(right_spacer)
        
        # ---------------------------------------------------------------
        # 为toolbar按钮添加提示框功能
        # ---------------------------------------------------------------
        
        # 通用提示框样式
        self.toolbar_tooltip_style = """
            QLabel {
                background-color: #FFFFE1;
                color: #000000;
                padding: 8px 12px;
                border: 1px solid #D4D4D4;
                border-radius: 3px;
                font-size: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        """
        
        # 通用提示框创建函数
        def create_toolbar_tooltip(text):
            tooltip = QLabel(self)
            tooltip.setText(text)
            tooltip.setStyleSheet(self.toolbar_tooltip_style)
            tooltip.setAlignment(Qt.AlignLeft)
            tooltip.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
            tooltip.hide()
            return tooltip
        
        # 通用hover事件处理函数
        def create_toolbar_hover_handlers(btn, tooltip):
            def show_tooltip(event):
                # 显示提示框
                btn_pos = btn.mapToGlobal(QPoint(0, 0))
                tooltip.adjustSize()
                # 位置：按钮右下角，提示框左上角与按钮右下角完全对齐
                x = btn_pos.x() + btn.width()
                y = btn_pos.y() + btn.height()
                tooltip.move(x, y)
                tooltip.show()
                event.accept()
            
            def hide_tooltip(event):
                # 隐藏提示框
                tooltip.hide()
                event.accept()
            
            return show_tooltip, hide_tooltip
        
        # 为Default按钮添加提示框
        self.default_tooltip = create_toolbar_tooltip("Use default parameters")
        default_enter, default_leave = create_toolbar_hover_handlers(self.default_btn, self.default_tooltip)
        self.default_btn.enterEvent = default_enter
        self.default_btn.leaveEvent = default_leave
        
        # 为Folder按钮添加提示框
        self.folder_tooltip = create_toolbar_tooltip("Use folder-specific parameters")
        folder_enter, folder_leave = create_toolbar_hover_handlers(self.folder_btn, self.folder_tooltip)
        self.folder_btn.enterEvent = folder_enter
        self.folder_btn.leaveEvent = folder_leave
        
        # 为File按钮添加提示框
        self.file_tooltip = create_toolbar_tooltip("Use file-specific parameters")
        file_enter, file_leave = create_toolbar_hover_handlers(self.file_btn, self.file_tooltip)
        self.file_btn.enterEvent = file_enter
        self.file_btn.leaveEvent = file_leave
        
        # 为Save按钮添加提示框
        self.save_tooltip = create_toolbar_tooltip("Save parameters to selected location")
        save_enter, save_leave = create_toolbar_hover_handlers(self.save_btn, self.save_tooltip)
        self.save_btn.enterEvent = save_enter
        self.save_btn.leaveEvent = save_leave
        
        # 为Reset按钮添加提示框
        self.reset_tooltip = create_toolbar_tooltip("Reset parameters to saved values")
        reset_enter, reset_leave = create_toolbar_hover_handlers(self.reset_svg_btn, self.reset_tooltip)
        self.reset_svg_btn.enterEvent = reset_enter
        self.reset_svg_btn.leaveEvent = reset_leave
        
        # 为Backward按钮添加提示框
        self.backward_tooltip = create_toolbar_tooltip("Load previous parameters")
        backward_enter, backward_leave = create_toolbar_hover_handlers(self.backward_btn, self.backward_tooltip)
        self.backward_btn.enterEvent = backward_enter
        self.backward_btn.leaveEvent = backward_leave
        
        # 为Forward按钮添加提示框
        self.forward_tooltip = create_toolbar_tooltip("Load next parameters")
        forward_enter, forward_leave = create_toolbar_hover_handlers(self.forward_btn, self.forward_tooltip)
        self.forward_btn.enterEvent = forward_enter
        self.forward_btn.leaveEvent = forward_leave
        
        # 为params_btn添加提示框
        self.params_tooltip = create_toolbar_tooltip("Parameters index")
        params_enter, params_leave = create_toolbar_hover_handlers(self.params_btn, self.params_tooltip)
        self.params_btn.enterEvent = params_enter
        self.params_btn.leaveEvent = params_leave
        
        # 为VAD按钮添加提示框
        self.vad_tooltip = create_toolbar_tooltip("Toggle VAD mode")
        vad_enter, vad_leave = create_toolbar_hover_handlers(self.vad_btn, self.vad_tooltip)
        self.vad_btn.enterEvent = vad_enter
        self.vad_btn.leaveEvent = vad_leave
        
        # 初始化输出流，将print语句重定向到GUI
        def update_print_label(text):
            # 更新print_label的文本，仅显示最后一行
            self.print_label.setText(f"{text}")
        
        # 创建输出流实例
        self.console_output = ConsoleOutput(update_print_label)
        # 保存原始stdout
        self.original_stdout = sys.stdout
        # 重定向stdout到自定义输出流
        sys.stdout = self.console_output
        
        # 测试print输出功能
        # print("Praditor started successfully!")
        
        # ---------------------
        # TOOLBAR



        # 移除可能冲突的CSS圆角设置，因为我们使用paintEvent绘制圆角
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent; 
            }

        """)
        
        # 调整主窗口的边距，确保工具栏与标题栏完全对齐
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 确保工具栏与标题栏的视觉效果完全一致
        # 由于QToolBar默认会自动填充主窗口宽度，无需额外设置宽度
        # 只需确保边距和圆角半径一致即可


        # 初始化参数txt
        # 检查是否存在default mode
        # if not os.path.exists("params.txt"):
        #     with open("params.txt", 'w') as txt_file:
        #         txt_file.write(f"{self.MySliders.getParams()}")
        # else:
        # 初始化参数文件，使用当前文件所在目录
        default_params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params.txt")
        if not os.path.exists(default_params_path):
            default_params_path = get_resource_path("src/app/params.txt")
            if not os.path.exists(default_params_path):
                with open(default_params_path, 'w') as txt_file:
                    txt_file.write(f"{self.MySliders.getParams()}")
        else:  # 存在default mode
            try:
                with open(default_params_path, "r") as txt_file:
                    self.MySliders.resetParams(eval(txt_file.read()))
            except KeyError:
                with open(default_params_path, 'w') as txt_file:
                    txt_file.write(f"{self.MySliders.getParams()}")


        self.MySliders.anySliderValueChanged.connect(self.checkIfParamsExist)
        
        # 模式按钮点击事件连接
        self.default_btn.clicked.connect(lambda: self.onModeButtonClicked(self.default_btn))
        self.folder_btn.clicked.connect(lambda: self.onModeButtonClicked(self.folder_btn))
        self.file_btn.clicked.connect(lambda: self.onModeButtonClicked(self.file_btn))
        
        # 初始化时检查一次参数匹配，确保刚载入GUI时也能显示下划线
        self.checkIfParamsExist()
        
        # 初始化时更新save和reset按钮状态
        self.updateToolbarButtonsState()
        
    def onVadButtonClicked(self):
        """处理VAD按钮点击事件"""
        self.toggleVadMode(self.vad_btn.isChecked())
    
    def toggleVadMode(self, is_vad_enabled):
        """切换VAD模式，调整UI布局"""
        if is_vad_enabled:
            # 设置Onset和Offset按钮为选中状态且不可取消选中
            self.title_bar.onset_btn.setChecked(False)
            self.title_bar.offset_btn.setChecked(False)
            self.title_bar.onset_btn.setEnabled(False)
            self.title_bar.offset_btn.setEnabled(False)
            # 确保按钮可见
            self.title_bar.onset_btn.setVisible(True)
            self.title_bar.offset_btn.setVisible(True)
            
            # 隐藏所有Offset sliders
            offset_sliders = [
                self.MySliders.amp_slider_offset,
                self.MySliders.cutoff0_slider_offset,
                self.MySliders.cutoff1_slider_offset,
                self.MySliders.numValid_slider_offset,
                self.MySliders.win_size_slider_offset,
                self.MySliders.ratio_slider_offset,
                self.MySliders.penalty_slider_offset,
                self.MySliders.ref_len_slider_offset,
                self.MySliders.eps_ratio_slider_offset
            ]
            for slider in offset_sliders:
                slider.setVisible(False)
            
            # 隐藏不需要的Onset sliders
            onset_sliders_to_hide = [
                self.MySliders.penalty_slider_onset,
                self.MySliders.ref_len_slider_onset,
                self.MySliders.win_size_slider_onset,
                self.MySliders.ratio_slider_onset
            ]
            for slider in onset_sliders_to_hide:
                slider.setVisible(False)
            
            # 隐藏对应的名称标签
            labels_to_hide = [
                self.MySliders.name_labels["Penalty"],
                self.MySliders.name_labels["RefLen"],
                self.MySliders.name_labels["KernelFrm%"],
                self.MySliders.name_labels["KernelSize"]
            ]
            for label in labels_to_hide:
                label.setVisible(False)
            
            # 将Onset滑块颜色改为灰色
            gray_color = "#999999"
            onset_sliders_to_keep = [
                self.MySliders.amp_slider_onset,
                self.MySliders.cutoff0_slider_onset,
                self.MySliders.cutoff1_slider_onset,
                self.MySliders.numValid_slider_onset,
                self.MySliders.eps_ratio_slider_onset
            ]
            for slider in onset_sliders_to_keep:
                slider.param_slider.setStyleSheet(qss_slider_with_color(gray_color))
            
            # 更新布局，让Onset sliders扩展到原来Offset sliders的位置
            layout = self.MySliders.layout()
            # 设置Onset sliders列占满所有空间
            layout.setColumnStretch(1, 1)  # Onset列占满剩余空间
            layout.setColumnStretch(2, 0)  # 移除Offset列的拉伸
            layout.setColumnMinimumWidth(2, 0)  # 移除Offset列的最小宽度限制
        else:
            # 恢复Onset和Offset按钮的可用状态
            self.title_bar.onset_btn.setEnabled(True)
            self.title_bar.offset_btn.setEnabled(True)
            # 确保按钮可见
            self.title_bar.onset_btn.setVisible(True)
            self.title_bar.offset_btn.setVisible(True)
            
            # 显示所有Offset sliders
            offset_sliders = [
                self.MySliders.amp_slider_offset,
                self.MySliders.cutoff0_slider_offset,
                self.MySliders.cutoff1_slider_offset,
                self.MySliders.numValid_slider_offset,
                self.MySliders.win_size_slider_offset,
                self.MySliders.ratio_slider_offset,
                self.MySliders.penalty_slider_offset,
                self.MySliders.ref_len_slider_offset,
                self.MySliders.eps_ratio_slider_offset
            ]
            for slider in offset_sliders:
                slider.setVisible(True)
            
            # 显示所有Onset sliders
            onset_sliders_to_show = [
                self.MySliders.penalty_slider_onset,
                self.MySliders.ref_len_slider_onset,
                self.MySliders.win_size_slider_onset,
                self.MySliders.ratio_slider_onset
            ]
            for slider in onset_sliders_to_show:
                slider.setVisible(True)
            
            # 显示对应的名称标签
            labels_to_show = [
                self.MySliders.name_labels["Penalty"],
                self.MySliders.name_labels["RefLen"],
                self.MySliders.name_labels["KernelFrm%"],
                self.MySliders.name_labels["KernelSize"]
            ]
            for label in labels_to_show:
                label.setVisible(True)
            
            # 恢复Onset滑块颜色
            onset_color = "#1991D3"
            onset_sliders = [
                self.MySliders.amp_slider_onset,
                self.MySliders.cutoff0_slider_onset,
                self.MySliders.cutoff1_slider_onset,
                self.MySliders.numValid_slider_onset,
                self.MySliders.win_size_slider_onset,
                self.MySliders.ratio_slider_onset,
                self.MySliders.penalty_slider_onset,
                self.MySliders.ref_len_slider_onset,
                self.MySliders.eps_ratio_slider_onset
            ]
            for slider in onset_sliders:
                slider.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
            
            # 恢复原始布局
            layout = self.MySliders.layout()
            layout.setColumnStretch(1, 1)  # 恢复Onset列拉伸因子
            layout.setColumnStretch(2, 1)  # 恢复Offset列拉伸因子
            layout.setColumnMinimumWidth(2, 200)  # 恢复Offset列最小宽度限制
        
        # 切换模式后更新参数索引标签，确保显示当前模式的参数
        self.updateParamIndexLabel()
        
        # 按照File→Folder→Default优先级加载参数
        self.showParams()
        
        # 检查参数文件是否存在，更新按钮状态
        self.checkIfParamsExist()

        # 切换模式后，不选中任何按钮
        self.default_btn.setChecked(False)
        self.folder_btn.setChecked(False)
        self.file_btn.setChecked(False)
        
        # 重新读取音频结果，根据当前模式选择不同的结果文件
        if hasattr(self, 'file_path') and self.file_path:
            self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=is_vad_enabled)
            self.showXsetNum(is_test=False)



    def keyPressEvent(self, event):

        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.playSound()
        else:
            if event.key() == Qt.Key_F5:
                self.playSound()

        super().keyPressEvent(event)

    def playSound(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.stop()  # 如果正在播放则暂停
            print("stop")
        else:
            self.player.setSource(QUrl.fromLocalFile(self.file_path))
            self.player.play()    # 开始/恢复播放
            print("play")



    def readXset(self):
        if self.vad_btn.isChecked():
            self.AudioViewer.tg_dict_tp = get_frm_intervals_from_textgrid(self.file_path)
        else:
            self.AudioViewer.tg_dict_tp = get_frm_points_from_textgrid(self.file_path)
        
        if not self.AudioViewer.tg_dict_tp or self.AudioViewer.tg_dict_tp == {"onset": [], "offset": []}:
            popup_window = QMessageBox()
            # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
            popup_window.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.png')))
            popup_window.setText(f"No X-set found in {self.file_path}")
            popup_window.exec()
            return


        self.AudioViewer.updateXset(self.AudioViewer.tg_dict_tp)
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["onset"], isVisible=not self.run_onset.isChecked())
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["offset"], isVisible=not self.run_offset.isChecked())


    def clearXset(self):
        # self.AudioViewer.tg_dict_tp = get_frm_points_from_textgrid(self.file_path)

        if not self.run_onset.isChecked():
            self.AudioViewer.removeXset(self.AudioViewer.tg_dict_tp["onset"])
        if not self.run_offset.isChecked():
            self.AudioViewer.removeXset(self.AudioViewer.tg_dict_tp["offset"])
        self.AudioViewer.tg_dict_tp = {}



    def turnOnset(self):
        if not self.run_onset.isChecked():
            onset_color = "#AFAFAF"
            slider_status = True
        else:
            slider_status = False
            onset_color = "#1991D3"

        self.MySliders.amp_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.cutoff0_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.cutoff1_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.numValid_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.win_size_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.ratio_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.penalty_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.ref_len_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.eps_ratio_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))

        self.MySliders.amp_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.cutoff0_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.cutoff1_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.numValid_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.win_size_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.ratio_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.penalty_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.ref_len_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.eps_ratio_slider_onset.param_slider.setDisabled(slider_status)

        self.AudioViewer.showOnset = not slider_status
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["onset"], isVisible=self.AudioViewer.showOnset)


    def turnOffset(self):
        if not self.run_offset.isChecked():
            offset_color = "#AFAFAF"
            slider_status = True
        else:
            offset_color = "#2AD25E"
            slider_status = False

        self.MySliders.amp_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.cutoff0_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.cutoff1_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.numValid_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.win_size_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.ratio_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.penalty_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.ref_len_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
        self.MySliders.eps_ratio_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))

        self.MySliders.amp_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.cutoff0_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.cutoff1_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.numValid_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.win_size_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.ratio_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.penalty_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.ref_len_slider_offset.param_slider.setDisabled(slider_status)
        self.MySliders.eps_ratio_slider_offset.param_slider.setDisabled(slider_status)

        self.AudioViewer.showOffset = not slider_status
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["offset"], isVisible=self.AudioViewer.showOffset)




    def resetParams(self):
        # 由于按钮可以同时被选中，我们需要确定优先读取哪个位置的参数
        # 优先级：File > Folder > Default
        txt_file_path = None
        
        # 检查是否处于VAD模式
        is_vad_mode = self.vad_btn.isChecked()
        file_suffix = "_vad" if is_vad_mode else ""
        
        if self.file_btn.isChecked():
            # File模式：从file同名的txt文件读取
            txt_file_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
        elif self.folder_btn.isChecked():
            # Folder模式：从当前文件夹的同名txt文件读取
            folder_path = os.path.dirname(self.file_path)
            folder_name = os.path.basename(folder_path)
            txt_file_path = os.path.join(folder_path, f"params{file_suffix}.txt")
        else:  # Default模式
            # 从应用程序所在目录读取
            txt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"params{file_suffix}.txt")
            if not os.path.exists(txt_file_path):
                txt_file_path = get_resource_path(f"src/app/params{file_suffix}.txt")

        try:
            with open(txt_file_path, 'r') as txt_file:
                self.MySliders.resetParams(eval(txt_file.read()))
            print(f"Params TXT file read from: {txt_file_path}")

        except FileNotFoundError:
            # 切换到Default模式
            self.default_btn.setChecked(True)
            print("Go back to Default mode")
            self.showParams()


    def saveParams(self):
        # 检查每个按钮的状态，如果被选中就保存到相应位置
        if self.default_btn.isChecked():
            # Default模式：保存到应用程序所在位置
            self.saveParamsToExeLocation()
        if self.folder_btn.isChecked():
            # Folder模式：保存到当前文件夹，文件名与文件夹同名
            self.saveParamsWithFolderName()
        if self.file_btn.isChecked():
            # File模式：保存到file同名
            self.saveParamsWithFileName()
        
        # 保存参数后检查是否与任何模式匹配，更新下划线
        self.checkIfParamsExist()
        
        # 更新工具栏按钮状态，确保Reset按钮在参数文件保存后显示为可用
        self.updateToolbarButtonsState()


    def checkIfParamsExist(self):
        current_params = str(self.MySliders.getParams())
        # current_params_dict = self.MySliders.getParams()
        
        # 检查是否处于VAD模式
        is_vad_mode = self.vad_btn.isChecked()
        file_suffix = "_vad" if is_vad_mode else ""
        
        # 检查Default模式
        default_params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"params{file_suffix}.txt")
        if not os.path.exists(default_params_path):
            default_params_path = get_resource_path(f"src/app/params{file_suffix}.txt")
        
        default_params_match = False
        if os.path.exists(default_params_path):
            try:
                with open(default_params_path, 'r') as txt_file:
                    default_params = str(eval(txt_file.read()))
                    default_params_match = (current_params == default_params)
            except:
                pass
        
        # 设置default_btn的file_exists和param_matched属性
        self.default_btn.setProperty("file_exists", os.path.exists(default_params_path))
        self.default_btn.setProperty("param_matched", default_params_match)
        self.default_btn.style().polish(self.default_btn)  # 刷新样式
        
        # 检查Folder模式
        folder_params_exists = False
        folder_params_match = False
        if self.file_path:
            folder_path = os.path.dirname(self.file_path)
            folder_params_path = os.path.join(folder_path, f"params{file_suffix}.txt")
            
            if os.path.exists(folder_params_path):
                folder_params_exists = True
                try:
                    with open(folder_params_path, 'r') as txt_file:
                        folder_params = str(eval(txt_file.read()))
                        folder_params_match = (current_params == folder_params)
                except:
                    pass
        
        # 设置folder_btn的file_exists和param_matched属性
        self.folder_btn.setProperty("file_exists", folder_params_exists)
        self.folder_btn.setProperty("param_matched", folder_params_match)
        self.folder_btn.style().polish(self.folder_btn)  # 刷新样式
        
        # 检查File模式
        file_params_exists = False
        file_params_match = False
        if self.file_path:
            file_params_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
            
            if os.path.exists(file_params_path):
                file_params_exists = True
                try:
                    with open(file_params_path, 'r') as txt_file:
                        file_params = str(eval(txt_file.read()))
                        file_params_match = (current_params == file_params)
                except:
                    pass
        
        # 设置file_btn的file_exists和param_matched属性
        self.file_btn.setProperty("file_exists", file_params_exists)
        self.file_btn.setProperty("param_matched", file_params_match)
        self.file_btn.style().polish(self.file_btn)  # 刷新样式

    def showParams(self):
        # 简化版showParams，处理多种参数模式
        if self.file_path is None:
            return
        
        # 检查是否处于VAD模式
        is_vad_mode = self.vad_btn.isChecked()
        file_suffix = "_vad" if is_vad_mode else ""
        
        # 默认使用文件同名参数
        txt_file_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
        params_to_use = None
        
        # 检查文件同名参数是否存在
        if os.path.exists(txt_file_path):
            with open(txt_file_path, "r") as txt_file:
                params_to_use = txt_file.read()
        else:
            # 检查folder模式的params.txt是否存在
            folder_path = os.path.dirname(self.file_path)
            folder_params_path = os.path.join(folder_path, f"params{file_suffix}.txt")
            
            if os.path.exists(folder_params_path):
                with open(folder_params_path, "r") as txt_file:
                    params_to_use = txt_file.read()
            else:
                # 最后使用默认的params.txt
                default_params_path = os.path.join(os.getcwd(), f"params{file_suffix}.txt")
                if not os.path.exists(default_params_path):
                    default_params_path = get_resource_path(f"src/app/params{file_suffix}.txt")
                    
                with open(default_params_path, "r") as default_txt_file:
                    params_to_use = default_txt_file.read()
        
        # 应用参数
        if params_to_use:
            self.MySliders.resetParams(eval(params_to_use))



    def lastParams(self):
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.vad_btn.isChecked() else "default"

        if len(self.param_sets[current_mode]) == 2:
            self.MySliders.resetParams(self.param_sets[current_mode][-2])
            self.param_sets[current_mode].reverse()


    def openFileDialog(self):

        # 设置过滤器，仅显示音频文件
        audio_filters = "Audio Files (*.mp3 *.wav *.ogg *.aac *.flac *.amr *.wma *.aiff)"
        # 弹出文件选择对话框
        file_name, _ = QFileDialog.getOpenFileName(None, "Select Audio File", "", audio_filters)

        if file_name:
            file_name = os.path.normpath(file_name)
            folder_path = os.path.dirname(file_name)

            self.file_paths = [os.path.normpath(os.path.join(folder_path, fpath)) for fpath in os.listdir(folder_path) if isAudioFile(fpath)]

            self.which_one = self.file_paths.index(file_name)
            self.file_path = self.file_paths[self.which_one]
            print(f"Selected file: {self.file_path}")
            self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.vad_btn.isChecked())
            
            # 启用所有模式按钮
            self.default_btn.setEnabled(True)
            self.folder_btn.setEnabled(True)
            self.file_btn.setEnabled(True)
            
            # 三个按钮都不选中
            self.default_btn.setChecked(False)
            self.folder_btn.setChecked(False)
            self.file_btn.setChecked(False)
            
            # 更新save和reset按钮的可用性
            self.updateToolbarButtonsState()
            self.showParams()
            # 检查参数匹配，更新下划线
            self.checkIfParamsExist()

            dir_name = os.path.basename(os.path.dirname(self.file_path))
            base_name = os.path.basename(self.file_path)
            self.setWindowTitle(f"Praditor - {dir_name}/{base_name} ({self.which_one+1}/{len(self.file_paths)})")

            self.showXsetNum(is_test=False)

        else:
            print("Empty folder")


    def showXsetNum(self, is_test=False):
        """根据当前tg_dict_tp的内容，更新onset/offset按钮的显示文本"""
        
        # 确保onset和offset键存在，不存在则初始化为空列表
        if 'onset' not in self.AudioViewer.tg_dict_tp:
            self.AudioViewer.tg_dict_tp['onset'] = []
        if 'offset' not in self.AudioViewer.tg_dict_tp:
            self.AudioViewer.tg_dict_tp['offset'] = []
        
        if not self.AudioViewer.tg_dict_tp['onset']:
            self.run_onset.setText("Onset")
        else:
            if is_test:
                self.run_onset.setText(f"Onset: {len(self.AudioViewer.tg_dict_tp['onset'])} ?")
            else:
                self.run_onset.setText(f"Onset: {len(self.AudioViewer.tg_dict_tp['onset'])}")

        if not self.AudioViewer.tg_dict_tp['offset']:
            self.run_offset.setText("Offset")
        else:
            if is_test:
                self.run_offset.setText(f"Offset: {len(self.AudioViewer.tg_dict_tp['offset'])} ?")
            else:
                self.run_offset.setText(f"Offset: {len(self.AudioViewer.tg_dict_tp['offset'])}")

    def browseInstruction(self):
        # 使用webbrowser模块打开默认浏览器并导航到指定网址
        webbrowser.open('https://github.com/Paradeluxe/Praditor?tab=readme-ov-file#how-to-use-praditor')
    
    def stopDetection(self):
        """停止当前正在运行的检测任务"""

        # 设置全局停止标志
        from src.core import detection
        detection.stop_flag = True    

        # 终止所有当前运行的线程
        for thread in self.current_runnables.copy():
            try:
                thread.stop()  # 使用安全停止方法
            except RuntimeError:
                # 忽略已删除的C++对象
                pass
        # 清空列表
        self.current_runnables.clear()

            
        # 清空检测结果
        self.detection_results = {"onset": [], "offset": []}
        self.detection_count = 0
        self.total_detections = 0
        
        # 退出run-all模式
        self.is_running_all = False

        # 启用所有按钮
        self.setButtonsEnabled(True)

        # detection.stop_flag = False
    

    
    def on_detect_finished(self, onset_results, offset_results):
        """检测任务完成后的处理"""
        self.detection_results["onset"] = onset_results
        self.detection_results["offset"] = offset_results
        self.detection_count += 1
        
        # 检查是否所有检测任务都已完成
        if self.detection_count == self.total_detections:
            # 处理检测结果
            self.process_detection_results()
        
            # 清空线程列表，因为所有线程都已完成
            self.current_runnables.clear()
    
    def runAllAudioFiles(self):
        """Run Praditor on all audio files sequentially, displaying one audio after current detection finishes"""
        if not hasattr(self, 'file_paths') or len(self.file_paths) == 0:
            return
        
        # 禁用除最小化、最大化、关闭、停止以外的所有按钮
        self.setButtonsEnabled(False)
        
        # 设置run-all标志和起始索引
        self.is_running_all = True
        self.run_all_current_index = 0  # 从第一个音频开始
        
        # 显示第一个音频
        self.which_one = self.run_all_current_index
        self.file_path = self.file_paths[self.which_one]
        dir_name = os.path.basename(os.path.dirname(self.file_path))
        base_name = os.path.basename(self.file_path)
        self.setWindowTitle(f"Praditor - {dir_name}/{base_name} ({self.which_one+1}/{len(self.file_paths)})")
        self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.vad_btn.isChecked())
        self.showXsetNum(is_test=False)
        
        # 启动检测
        self.execPraditor(is_test=False)

        self.updateToolbarButtonsState()



    
    def on_run_signal(self):
        """处理run_signal信号，在执行检测前设置stop_flag = False"""
        from src.core import detection
        detection.stop_flag = False
        self.execPraditor(is_test=False)

        self.updateToolbarButtonsState()

    
    def on_test_signal(self):
        """处理test_signal信号，在执行检测前设置stop_flag = False"""
        from src.core import detection
        detection.stop_flag = False
        self.execPraditor(is_test=True)

        self.updateToolbarButtonsState()

    
    def process_detection_results(self):
        # 处理所有检测结果
        onsets = self.detection_results["onset"]
        offsets = self.detection_results["offset"]
        is_vad_mode = self.current_detection_params["is_vad_mode"]
        is_test = self.current_detection_params["is_test"]
        
        if is_vad_mode:
            ###########################
            # 如果头尾是从有声直接开始/结束，则为其赋值为0/音频长度
            ###########################
            if onsets and offsets:  # 确保列表非空
                if onsets[0] >= offsets[0]:
                    onsets = [0.0] + onsets
    
                if offsets[-1] <= onsets[-1]:
                    offsets.append(self.AudioViewer.audio_obj.duration_seconds)
    
                ##########################
                # Select the one offset that is closest to onset and earlier than onset
                ##########################
    
                new_onsets = []
                new_offsets = []
                for i, onset in enumerate(onsets):
                    if i == 0:
                        new_offsets.append(offsets[-1])
                        new_onsets.append(onset)
                    else:
                        try:
                            new_offsets.append(max([offset for offset in offsets if onsets[i-1] < offset < onset]))
                            new_onsets.append(onset)
                        except ValueError:
                            pass
    
                onsets = sorted(new_onsets)
                offsets = sorted(new_offsets)
    
        if is_test:
            # 测试模式：直接显示结果，不保存
            self.AudioViewer.tg_dict_tp["onset"] = onsets
            self.AudioViewer.tg_dict_tp["offset"] = offsets
            self.showXsetNum(is_test=is_test)
        else:  # default mode
            # 保存结果
            self.AudioViewer.tg_dict_tp["onset"] = onsets
            self.AudioViewer.tg_dict_tp["offset"] = offsets
    
            create_textgrid_with_time_point(audio_file_path=self.file_path, is_vad_mode=is_vad_mode, onsets=self.AudioViewer.tg_dict_tp["onset"], offsets=self.AudioViewer.tg_dict_tp["offset"])
            
            self.readXset()
            self.showXsetNum(is_test=is_test)
            self.update_current_param()
        
        # 检查是否处于run-all模式
        if self.is_running_all:
            # 递增当前索引
            self.run_all_current_index += 1
            # from src.core import detection
            # print("running all?", not detection.stop_flag)
            # 检查是否还有更多文件要处理
            if self.run_all_current_index < len(self.file_paths):# and not detection.stop_flag:
                # 更新当前索引到which_one
                self.which_one = self.run_all_current_index
                # 更新当前文件路径
                self.file_path = self.file_paths[self.which_one]
                # 更新窗口标题
                dir_name = os.path.basename(os.path.dirname(self.file_path))
                base_name = os.path.basename(self.file_path)
                self.setWindowTitle(f"Praditor - {dir_name}/{base_name} ({self.which_one+1}/{len(self.file_paths)})")
                # 读取新的音频文件
                self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.vad_btn.isChecked())
                # 显示当前音频的xset数量
                self.showXsetNum(is_test=False)
                # 启动下一个音频的检测
                self.execPraditor(is_test=False)
            else:
                # 所有文件处理完成，退出run-all模式
                self.is_running_all = False
                
                # 确保所有线程都已终止
                if self.current_runnables:
                    for thread in self.current_runnables.copy():
                        try:
                            thread.stop()  # 使用安全停止方法
                        except RuntimeError:
                            # 忽略已删除的C++对象
                            pass
                    # 清空列表
                    self.current_runnables.clear()
                
                # 启用所有按钮
                self.setButtonsEnabled(True)
                
                # 发射run完成信号
                self.run_current_done.emit()
        else:
            # 单个文件处理完成
            # 启用所有按钮
            self.setButtonsEnabled(True)
            
            # 发射run完成信号
            self.run_current_done.emit()
        


    def execPraditor(self, is_test: bool):

        from src.core import detection
        detection.stop_flag = False

        # 仅在非run-all模式下禁用按钮，run-all模式下已经在runAllAudioFiles方法中禁用了
        if not self.is_running_all:
            # 禁用除最小化、最大化、关闭、停止以外的所有按钮
            self.setButtonsEnabled(False)

        # 检测当前模式，直接使用detectPraditor函数
        is_vad_mode = self.vad_btn.isChecked()
        
        if is_vad_mode:
            if float(self.MySliders.cutoff1_slider_onset.value_edit.text()) > float(self.AudioViewer.audio_samplerate)/2:

                popup_window = QMessageBox()
                # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
                popup_window.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.png')))
                popup_window.setText(f"LowPass exceeds the Nyquist frequency boundary {float(self.AudioViewer.audio_samplerate)/2:.0f}")
                popup_window.exec()

                return

        else: # default mode
            if float(self.MySliders.cutoff1_slider_onset.value_edit.text()) > float(self.AudioViewer.audio_samplerate)/2 or \
                float(self.MySliders.cutoff1_slider_offset.value_edit.text()) > float(self.AudioViewer.audio_samplerate)/2:

                popup_window = QMessageBox()
                # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
                popup_window.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.png')))
                popup_window.setText(f"LowPass exceeds the Nyquist frequency boundary {float(self.AudioViewer.audio_samplerate)/2:.0f}")
                popup_window.exec()

                return

        # 重置检测结果
        self.detection_results = {"onset": [], "offset": []}
        self.detection_count = 0
        self.total_detections = 0
        
        # 保存当前检测参数，供后续处理使用
        self.current_detection_params = {
            "is_vad_mode": is_vad_mode,
            "is_test": is_test
        }
        
        # 获取检测参数
        params = self.MySliders.getParams()

        if self.run_onset.isChecked():
            params["onset"] = {}
        else:
            try:
                self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["onset"])
            except KeyError:
                pass
        
        if self.run_offset.isChecked():
            params["offset"] = {}
        else:
            try:
                self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["offset"])
            except KeyError:
                pass

        xset_thread = DetectPraditorThread(params, self.AudioViewer.audio_obj, mode="vad" if is_vad_mode else "general")

        xset_thread.finished.connect(lambda thread=xset_thread: self.current_runnables.remove(thread) if thread in self.current_runnables else None)
        xset_thread.finished.connect(self.on_detect_finished)
        xset_thread.finished.connect(xset_thread.deleteLater)

        xset_thread.start()
        self.total_detections += 1
        self.current_runnables.append(xset_thread)

        
        # 如果没有需要执行的检测任务，直接处理结果
        if self.total_detections == 0:
            self.process_detection_results()
    
    def update_current_param(self):
        current_params = self.MySliders.getParams()
        
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.vad_btn.isChecked() else "default"
        
        # 如果当前参数已经在列表中，移除它
        if current_params in self.param_sets[current_mode]:
            self.param_sets[current_mode].remove(current_params)
        
        # 添加到列表末尾
        self.param_sets[current_mode].append(current_params)
        
        # 限制最多保存10套参数
        if len(self.param_sets[current_mode]) > 10:
            self.param_sets[current_mode] = self.param_sets[current_mode][-10:]
        
        # 更新当前索引为最后一个
        self.current_param_index[current_mode] = len(self.param_sets[current_mode]) - 1
        self.updateParamIndexLabel()
        # 更新forward和backward按钮状态
        self.updateToolbarButtonsState()
    

    def loadPreviousParams(self):
        """加载前一套参数"""
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.vad_btn.isChecked() else "default"
        if self.param_sets[current_mode] and self.current_param_index[current_mode] > 0:
            self.current_param_index[current_mode] -= 1
            self.MySliders.resetParams(self.param_sets[current_mode][self.current_param_index[current_mode]])
            self.updateParamIndexLabel()
            # print(f"Loaded previous params (index: {self.current_param_index[current_mode]})")
    

    def loadNextParams(self):
        """加载后一套参数"""
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.vad_btn.isChecked() else "default"
        if self.param_sets[current_mode] and self.current_param_index[current_mode] < len(self.param_sets[current_mode]) - 1:
            self.current_param_index[current_mode] += 1
            self.MySliders.resetParams(self.param_sets[current_mode][self.current_param_index[current_mode]])
            self.updateParamIndexLabel()
            # print(f"Loaded next params (index: {self.current_param_index[current_mode]})")
    

    def updateParamIndexLabel(self):
        """更新参数索引标签"""
        # print(self.param_sets)
        if hasattr(self, 'params_btn'):
            # 获取当前模式（默认或VAD）
            current_mode = "vad" if self.vad_btn.isChecked() else "default"
            # 获取当前模式的参数集
            param_set = self.param_sets[current_mode]
            
            if param_set:
                # 确保当前索引有效
                if self.current_param_index[current_mode] < 0:
                    self.current_param_index[current_mode] = 0
                if self.current_param_index[current_mode] >= len(param_set):
                    self.current_param_index[current_mode] = len(param_set) - 1
                
                # 当前索引从1开始显示，最多10套
                display_index = self.current_param_index[current_mode] + 1
                total_count = len(param_set)
            else:
                display_index = 0
                total_count = 0
                
            # 根据当前模式显示该模式的参数索引和总数
            self.params_btn.setText(f"{display_index}/{min(total_count, 10)}")
    

    def updateToolbarButtonsState(self):
        """根据模式按钮的选中状态和音频导入状态更新按钮的可用性和样式
        - save按钮：依赖模式按钮的选中状态
        - reset按钮：必须选中的模式存在对应的参数文件
        - forward和backward按钮：必须成功导入音频且有两套及以上的参数
        """
        # 检查是否有任何模式按钮被选中
        any_mode_selected = self.default_btn.isChecked() or self.folder_btn.isChecked() or self.file_btn.isChecked()
        
        # 检查音频是否已成功导入
        audio_imported = hasattr(self, 'file_path') and self.file_path is not None and len(self.file_path) > 0
        
        # 检查是否有两套及以上的参数
        current_mode = "vad" if self.vad_btn.isChecked() else "default"
        has_multiple_params = len(self.param_sets[current_mode]) >= 2
        
        # 检查当前选中的模式是否存在对应的参数文件
        reset_enabled = False
        if any_mode_selected:
            # 检查是否处于VAD模式
            is_vad_mode = self.vad_btn.isChecked()
            file_suffix = "_vad" if is_vad_mode else ""
            
            if self.default_btn.isChecked():
                # Default模式：检查应用程序所在目录的params文件
                default_params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"params{file_suffix}.txt")
                if not os.path.exists(default_params_path):
                    default_params_path = get_resource_path(f"src/app/params{file_suffix}.txt")
                reset_enabled = os.path.exists(default_params_path)
            elif self.folder_btn.isChecked() and audio_imported:
                # Folder模式：检查当前文件夹的params文件
                folder_path = os.path.dirname(self.file_path)
                folder_params_path = os.path.join(folder_path, f"params{file_suffix}.txt")
                reset_enabled = os.path.exists(folder_params_path)
            elif self.file_btn.isChecked() and audio_imported:
                # File模式：检查文件同名的params文件
                file_params_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
                reset_enabled = os.path.exists(file_params_path)
        
        # 更新save按钮
        self.save_btn.setEnabled(any_mode_selected)
        self.save_btn.setIcon(QIcon(get_resource_path(f'resources/icons/save{"_gray" if not any_mode_selected else ""}.svg')))
        
        # 更新reset按钮
        self.reset_svg_btn.setEnabled(reset_enabled)
        self.reset_svg_btn.setIcon(QIcon(get_resource_path(f'resources/icons/reset{"_gray" if not reset_enabled else ""}.svg')))
        
        # 更新backward按钮 - 必须音频导入成功且有两套及以上的参数
        backward_enabled = audio_imported and has_multiple_params
        # print(f"backward_enabled: {backward_enabled}")
        self.backward_btn.setEnabled(backward_enabled)
        self.backward_btn.setIcon(QIcon(get_resource_path(f'resources/icons/backward{"_gray" if not backward_enabled else ""}.svg')))

        
        # 更新forward按钮 - 必须音频导入成功且有两套及以上的参数
        forward_enabled = audio_imported and has_multiple_params
        self.forward_btn.setEnabled(forward_enabled)
        self.forward_btn.setIcon(QIcon(get_resource_path(f'resources/icons/forward{"_gray" if not forward_enabled else ""}.svg')))
    
    def _setButtonEnabled(self, button, icon_name, enabled):
        """设置按钮是否可用，并自动切换图标
        
        Args:
            button (QPushButton): 要设置的按钮
            icon_name (str): 图标名称（不带.svg后缀）
            enabled (bool): 是否可用
        """
        # 设置按钮可用性
        button.setEnabled(enabled)
        
        # 根据状态切换图标
        if enabled:
            button.setIcon(QIcon(get_resource_path(f'resources/icons/{icon_name}.svg')))
        else:
            button.setIcon(QIcon(get_resource_path(f'resources/icons/{icon_name}_gray.svg')))
    
    def setButtonsEnabled(self, enabled: bool):
        """设置按钮的启用状态
        Args:
            enabled: True表示恢复原始状态，False表示禁用
            禁用除了最小化、最大化、关闭、停止以外的所有按键
        """
        # 标题栏按钮映射：按钮 -> 图标名称
        titlebar_buttons_map = {
            self.title_bar.trash_btn: 'trash',
            self.title_bar.read_btn: 'read',
            self.title_bar.run_btn: 'play',
            self.title_bar.run_all_btn: 'run-all',
            self.title_bar.test_btn: 'test',
            self.title_bar.prev_audio_btn: 'prev_audio',
            self.title_bar.next_audio_btn: 'next_audio',
        }
        
        # 主窗口按钮
        main_buttons_to_toggle = [
            self.vad_btn,
            self.run_onset,
            self.run_offset,
            self.default_btn,
            self.folder_btn,
            self.file_btn,
            self.save_btn,
            self.reset_svg_btn,
            self.backward_btn,
            self.forward_btn,
            self.params_btn,
        ]
        
        all_buttons_to_toggle = list(titlebar_buttons_map.keys()) + main_buttons_to_toggle
        
        if not enabled:
            # 禁用前，保存所有需要切换的按钮的原始状态
            self._button_original_states.clear()
            for btn in all_buttons_to_toggle:
                self._button_original_states[btn] = btn.isEnabled()
            
            # 处理标题栏按钮，同时更新图标
            for btn, icon_name in titlebar_buttons_map.items():
                self._setButtonEnabled(btn, icon_name, False)
            
            # 处理主窗口按钮
            for btn in main_buttons_to_toggle:
                btn.setEnabled(False)
        else:
            # 恢复时，还原所有按钮的原始状态
            for btn, icon_name in titlebar_buttons_map.items():
                original_state = self._button_original_states.get(btn, True)
                self._setButtonEnabled(btn, icon_name, original_state)
            
            for btn in main_buttons_to_toggle:
                original_state = self._button_original_states.get(btn, True)
                btn.setEnabled(original_state)
        
        # 确保最小化、最大化、关闭、停止按钮始终可用
        self.title_bar.minimize_btn.setEnabled(True)
        self.title_bar.maximize_btn.setEnabled(True)
        self.title_bar.close_btn.setEnabled(True)
        self.title_bar.stop_btn.setEnabled(True)


        self.updateToolbarButtonsState()


    def onModeButtonClicked(self, clicked_btn):
        """模式按钮点击事件处理，确保一次只能选中一个模式"""
        # 取消其他两个按钮的选中状态
        for btn in [self.default_btn, self.folder_btn, self.file_btn]:
            if btn != clicked_btn:
                btn.setChecked(False)
        # 更新save和reset按钮状态
        self.updateToolbarButtonsState()


    def prevnext_audio(self, direction=None):
        """处理prev/next音频切换
        direction: None表示从按钮触发，使用sender判断；"prev"或"next"表示从信号触发
        """
        self.player.stop()
        
        # 确定切换方向
        if direction is not None:
            if direction == "prev":
                self.which_one -= 1
            else:  # "next"
                self.which_one += 1
        else:
            # 兼容旧的按钮点击方式
            sender = self.sender()
            if hasattr(sender, "text") and sender.text() == "Prev":
                self.which_one -= 1
            else:  # "Next" 或其他
                self.which_one += 1
        
        self.which_one %= len(self.file_paths)
        self.file_path = self.file_paths[self.which_one]
        dir_name = os.path.basename(os.path.dirname(self.file_path))
        base_name = os.path.basename(self.file_path)
        self.setWindowTitle(f"Praditor - {dir_name}/{base_name} ({self.which_one+1}/{len(self.file_paths)})")
        self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.vad_btn.isChecked())
        
        # 启用所有模式按钮
        self.default_btn.setEnabled(True)
        self.folder_btn.setEnabled(True)
        self.file_btn.setEnabled(True)
        
        # 三个按钮都不选中
        self.default_btn.setChecked(False)
        self.folder_btn.setChecked(False)
        self.file_btn.setChecked(False)
        
        # 更新save和reset按钮的可用性
        self.updateToolbarButtonsState()
        self.showParams()

        # 检查参数匹配，更新下划线
        self.checkIfParamsExist()
        self.showXsetNum()


    def stopSound(self):
        try:
            if self.audio_sink.state() == QAudio.State.ActiveState:
                self.audio_sink.stop()
                self.buffer.close()
                print("Audio stopped")
        except AttributeError:
            pass
    

    def saveParamsWithFolderName(self):
        """保存参数到当前文件夹，文件名为params.txt或params_vad.txt（VAD模式下）"""
        if hasattr(self, 'file_path') and self.file_path:
            # 检查是否处于VAD模式
            is_vad_mode = self.vad_btn.isChecked()
            file_suffix = "_vad" if is_vad_mode else ""
            
            folder_path = os.path.dirname(self.file_path)
            txt_file_path = os.path.join(folder_path, f"params{file_suffix}.txt")
            
            with open(txt_file_path, 'w') as txt_file:
                txt_file.write(f"{self.MySliders.getParams()}")
            print(f"Params saved to folder as params{file_suffix}.txt: {txt_file_path}")
    
    def saveParamsToExeLocation(self):
        """保存参数到exe所在位置，文件名为params.txt或params_vad.txt（VAD模式下）"""
        # 获取当前脚本所在目录（相当于exe所在位置）
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 检查是否处于VAD模式
        is_vad_mode = self.vad_btn.isChecked()
        file_suffix = "_vad" if is_vad_mode else ""
        
        txt_file_path = os.path.join(exe_dir, f"params{file_suffix}.txt")
        
        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(f"{self.MySliders.getParams()}")
        print(f"Params saved to exe location: {txt_file_path}")
    
    def saveParamsWithFileName(self):
        """保存参数到file同名，文件名后缀为.txt或_vad.txt（VAD模式下）"""
        if hasattr(self, 'file_path') and self.file_path:
            # 检查是否处于VAD模式
            is_vad_mode = self.vad_btn.isChecked()
            file_suffix = "_vad" if is_vad_mode else ""
            
            txt_file_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
            
            with open(txt_file_path, 'w') as txt_file:
                txt_file.write(f"{self.MySliders.getParams()}")
            print(f"Params saved with file name: {txt_file_path}")
    
    def toggleMaximize(self):
        # 切换窗口最大化/还原状态
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def setWindowTitle(self, title):
        # 重写setWindowTitle方法，同时更新自定义标题栏
        super().setWindowTitle(title)
        if hasattr(self, 'title_bar'):
            self.title_bar.set_title(title)
    
    def paintEvent(self, event):
        # 重写paintEvent事件，绘制带有抗锯齿的圆角背景和阴影
        painter = QPainter(self)
        
        # 设置高质量渲染提示（仅使用支持的属性）
        painter.setRenderHint(QPainter.Antialiasing, True)  # 抗锯齿
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)  # 平滑像素图变换
        painter.setRenderHint(QPainter.TextAntialiasing, True)  # 文本抗锯齿
        
        # 主窗口背景色
        background_color = QColor(233, 237, 241)  # #E9EDF1
        
        # 创建圆角矩形路径
        radius = 8  # 与CSS中设置的border-radius保持一致
        
        # 绘制阴影 - 更明显的黑色阴影效果
        shadow_rect = QRectF(self.rect())
        
        # 设置更明显的阴影参数
        shadow_radius = 10
        shadow_opacity = 30
        
        # 绘制多层阴影，从外向内，透明度逐渐降低
        for i in range(shadow_radius, 0, -1):
            # 计算当前阴影的透明度和偏移量
            opacity = int(shadow_opacity * (i / shadow_radius))
            offset = shadow_radius - i + 1
            
            # 创建阴影矩形
            shadow_rect_offset = QRectF(
                shadow_rect.x() + offset,
                shadow_rect.y() + offset,
                shadow_rect.width() - offset * 2,
                shadow_rect.height() - offset * 2
            )
            
            # 创建阴影路径
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(shadow_rect_offset, radius, radius)
            
            # 绘制阴影
            shadow_color = QColor(0, 0, 0, opacity)  # 黑色阴影，透明度根据层数调整
            painter.fillPath(shadow_path, shadow_color)
        
        # 绘制主窗口背景
        main_rect = QRectF(self.rect())
        main_path = QPainterPath()
        main_path.addRoundedRect(main_rect, radius, radius)
        painter.fillPath(main_path, background_color)
    
    def mousePressEvent(self, event):
        # 重写鼠标按下事件，当点击主窗口背景时，将焦点设置到主窗口
        # 这样可以让QLineEdit失去焦点
        self.setFocus(Qt.MouseFocusReason)
        event.accept()




app = QApplication(sys.argv)

# 创建系统托盘图标
# tray_icon = QSystemTrayIcon(QIcon("icon.png"), app)

window = MainWindow()

# 加载图标文件
# icon = QIcon('icon.png')  # 替换为你的图标文件路径
print(get_resource_path('resources/icons/icon.ico'))
print(os.path.exists(get_resource_path("resources/icons/icon.ico")))
# 设置窗口图标
# window.setWindowIcon(QIcon(resource_path('icon.ico')))
window.show()

app.exec()
