import ctypes
import os
import shutil
import sys
import webbrowser

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QIcon
from PySide6.QtMultimedia import QAudioOutput, QAudio, \
    QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QFileDialog, QWidget, QToolBar, QPushButton, QSizePolicy, QMessageBox
)

from src.gui.styles import *
from src.core.detection_auto import autoPraditorWithTimeRange, create_textgrid_with_time_point
# from core_light import autoPraditorWithTimeRange, create_textgrid_with_time_point
from src.gui.plots_auto import AudioViewer
from src.gui.sliders_auto import MySliders
from src.utils.audio import isAudioFile, get_frm_intervals_from_textgrid
from src.utils.resources import get_resource_path

plat = os.name.lower()

if plat == 'nt':  # Windows
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'AutoPraditor') # arbitrary string


elif plat == 'posix':  # Unix-like systems (Linux, macOS)
    pass
else:
    pass


class CustomTitleBar(QWidget):
    """自定义Windows风格标题栏，类似Trae样式"""
    
    # 定义信号
    close_signal = Signal()
    minimize_signal = Signal()
    maximize_signal = Signal()
    file_menu_clicked = Signal()
    help_menu_clicked = Signal()
    run_signal = Signal()
    test_signal = Signal()
    trash_signal = Signal()
    read_signal = Signal()
    onset_signal = Signal()
    offset_signal = Signal()
    prev_audio_signal = Signal()
    next_audio_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化拖拽变量
        self.drag_position = QPoint()
        
        # 设置标题栏样式，确保完全覆盖默认菜单栏区域
        # 移除固定高度，改为随内容自适应
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: none;
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
        layout.setContentsMargins(8, 0, 8, 0)  # 左右各8px边距，上下无边距
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignVCenter)  # 垂直居中对齐
        
        # 创建设置按钮（使用settings.svg图标）
        self.help_menu_btn = QPushButton()
        self.help_menu_btn.setIcon(QIcon(get_resource_path('resources/icons/settings.svg')))
        self.help_menu_btn.setFixedSize(32, 32)
        self.help_menu_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.help_menu_btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        # 连接菜单按钮信号
        self.help_menu_btn.clicked.connect(self.help_menu_clicked.emit)
        
        # 添加hover事件
        self.help_menu_btn.enterEvent = lambda event: self.help_menu_btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.help_menu_btn.leaveEvent = lambda event: self.help_menu_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        
        # 添加设置按钮到布局左侧
        layout.addWidget(self.help_menu_btn)
        
        # 添加标题标签，设置居左显示（Windows风格）
        self.title_label = QLabel("AutoPraditor")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 居左垂直居中
        self.title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #333333; padding: 5px 10px 5px 5px;")
        # 设置标题标签为可点击，鼠标指针为手形
        self.title_label.setCursor(QCursor(Qt.PointingHandCursor))
        # 将标题点击事件连接到file_menu_clicked信号
        self.title_label.mousePressEvent = lambda event: self.file_menu_clicked.emit()
        layout.addWidget(self.title_label)
        
        # 添加前一个音频按钮
        self.prev_audio_btn = QPushButton()
        self.prev_audio_btn.setIcon(QIcon(get_resource_path('resources/icons/prev_audio.svg')))
        self.prev_audio_btn.setFixedSize(32, 32)
        self.prev_audio_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.prev_audio_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.prev_audio_btn.setStatusTip("Previous Audio")
        # 添加hover事件
        self.prev_audio_btn.enterEvent = lambda event: self.prev_audio_btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.prev_audio_btn.leaveEvent = lambda event: self.prev_audio_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        layout.addWidget(self.prev_audio_btn)
        
        # 添加后一个音频按钮
        self.next_audio_btn = QPushButton()
        self.next_audio_btn.setIcon(QIcon(get_resource_path('resources/icons/next_audio.svg')))
        self.next_audio_btn.setFixedSize(32, 32)
        self.next_audio_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.next_audio_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_audio_btn.setStatusTip("Next Audio")
        # 添加hover事件
        self.next_audio_btn.enterEvent = lambda event: self.next_audio_btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.next_audio_btn.leaveEvent = lambda event: self.next_audio_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        layout.addWidget(self.next_audio_btn)
        
        # 添加伸缩空间，将按钮推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)
        
        # 添加onset和offset按钮
        self.onset_btn = QPushButton("Onset")
        self.onset_btn.setStatusTip("Extract Onsets")
        self.onset_btn.setFixedSize(80, 25)
        onset_color = "#1991D3"
        self.onset_btn.setStyleSheet(f"QPushButton {{ background: {onset_color}; color: white; font-weight: bold; border: 2px solid {onset_color}; border-radius: 5px; margin: 0px; font-size: 13px; }} QPushButton:pressed {{ background: #666666; color: {onset_color}; font-weight: bold; border: 2px solid {onset_color}; border-radius: 5px; margin: 0px; }} QPushButton:checked {{ background-color: white; color: {onset_color}; border: 2px solid {onset_color}; font-weight: bold; border-radius: 5px; margin: 0px; }}")
        self.onset_btn.setCheckable(True)
        self.onset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(self.onset_btn)
        
        layout.addSpacing(8)  # 添加按钮之间的空格
        
        self.offset_btn = QPushButton("Offset")
        self.offset_btn.setStatusTip("Extract Offsets")
        self.offset_btn.setFixedSize(80, 25)
        offset_color = "#2AD25E"
        self.offset_btn.setStyleSheet(f"QPushButton {{ background: {offset_color}; color: white; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; font-size: 13px; }} QPushButton:pressed {{ background: #666666; color: {offset_color}; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; }} QPushButton:checked {{ background-color: white; color: {offset_color}; border: 2px solid {offset_color}; font-weight: bold; border-radius: 5px; margin: 0px; }}")
        self.offset_btn.setCheckable(True)
        self.offset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(self.offset_btn)
        
        layout.addSpacing(8)  # 添加按钮之间的空格
        
        # 连接onset和offset按钮信号
        self.onset_btn.pressed.connect(self.onset_signal.emit)
        self.offset_btn.pressed.connect(self.offset_signal.emit)
        
        # 添加trash按钮（用于清除onsets和offsets）
        self.trash_btn = QPushButton()
        self.trash_btn.setIcon(QIcon(get_resource_path('resources/icons/trash.svg')))
        self.trash_btn.setFixedSize(32, 32)
        self.trash_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.trash_btn.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(self.trash_btn)
        
        # 添加read按钮（用于显示onsets和offsets）
        self.read_btn = QPushButton()
        self.read_btn.setIcon(QIcon(get_resource_path('resources/icons/read.svg')))
        self.read_btn.setFixedSize(32, 32)
        self.read_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.read_btn.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(self.read_btn)
        
        # 添加运行按钮（类似IDE中的播放键）
        self.run_btn = QPushButton()
        self.run_btn.setIcon(QIcon(get_resource_path('resources/icons/play.svg')))
        self.run_btn.setFixedSize(32, 32)
        self.run_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.run_btn.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(self.run_btn)
        
        # 添加测试按钮
        self.test_btn = QPushButton()
        self.test_btn.setIcon(QIcon(get_resource_path('resources/icons/test.svg')))
        self.test_btn.setFixedSize(32, 32)
        self.test_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.test_btn.setCursor(QCursor(Qt.PointingHandCursor))
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
        
        # 连接按钮信号
        self.trash_btn.clicked.connect(self.trash_signal.emit)
        self.read_btn.clicked.connect(self.read_signal.emit)
        self.run_btn.clicked.connect(self.run_signal.emit)
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
        self.close_btn.enterEvent = lambda event: self.update_button_style(self.close_btn, 'close', 'hover')
        self.close_btn.leaveEvent = lambda event: self.update_button_style(self.close_btn, 'close', 'normal')
        self.close_btn.pressed.connect(lambda: self.update_button_style(self.close_btn, 'close', 'pressed'))
        self.close_btn.released.connect(lambda: self.update_button_style(self.close_btn, 'close', 'hover'))
        
        # 最小化按钮
        self.minimize_btn.enterEvent = lambda event: self.update_button_style(self.minimize_btn, 'minimize', 'hover')
        self.minimize_btn.leaveEvent = lambda event: self.update_button_style(self.minimize_btn, 'minimize', 'normal')
        self.minimize_btn.pressed.connect(lambda: self.update_button_style(self.minimize_btn, 'minimize', 'pressed'))
        self.minimize_btn.released.connect(lambda: self.update_button_style(self.minimize_btn, 'minimize', 'hover'))
        
        # 最大化按钮
        self.maximize_btn.enterEvent = lambda event: self.update_button_style(self.maximize_btn, 'maximize', 'hover')
        self.maximize_btn.leaveEvent = lambda event: self.update_button_style(self.maximize_btn, 'maximize', 'normal')
        self.maximize_btn.pressed.connect(lambda: self.update_button_style(self.maximize_btn, 'maximize', 'pressed'))
        self.maximize_btn.released.connect(lambda: self.update_button_style(self.maximize_btn, 'maximize', 'hover'))
        
        # 运行按钮
        self.run_btn.enterEvent = lambda event: self.run_btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.run_btn.leaveEvent = lambda event: self.run_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        
        # 测试按钮
        self.test_btn.enterEvent = lambda event: self.test_btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.test_btn.leaveEvent = lambda event: self.test_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        
        # trash按钮
        self.trash_btn.enterEvent = lambda event: self.trash_btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.trash_btn.leaveEvent = lambda event: self.trash_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        
        # read按钮
        self.read_btn.enterEvent = lambda event: self.read_btn.setStyleSheet("background-color: #E8E8E8; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.read_btn.leaveEvent = lambda event: self.read_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
    
    def update_button_style(self, btn, btn_type, state):
        """更新按钮样式（现代Windows风格）"""
        # 当状态为normal时，使用白色背景，否则使用配置的颜色
        if state == 'normal':
            color = 'white'
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
        if "AutoPraditor" in title:
            # 将AutoPraditor部分加粗，其他部分保持正常
            parts = title.split("AutoPraditor")
            formatted_title = f"<b>AutoPraditor</b>{parts[1] if len(parts) > 1 else ''}"
            self.title_label.setText(formatted_title)
        else:
            # 如果标题中没有AutoPraditor，直接设置
            self.title_label.setText(title)
        # 确保标签支持HTML格式
        self.title_label.setTextFormat(Qt.RichText)
    
    def update_maximize_button(self, is_maximized):
        """更新最大化按钮状态"""
        # macOS风格下，最大化按钮样式不变，只改变功能
        pass


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # 隐藏默认标题栏，使用自定义标题栏
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        
        # 设置窗口属性，实现带有抗锯齿的圆角
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_StyledBackground, False)
        
        # load window icon
        self.param_sets = []
        self.audio_sink = None
        self.buffer = None
        self.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.ico')))
        self.file_paths = []
        self.file_path = None
        self.which_one = 0
        self.setWindowTitle("AutoPraditor")
        self.setMinimumSize(1000, 750)


        # 初始化媒体播放器和音频输出
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)

        self.player.setAudioOutput(self.audio_output)

        # 创建自定义标题栏并设置为菜单栏部件，使其显示在工具栏上方
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)
        
        # 连接标题栏信号
        self.title_bar.close_signal.connect(self.close)
        self.title_bar.minimize_signal.connect(self.showMinimized)
        self.title_bar.maximize_signal.connect(self.toggleMaximize)
        self.title_bar.trash_signal.connect(self.clearXset)
        self.title_bar.read_signal.connect(self.readXset)
        self.title_bar.run_signal.connect(self.runPraditorOnAudio)
        self.title_bar.test_signal.connect(self.testPraditorOnAudio)
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
        
        # 隐藏默认菜单栏
        self.menuBar().setVisible(False)
        
        # TOOLBAR
        # ---------------------

        toolbar = QToolBar("My main toolbar")
        toolbar.setFixedHeight(40)
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
        QToolBar {
            background-color:white;
            spacing: 0px;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            margin: 0px;
            padding: 5px 10px;
        }

        QToolBar::separator {
            background-color: #DBDBDB;
            width: 1px;
            margin-left: 8px;
            margin-right: 8px;
            margin-top: 8px;
            margin-bottom: 8px;
        }
        "")  # 使用对象名称设置样式
        # toolbar.setIconSize(QSize(16, 16))


        self.addToolBar(toolbar)
        # ---------------------------------------------------------------
        toolbar.addSeparator()

        self.clear_xset = QPushButton("Clear", self)  # Reload
        self.clear_xset.setFixedSize(50, 25)
        self.clear_xset.setStatusTip("Clear Onsets and Offsets from the screen")
        self.clear_xset.setStyleSheet(qss_button_normal)
        self.clear_xset.pressed.connect(self.clearXset)

        toolbar.addWidget(self.clear_xset)


        self.read_xset = QPushButton("Show", self)
        self.read_xset.setFixedSize(50, 25)
        self.read_xset.setStatusTip("Read Onsets and Offsets if there is the existing .TextGrid")
        self.read_xset.setStyleSheet(qss_button_normal)
        self.read_xset.pressed.connect(self.readXset)
        toolbar.addWidget(self.read_xset)

        toolbar.addSeparator()

        self.prev_audio = QPushButton("Prev", self)
        self.prev_audio.setFixedSize(50, 25)
        self.prev_audio.setStatusTip("Go to PREVIOUS audio in the folder")
        self.prev_audio.setStyleSheet(qss_button_normal)
        self.prev_audio.pressed.connect(self.prevnext_audio)
        toolbar.addWidget(self.prev_audio)

        self.run_praditor = QPushButton("Run", self)
        self.run_praditor.setFixedSize(50, 25)
        self.run_praditor.setStatusTip("Extract speech onsets/offsets")
        self.run_praditor.setStyleSheet(qss_button_normal)
        self.run_praditor.pressed.connect(self.runPraditorOnAudio)
        toolbar.addWidget(self.run_praditor)
        
        self.test_praditor = QPushButton("Test", self)
        self.test_praditor.setFixedSize(50, 25)
        self.test_praditor.setStatusTip("Test the number of onsets/offsets but no change to .TextGrid")
        self.test_praditor.setStyleSheet(qss_button_normal)
        self.test_praditor.pressed.connect(self.testPraditorOnAudio)
        toolbar.addWidget(self.test_praditor)
        

        self.next_audio = QPushButton("Next", self)
        self.next_audio.setFixedSize(50, 25)
        self.next_audio.setStatusTip("Go to NEXT audio in the folder")
        self.next_audio.setStyleSheet(qss_button_normal)
        self.next_audio.pressed.connect(self.prevnext_audio)
        toolbar.addWidget(self.next_audio)
        toolbar.addSeparator()

        # ----------------------------------------------
        # ----------------------------------------------
        # ----------------------------------------------


        # self.run_onset = QPushButton("Onset", self)
        self.run_onset = QLabel("", self)
        self.run_onset.setStatusTip("Extract Onsets")
        self.run_onset.setFixedSize(180, 25)
        # self.run_onset.pressed.connect(self.turnOnset)
        self.run_onset.setStyleSheet(qss_button_checkable_with_color())
        # self.run_onset.setCheckable(True)
        # self.run_onset.setChecked(False)
        toolbar.addWidget(self.run_onset)

        # self.run_offset = QPushButton("Offset", self)
        # self.run_offset.setStatusTip("Extract Offsets")
        # self.run_offset.setFixedSize(80, 25)
        # self.run_offset.pressed.connect(self.turnOffset)
        # self.run_offset.setStyleSheet(qss_button_checkable_with_color("#2AD25E"))
        # self.run_offset.setCheckable(True)
        # # self.run_offset.setChecked(False)
        # toolbar.addWidget(self.run_offset)




        spacer_left = QWidget()
        spacer_left.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer_left)



        self.select_mode = QPushButton("Default", self)
        self.select_mode.setStatusTip("Choose to show Default or Current params")
        self.select_mode.setFixedSize(60, 25)
        self.select_mode.released.connect(self.showParams)
        self.select_mode.setStyleSheet(qss_button_checkable_with_color("black"))
        self.select_mode.setCheckable(True)
        self.select_mode.setChecked(True)
        toolbar.addWidget(self.select_mode)
        # print(self.select_mode.isChecked())


        toolbar.addSeparator()
        # ----------------------------------------------
        # ----------------------------------------------
        # ----------------------------------------------


        self.save_param = QPushButton("Save", self)
        self.save_param.setFixedSize(50, 25)
        self.save_param.setStatusTip("Save these params to the selected mode")
        self.save_param.setStyleSheet(qss_button_checkable_with_color("#333333"))
        self.save_param.pressed.connect(self.saveParams)
        self.save_param.setCheckable(True)
        self.save_param.setChecked(True)
        toolbar.addWidget(self.save_param)

        self.reset_param = QPushButton("Reset", self)
        self.reset_param.setFixedSize(50, 25)
        self.reset_param.setStatusTip("Reset to params that has been saved")
        self.reset_param.setStyleSheet(qss_button_normal)
        self.reset_param.pressed.connect(self.resetParams)
        # self.reset_param.setCheckable(True)
        # self.reset_param.setChecked(True)
        toolbar.addWidget(self.reset_param)

        self.last_param = QPushButton("Last", self)
        self.last_param.setFixedSize(50, 25)
        self.last_param.setStatusTip("Roll back to the last set of params")
        self.last_param.setStyleSheet(qss_button_normal)
        self.last_param.pressed.connect(self.lastParams)
        toolbar.addWidget(self.last_param)

        toolbar.addSeparator()
        # spacer_right = QWidget()
        # spacer_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # toolbar.addWidget(spacer_right)


        # ----------------------------------------------
        # ----------------------------------------------
        # ----------------------------------------------


        # ---------------------
        # TOOLBAR




        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()  # 创建一个水平布局
        central_widget.setLayout(layout)
        # file_menu.addSeparator()
        # file_menu.addAction(button_action2)
        # ---------------------------------------------------
        self.AudioViewer = AudioViewer()
        self.AudioViewer.setMinimumHeight(200)
        layout.addWidget(self.AudioViewer)
        # ---------------------------------------------------

        # ---------------------------------------------------
        # self.ParamButtons = ParamButtons()
        # layout.addWidget(self.ParamButtons)
        # ---------------------------------------------------

        # ---------------------------------------------------
        self.MySliders = MySliders()
        self.MySliders.amp_slider_onset.setStatusTip(" Onset  |  A coef for determining actual threshold (baseline × coefficient = actual threshold)")
        self.MySliders.numValid_slider_onset.setStatusTip(" Onset  |  Accumulated net count of above-threshold frames")
        # self.MySliders.penalty_slider_onset.setStatusTip(" Onset  |  Penalty for below-threshold frames")
        # self.MySliders.ref_len_slider_onset.setStatusTip(" Onset  |  Length of the reference segment used to generate baseline (useful in detecting in-utterance silent pause)")
        # self.MySliders.ratio_slider_onset.setStatusTip(" Onset  |  % of frames retained in the kernel")
        # self.MySliders.win_size_slider_onset.setStatusTip(" Onset  |  Size of the kernel (in frames)")
        self.MySliders.eps_ratio_slider_onset.setStatusTip(" Onset  |  Neighborhood radius in DBSCAN clustering (useful in detecting in-utterance silent pause)")
        self.MySliders.cutoff1_slider_onset.setStatusTip(" Onset  |  Higher cutoff frequency of bandpass filter")
        self.MySliders.cutoff0_slider_onset.setStatusTip(" Onset  |  Lower cutoff frequency of bandpass filter")


        # self.MySliders.amp_slider_offset.setStatusTip(" Offset  |  A coef for determining actual threshold (baseline × coefficient = actual threshold)")
        # self.MySliders.numValid_slider_offset.setStatusTip(" Offset  |  Accumulated net count of above-threshold frames")
        # # self.MySliders.penalty_slider_offset.setStatusTip(" Offset  |  Penalty for below-threshold frames")
        # # self.MySliders.ref_len_slider_offset.setStatusTip(" Offset  |  Length of the reference segment used to generate baseline (useful in detecting in-utterance silent pause)")
        # # self.MySliders.ratio_slider_offset.setStatusTip(" Offset  |  % of frames retained in the kernel")
        # # self.MySliders.win_size_slider_offset.setStatusTip(" Offset  |  Size of the kernel (in frames)")
        # self.MySliders.eps_ratio_slider_offset.setStatusTip(" Offset  |  Neighborhood radius in DBSCAN clustering (useful in detecting in-utterance silent pause)")
        # self.MySliders.cutoff1_slider_offset.setStatusTip(" Offset  |  Higher cutoff frequency of bandpass filter")
        # self.MySliders.cutoff0_slider_offset.setStatusTip(" Offset  |  Lower cutoff frequency of bandpass filter")


        layout.addWidget(self.MySliders)
        # ---------------------------------------------------
        layout.setContentsMargins(10, 20, 10, 40)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #E9EDF1; 

            }

        """)


        # 初始化参数txt
        # 检查是否存在default mode

        # 初始化参数文件，使用当前文件所在目录
        default_params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params_vad.txt")
        print(default_params_path)
        if not os.path.exists(default_params_path):
            default_params_path = get_resource_path("src/app/params_vad.txt")
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
        self.AudioViewer.tg_dict_tp = get_frm_intervals_from_textgrid(self.file_path)
        
        if not self.AudioViewer.tg_dict_tp or self.AudioViewer.tg_dict_tp == {"onset": [], "offset": []}:
            popup_window = QMessageBox()
            # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
            popup_window.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.png')))
            popup_window.setText(f"This audio file has no .TextGrid attached.")
            popup_window.exec()
            return


        self.AudioViewer.updateXset(self.AudioViewer.tg_dict_tp)
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["onset"], isVisible=True)#not self.run_onset.isChecked())
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["offset"], isVisible=True)#not self.run_onset.isChecked())
        # self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["offset"], isVisible=not self.run_offset.isChecked())


    def clearXset(self):
        # self.AudioViewer.tg_dict_tp = get_frm_points_from_textgrid(self.file_path)

        # if not self.run_onset.isChecked():
        self.AudioViewer.removeXset(self.AudioViewer.tg_dict_tp["onset"])
        # if not self.run_offset.isChecked():
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
        # self.MySliders.win_size_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        # self.MySliders.ratio_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        # self.MySliders.penalty_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        # self.MySliders.ref_len_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))
        self.MySliders.eps_ratio_slider_onset.param_slider.setStyleSheet(qss_slider_with_color(onset_color))

        self.MySliders.amp_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.cutoff0_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.cutoff1_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.numValid_slider_onset.param_slider.setDisabled(slider_status)
        # self.MySliders.win_size_slider_onset.param_slider.setDisabled(slider_status)
        # self.MySliders.ratio_slider_onset.param_slider.setDisabled(slider_status)
        # self.MySliders.penalty_slider_onset.param_slider.setDisabled(slider_status)
        # self.MySliders.ref_len_slider_onset.param_slider.setDisabled(slider_status)
        self.MySliders.eps_ratio_slider_onset.param_slider.setDisabled(slider_status)

        self.AudioViewer.showOnset = not slider_status
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["onset"], isVisible=self.AudioViewer.showOnset)


    # def turnOffset(self):
    #     if not self.run_offset.isChecked():
    #         offset_color = "#AFAFAF"
    #         slider_status = True
    #     else:
    #         offset_color = "#2AD25E"
    #         slider_status = False

    #     self.MySliders.amp_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     self.MySliders.cutoff0_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     self.MySliders.cutoff1_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     self.MySliders.numValid_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     # self.MySliders.win_size_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     # self.MySliders.ratio_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     # self.MySliders.penalty_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     # self.MySliders.ref_len_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))
    #     self.MySliders.eps_ratio_slider_offset.param_slider.setStyleSheet(qss_slider_with_color(offset_color))

    #     self.MySliders.amp_slider_offset.param_slider.setDisabled(slider_status)
    #     self.MySliders.cutoff0_slider_offset.param_slider.setDisabled(slider_status)
    #     self.MySliders.cutoff1_slider_offset.param_slider.setDisabled(slider_status)
    #     self.MySliders.numValid_slider_offset.param_slider.setDisabled(slider_status)
    #     # self.MySliders.win_size_slider_offset.param_slider.setDisabled(slider_status)
    #     # self.MySliders.ratio_slider_offset.param_slider.setDisabled(slider_status)
    #     # self.MySliders.penalty_slider_offset.param_slider.setDisabled(slider_status)
    #     # self.MySliders.ref_len_slider_offset.param_slider.setDisabled(slider_status)
    #     self.MySliders.eps_ratio_slider_offset.param_slider.setDisabled(slider_status)

    #     self.AudioViewer.showOffset = not slider_status
    #     self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["offset"], isVisible=self.AudioViewer.showOffset)




    def resetParams(self):
        if self.select_mode.text() == "Current":
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        else:  # if self.select_mode.text() == "Default":
            # 保存到当前文件所在目录
            txt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params_vad.txt")

        try:
            with open(txt_file_path, 'r') as txt_file:
                self.MySliders.resetParams(eval(txt_file.read()))
            print(f"Params TXT file read from: {txt_file_path}")

        except FileNotFoundError:
            self.select_mode.setChecked(False)

            print("Go back to Default mode")


            self.showParams()

    def saveParams(self):
        # print(get_resource_path("config/params_vad.txt"))
        if self.select_mode.text() == "Current":
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        else:  # if self.select_mode.text() == "Default":
            txt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params_vad.txt")


        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(f"{self.MySliders.getParams()}")
        print(self.save_param.isChecked())
        self.save_param.setChecked(False)


    def checkIfParamsExist(self):
        if self.select_mode.text() == "Current":
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        else:  # if self.select_mode.text() == "Default":
            # 从当前文件所在目录读取
            txt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params_vad.txt")
            if not os.path.exists(txt_file_path):
                txt_file_path = get_resource_path("src/app/params_vad.txt")

        with open(txt_file_path, 'r') as txt_file:
            # print(str(txt_file.read()) == str(self.MySliders.getParams()))
            # print("___")
            self.save_param.setChecked(str(txt_file.read()) == str(self.MySliders.getParams()))

        # defaul和last


    def showParams(self):
        # 第一步 如果音频文件本身就不存在，不运行
        if self.file_path is None:
            self.select_mode.setText("Default")
            self.select_mode.setChecked(True)
            return
        # 第二步 根据按钮本身的状态调整文字显示（按钮样式会根据按钮状态自动调整跟随）
        if self.select_mode.text() == "Default":
            self.select_mode.setText("Current")
        else:
            self.select_mode.setText("Default")
        # if self.select_mode.isChecked():

        # 第三步 如果是单独参数同时又不存在，那么先从默认参数复制一份到单独参数来
        if self.select_mode.text() == "Current":
            if not os.path.exists(os.path.splitext(self.file_path)[0] + "_vad.txt"):
                with open(os.path.splitext(self.file_path)[0] + "_vad.txt", "w") as txt_file:
                    default_params_path = os.path.join(os.getcwd(), "params_vad.txt")
                    if not os.path.exists(default_params_path):
                        default_params_path = get_resource_path("src/app/params_vad.txt")
                    with open(default_params_path, "r") as default_txt_file:
                        txt_file.write(default_txt_file.read())
        elif self.select_mode.text() == "Default":
            pass

        # 第四步 根据按钮文字呈现参数
        if self.select_mode.text() == "Current":
            with open(os.path.splitext(self.file_path)[0] + "_vad.txt", 'r') as txt_file:
                self.MySliders.resetParams(eval(txt_file.read()))
            self.select_mode.setChecked(False)
        elif self.select_mode.text() == "Default":
            default_params_path = os.path.join(os.getcwd(), "params_vad.txt")
            if not os.path.exists(default_params_path):
                default_params_path = get_resource_path("src/app/params_vad.txt")
            with open(default_params_path, 'r') as txt_file:
                self.MySliders.resetParams(eval(txt_file.read()))
            self.select_mode.setChecked(True)



    def lastParams(self):
        print(len(self.param_sets))
        if len(self.param_sets) == 2:

            self.MySliders.resetParams(self.param_sets[-2])
            self.param_sets.reverse()



    # def showParamInstruction(self):
    #     # QMessageBox.information(None, "标题", "这是一个信息消息框。")
    #     self.popup = Example()
    #     self.popup.show()

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
            self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path)

            if os.path.exists(os.path.splitext(self.file_path)[0] + "_vad.txt"):
                self.select_mode.setChecked(False)
            else:
                self.select_mode.setChecked(True)
            self.showParams()
            self.setWindowTitle(f"Praditor - {self.file_path} ({self.which_one+1}/{len(self.file_paths)})")

            self.showXsetNum()
            self.param_sets.append(self.MySliders.getParams())

        else:
            print("Empty folder")


    def showXsetNum(self):
        print(self.AudioViewer.tg_dict_tp)
        if not self.AudioViewer.tg_dict_tp['onset']:
            self.run_onset.setText("")
        else:
            self.run_onset.setText(f"{len(self.AudioViewer.tg_dict_tp['onset'])} Onset(s), {len(self.AudioViewer.tg_dict_tp['offset'])} Offset(s) ")

        # if not self.AudioViewer.tg_dict_tp['offset']:
        #     self.run_offset.setText("Offset")
        # else:
        #     self.run_offset.setText(f"Offset: {len(self.AudioViewer.tg_dict_tp['offset'])}")

    def browseInstruction(self):
        # 使用webbrowser模块打开默认浏览器并导航到指定网址
        webbrowser.open('https://github.com/Paradeluxe/Praditor?tab=readme-ov-file#how-to-use-praditor')

    def runPraditorOnAudio(self):
        # 检查采样率
        # print(self.AudioViewer.audio_samplerate)
        # print(self.MySliders.cutoff1_slider_onset.value_label.text())
        if float(self.MySliders.cutoff1_slider_onset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2:# or \
            # float(self.MySliders.cutoff1_slider_offset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2:

            popup_window = QMessageBox()
            # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
            popup_window.setWindowIcon(QIcon(get_resource_path('icon.png')))
            popup_window.setText(f"LowPass exceeds the Nyquist frequency boundary {float(self.AudioViewer.audio_samplerate)/2:.0f}")
            popup_window.exec()
            return



        # if not self.run_onset.isChecked():
        try:
            self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["onset"])
        except KeyError:
            pass
        onsets = autoPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "onset")
        # else:
        #     self.AudioViewer.tg_dict_tp["onset"] = []

        # if not self.run_offset.isChecked():
        # if not self.run_onset.isChecked():
        try:
            self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["offset"])
        except KeyError:
            pass
        offsets = autoPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "offset")
        # else:
        #     self.AudioViewer.tg_dict_tp["offset"] = []

        ###########################
        # 如果头尾是从有声直接开始/结束，则为其赋值为0/音频长度
        ###########################
        # onsets = sorted(onsets)
        # offsets = sorted(offsets)

        if onsets[0] >= offsets[0]:
            onsets = [0.0] + onsets

        if offsets[-1] <= onsets[-1]:
            offsets.append(self.AudioViewer.audio_obj.duration_seconds)

        # print(onsets)
        # print(offsets)
        #--------------------------#



        ##########################
        # Select the one offset that is closest to onset and earlier than onset
        ##########################

        new_onsets = []
        new_offsets = []
        for i, onset in enumerate(onsets):
            # print(onset)
            if i == 0:
                new_offsets.append(offsets[-1])
                new_onsets.append(onset)
            else:
                try:
                    new_offsets.append(max([offset for offset in offsets if onsets[i-1] < offset < onset]))
                    new_onsets.append(onset)

                except ValueError:
                    pass


        new_onsets = sorted(new_onsets)
        new_offsets = sorted(new_offsets)
        #--------------------------#


        self.AudioViewer.tg_dict_tp["onset"] = new_onsets
        self.AudioViewer.tg_dict_tp["offset"] = new_offsets
        # print(self.AudioViewer.tg_dict_tp)


        create_textgrid_with_time_point(self.file_path, self.AudioViewer.tg_dict_tp["onset"], self.AudioViewer.tg_dict_tp["offset"])
        self.readXset()
        self.showXsetNum()
        self.update_current_param()


    def testPraditorOnAudio(self):
        if float(self.MySliders.cutoff1_slider_onset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2:# or \
            #float(self.MySliders.cutoff1_slider_offset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2:

            popup_window = QMessageBox()
            # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
            popup_window.setWindowIcon(QIcon(resource_path('icon.png')))
            popup_window.setText(f"LowPass exceeds the Nyquist frequency boundary {float(self.AudioViewer.audio_samplerate)/2:.0f}")
            popup_window.exec()


        _test_tg_dict_tp = {"onset": [], "offset": []}
        # if not self.run_onset.isChecked():
        _test_tg_dict_tp["onset"] = autoPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "onset")
        # else:
            # _test_tg_dict_tp["onset"] = []

        # if not self.run_offset.isChecked():
        _test_tg_dict_tp["offset"] = autoPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "offset")
        # else:
            # _test_tg_dict_tp["offset"] = []
        


        if not _test_tg_dict_tp['onset']:
            self.run_onset.setText("")
        else:
            self.run_onset.setText(f"{len(_test_tg_dict_tp['onset'])} Onset(s), {len(_test_tg_dict_tp['offset'])} Offset(s) ?")

        # if not _test_tg_dict_tp['offset']:
        #     self.run_offset.setText("Offset")
        # else:
        #     self.run_offset.setText(f"Offset: {len(_test_tg_dict_tp['offset'])} ?")



        # self.update_current_param()


    def update_current_param(self):
        if self.MySliders.getParams() in self.param_sets:
            self.param_sets.remove(self.MySliders.getParams())
            self.param_sets.append(self.MySliders.getParams())
        else:
            self.param_sets.append(self.MySliders.getParams())
            self.param_sets = self.param_sets[-2:]



    def prevnext_audio(self):
        print(self.sender().text())
        self.player.stop()
        if self.sender().text() == "Prev":
            self.which_one -= 1
        else:  # "Next"
            self.which_one += 1
        self.which_one %= len(self.file_paths)
        self.file_path = self.file_paths[self.which_one]
        self.setWindowTitle(f"Praditor (VAD) - {self.file_path} ({self.which_one+1}/{len(self.file_paths)})")
        self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path)

        if os.path.exists(os.path.splitext(self.file_path)[0] + "_vad.txt"):
            self.select_mode.setChecked(False)
        else:
            self.select_mode.setChecked(True)
        self.showParams()
        self.showXsetNum()
        # self.update_current_param()
        # self.statusBar().showMessage("1", 0)


    def stopSound(self):
        try:
            if self.audio_sink.state() == QAudio.State.ActiveState:
                self.audio_sink.stop()
                self.buffer.close()
                print("Audio stopped")
        except AttributeError:
            pass



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