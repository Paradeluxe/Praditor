import ctypes
import os
import sys
import webbrowser

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PySide6.QtCore import Qt, QUrl, Signal, QPoint, QRectF
from PySide6.QtGui import QAction, QIcon, QCursor, QPainterPath, QRegion, QPainter, QColor
from PySide6.QtMultimedia import QAudioOutput, QAudio, \
    QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog, QWidget, QToolBar, QPushButton, QSizePolicy, QMessageBox, QLabel, QComboBox
)

from src.gui.styles import *
from src.core.detection import runPraditorWithTimeRange, create_textgrid_with_time_point
# from core_light import runPraditorWithTimeRange, create_textgrid_with_time_point
from src.gui.plots import AudioViewer
from src.gui.sliders import MySliders
from src.utils.audio import isAudioFile, get_frm_points_from_textgrid
from src.utils.resources import get_resource_path

plat = os.name.lower()

if plat == 'nt':  # Windows
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'Praditor') # arbitrary string


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
        layout.setContentsMargins(8, 0, 0, 0)  # 左侧边距，右侧无边距
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignVCenter)  # 垂直居中对齐
        
        # 创建菜单按钮
        self.file_menu_btn = QPushButton("File")
        self.help_menu_btn = QPushButton("Help")
        
        # 设置菜单按钮样式（Windows风格）
        menu_btn_style = """
            QPushButton {
                background-color: white;
                border: none;
                color: #333333;
                font-size: 13px;
                padding: 8px 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """
        
        for btn in [self.file_menu_btn, self.help_menu_btn]:
            btn.setStyleSheet(menu_btn_style)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
        
        # 连接菜单按钮信号
        self.file_menu_btn.clicked.connect(self.file_menu_clicked.emit)
        self.help_menu_btn.clicked.connect(self.help_menu_clicked.emit)
        
        # 添加菜单按钮到布局左侧
        layout.addWidget(self.file_menu_btn)
        layout.addWidget(self.help_menu_btn)
        
        # 添加标题标签，设置居左显示（Windows风格）
        self.title_label = QLabel("Praditor")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 居左垂直居中
        self.title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #333333; padding: 0 12px;")
        layout.addWidget(self.title_label)
        
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
        
        # 添加按钮之间的空格
        layout.addSpacing(8)
        
        self.offset_btn = QPushButton("Offset")
        self.offset_btn.setStatusTip("Extract Offsets")
        self.offset_btn.setFixedSize(80, 25)
        offset_color = "#2AD25E"
        self.offset_btn.setStyleSheet(f"QPushButton {{ background: {offset_color}; color: white; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; font-size: 13px; }} QPushButton:pressed {{ background: #666666; color: {offset_color}; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; }} QPushButton:checked {{ background-color: white; color: {offset_color}; border: 2px solid {offset_color}; font-weight: bold; border-radius: 5px; margin: 0px; }}")
        self.offset_btn.setCheckable(True)
        self.offset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        layout.addWidget(self.offset_btn)
        
        # 添加按钮之间的空格
        layout.addSpacing(8)
        
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
                'hover': '#F5F5F5',
                'pressed': '#E0E0E0'
            },
            'maximize': {
                'normal': 'transparent',
                'hover': '#F5F5F5',
                'pressed': '#E0E0E0'
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
        self.run_btn.enterEvent = lambda event: self.run_btn.setStyleSheet("background-color: #F5F5F5; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.run_btn.leaveEvent = lambda event: self.run_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        
        # 测试按钮
        self.test_btn.enterEvent = lambda event: self.test_btn.setStyleSheet("background-color: #F5F5F5; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.test_btn.leaveEvent = lambda event: self.test_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        
        # trash按钮
        self.trash_btn.enterEvent = lambda event: self.trash_btn.setStyleSheet("background-color: #F5F5F5; border: none; color: #333333; font-size: 16px; text-align: center;")
        self.trash_btn.leaveEvent = lambda event: self.trash_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 16px; text-align: center;")
        
        # read按钮
        self.read_btn.enterEvent = lambda event: self.read_btn.setStyleSheet("background-color: #F5F5F5; border: none; color: #333333; font-size: 16px; text-align: center;")
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
        # self.setWindowIcon(QIcon(QPixmap(resource_path('icon.png'))))
        self.param_sets = []
        self.current_param_index = -1  # 初始化当前参数索引
        self.audio_sink = None
        self.buffer = None
        self.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.ico')))
        self.file_paths = []
        self.file_path = None
        self.which_one = 0
        self.setWindowTitle("Praditor")
        self.setMinimumSize(1000, 750)



        # 初始化媒体播放器和音频输出
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)

        self.player.setAudioOutput(self.audio_output)


        # icon = QIcon()
        # icon.addPixmap(QPixmap(resource_path("icon.png")), QIcon.Normal, QIcon.On)
        # self.setWindowIcon(icon)


        # MENU
        # --------------------------------------
        # self.menuBar().setFixedHeight(35)

        file_menu = self.menuBar().addMenu("&File")
        button_action = QAction("&Read file...", self)
        button_action.setStatusTip("Read audio files HERE!")
        button_action.triggered.connect(self.openFileDialog)
        file_menu.addAction(button_action)
        # file_menu.setStyleSheet("""
        #     QMenu {
        #         color: black;
        #         background-color: white;
        #
        #     }
        # """)

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
        self.title_bar.run_signal.connect(self.runPraditorOnAudio)
        self.title_bar.test_signal.connect(self.testPraditorOnAudio)
        self.title_bar.onset_signal.connect(self.turnOnset)
        self.title_bar.offset_signal.connect(self.turnOffset)
        
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
        # file_menu.addSeparator()
        # file_menu.addAction(button_action2)
        # ---------------------------------------------------
        self.AudioViewer = AudioViewer()
        self.AudioViewer.setMinimumHeight(200)
        layout.addWidget(self.AudioViewer, 1)  # 添加拉伸因子1，让AudioViewer占据更多空间
        # 连接AudioViewer的信号到prevnext_audio方法
        self.AudioViewer.prevClicked.connect(lambda: self.prevnext_audio("prev"))
        self.AudioViewer.nextClicked.connect(lambda: self.prevnext_audio("next"))
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
        self.MySliders.ratio_slider_onset.setStatusTip(" Onset  |  % of frames retained in the kernel")
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
        layout.setContentsMargins(10, 10, 10, 30)
        # 将内容部件添加到主布局
        main_layout.addWidget(central_widget)
        
        # TOOLBAR
        # ---------------------

        toolbar = QToolBar("My main toolbar")
        # 移除固定高度，改为自适应高度
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
        QToolBar {
            background-color:white;
            spacing: 0px;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            margin: 0px;
            padding: 5px 0px;
        }

        QToolBar::separator {
            background-color: #DBDBDB; /* 将分隔线的背景色设置为红色 */
            width: 1px; /* 设置分隔线的宽度 */
            margin-left: 5px; /* 左边距 */
            margin-right: 5px; /* 右边距 */
            margin-top: 5px; /* 上边距 */
            margin-bottom: 5px; /* 下边距 */
        }
        """)  # 使用对象名称设置样式
        # 设置工具栏边距与标题栏一致
        toolbar.layout().setContentsMargins(8, 5, 8, 5)
        # toolbar.setIconSize(QSize(16, 16))

        self.addToolBar(Qt.BottomToolBarArea, toolbar)
        # 保存工具栏引用，以便在resizeEvent中使用
        self.toolbar = toolbar
        # ---------------------------------------------------------------

        toolbar.addSeparator()
        
        # 保存按钮
        self.save_btn = QPushButton("Save", self)
        self.save_btn.setIcon(QIcon(get_resource_path('resources/icons/save.svg')))
        self.save_btn.setStatusTip("Save params to the selected location")
        self.save_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 13px; text-align: center; padding: 0; margin: 0 10px;")
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_btn.clicked.connect(self.saveParams)
        toolbar.addWidget(self.save_btn)
        
        # Reset按钮
        self.reset_svg_btn = QPushButton("Reset", self)
        self.reset_svg_btn.setIcon(QIcon(get_resource_path('resources/icons/reset.svg')))
        self.reset_svg_btn.setStatusTip("Reset to params that has been saved")
        self.reset_svg_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 13px; text-align: center; padding: 0; margin: 0 10px;")
        self.reset_svg_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_svg_btn.clicked.connect(self.resetParams)
        toolbar.addWidget(self.reset_svg_btn)

        toolbar.addSeparator()

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
        
        # Backward按钮
        self.backward_btn = QPushButton("Backward", self)
        self.backward_btn.setIcon(QIcon(get_resource_path('resources/icons/backward.svg')))
        self.backward_btn.setStatusTip("Load previous params")
        self.backward_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 13px; text-align: center; padding: 0; margin: 0 10px;")
        self.backward_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.backward_btn.clicked.connect(self.loadPreviousParams)
        toolbar.addWidget(self.backward_btn)
        
        # Forward按钮
        self.forward_btn = QPushButton("Forward", self)
        self.forward_btn.setIcon(QIcon(get_resource_path('resources/icons/forward.svg')))
        self.forward_btn.setStatusTip("Load next params")
        self.forward_btn.setStyleSheet("background-color: white; border: none; color: #333333; font-size: 13px; text-align: center; padding: 0; margin: 0 10px;")
        self.forward_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.forward_btn.clicked.connect(self.loadNextParams)
        toolbar.addWidget(self.forward_btn)
        
        # 添加伸缩空间，将参数索引标签推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)
        
        # 参数索引标签
        self.param_index_label = QLabel("0/0", self)
        self.param_index_label.setStyleSheet("color: #666666; font-size: 12px; padding: 0 10px;")
        toolbar.addWidget(self.param_index_label)
        
        # ---------------------
        # TOOLBAR



        # 移除可能冲突的CSS圆角设置，因为我们使用paintEvent绘制圆角
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent; 
            }

        """)
        
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
        self.default_btn.clicked.connect(self.onModeButtonClicked)
        self.folder_btn.clicked.connect(self.onModeButtonClicked)
        self.file_btn.clicked.connect(self.onModeButtonClicked)
        
        # 初始化时检查一次参数匹配，确保刚载入GUI时也能显示下划线
        self.checkIfParamsExist()
        
        # 初始化时更新save和reset按钮状态
        self.updateSaveResetButtonsState()



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
        self.AudioViewer.tg_dict_tp = get_frm_points_from_textgrid(self.file_path)

        if not self.AudioViewer.tg_dict_tp or self.AudioViewer.tg_dict_tp == {"onset": [], "offset": []}:
            popup_window = QMessageBox()
            # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
            popup_window.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.png')))
            popup_window.setText(f"This audio file has no .TextGrid attached.")
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
        
        if self.file_btn.isChecked():
            # File模式：从file同名的txt文件读取
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        elif self.folder_btn.isChecked():
            # Folder模式：从当前文件夹的同名txt文件读取
            folder_path = os.path.dirname(self.file_path)
            folder_name = os.path.basename(folder_path)
            txt_file_path = os.path.join(folder_path, f"{folder_name}.txt")
        else:  # Default模式
            # 从应用程序所在目录读取
            txt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params.txt")
            if not os.path.exists(txt_file_path):
                txt_file_path = get_resource_path("src/app/params.txt")

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


    def checkIfParamsExist(self):
        current_params = str(self.MySliders.getParams())
        current_params_dict = self.MySliders.getParams()
        
        # 重置所有按钮样式为默认
        default_style = qss_save_location_button
        
        # 定义下划线样式（在原有样式基础上添加下划线，不改变按钮大小）
        def getUnderlinedStyle(base_style):
            # 添加下划线样式，不改变按钮大小
            styled = base_style
            # 处理黑色文本情况
            if "color: black;" in styled:
                styled = styled.replace("color: black;", "color: black; text-decoration: underline;")
            # 处理灰色文本情况
            if "color: gray;" in styled:
                styled = styled.replace("color: gray;", "color: gray; text-decoration: underline;")
            return styled
        
        # 检查Default模式
        try:
            default_params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params.txt")
            if not os.path.exists(default_params_path):
                default_params_path = get_resource_path("src/app/params.txt")
            
            with open(default_params_path, 'r') as txt_file:
                saved_params = txt_file.read()
                if saved_params == current_params:
                    self.default_btn.setStyleSheet(getUnderlinedStyle(qss_save_location_button))
                else:
                    self.default_btn.setStyleSheet(default_style)
        except FileNotFoundError:
            self.default_btn.setStyleSheet(default_style)
        
        # 检查Folder模式
        try:
            if self.file_path:
                folder_path = os.path.dirname(self.file_path)
                folder_name = os.path.basename(folder_path)
                folder_params_path = os.path.join(folder_path, f"{folder_name}.txt")
                
                with open(folder_params_path, 'r') as txt_file:
                    saved_params = txt_file.read()
                    if saved_params == current_params:
                        self.folder_btn.setStyleSheet(getUnderlinedStyle(qss_save_location_button))
                    else:
                        self.folder_btn.setStyleSheet(default_style)
            else:
                self.folder_btn.setStyleSheet(default_style)
        except FileNotFoundError:
            self.folder_btn.setStyleSheet(default_style)
        
        # 检查File模式
        try:
            if self.file_path:
                file_params_path = os.path.splitext(self.file_path)[0] + ".txt"
                
                with open(file_params_path, 'r') as txt_file:
                    saved_params = txt_file.read()
                    if saved_params == current_params:
                        self.file_btn.setStyleSheet(getUnderlinedStyle(qss_save_location_button))
                    else:
                        self.file_btn.setStyleSheet(default_style)
            else:
                self.file_btn.setStyleSheet(default_style)
        except FileNotFoundError:
            self.file_btn.setStyleSheet(default_style)

        # defaul和last


    def showParams(self):
        # 简化版showParams，只处理默认参数
        if self.file_path is None:
            return
        
        # 默认只使用文件同名参数
        txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        
        # 如果参数文件不存在，创建一个默认的
        if not os.path.exists(txt_file_path):
            default_params_path = os.path.join(os.getcwd(), "params.txt")
            if not os.path.exists(default_params_path):
                default_params_path = get_resource_path("src/app/params.txt")
                
            with open(default_params_path, "r") as default_txt_file:
                default_params = default_txt_file.read()
            
            with open(txt_file_path, "w") as txt_file:
                txt_file.write(default_params)
        
        # 读取并应用参数
        with open(txt_file_path, 'r') as txt_file:
            self.MySliders.resetParams(eval(txt_file.read()))



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
            
            # 启用所有模式按钮
            self.default_btn.setEnabled(True)
            self.folder_btn.setEnabled(True)
            self.file_btn.setEnabled(True)
            
            # 三个按钮都不选中
            self.default_btn.setChecked(False)
            self.folder_btn.setChecked(False)
            self.file_btn.setChecked(False)
            
            # 更新save和reset按钮的可用性
            self.updateSaveResetButtonsState()
            self.showParams()

            dir_name = os.path.basename(os.path.dirname(self.file_path))
            base_name = os.path.basename(self.file_path)
            self.setWindowTitle(f"Praditor - {dir_name}/{base_name} ({self.which_one+1}/{len(self.file_paths)})")

            self.showXsetNum()
            self.param_sets.append(self.MySliders.getParams())

        else:
            print("Empty folder")


    def showXsetNum(self):

        if not self.AudioViewer.tg_dict_tp['onset']:
            self.run_onset.setText("Onset")
        else:
            self.run_onset.setText(f"Onset: {len(self.AudioViewer.tg_dict_tp['onset'])}")

        if not self.AudioViewer.tg_dict_tp['offset']:
            self.run_offset.setText("Offset")
        else:
            self.run_offset.setText(f"Offset: {len(self.AudioViewer.tg_dict_tp['offset'])}")

    def browseInstruction(self):
        # 使用webbrowser模块打开默认浏览器并导航到指定网址
        webbrowser.open('https://github.com/Paradeluxe/Praditor?tab=readme-ov-file#how-to-use-praditor')

    def runPraditorOnAudio(self):
        # 检查采样率
        # print(self.AudioViewer.audio_samplerate)
        # print(self.MySliders.cutoff1_slider_onset.value_label.text())
        if float(self.MySliders.cutoff1_slider_onset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2 or \
            float(self.MySliders.cutoff1_slider_offset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2:

            popup_window = QMessageBox()
            # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
            popup_window.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.png')))
            popup_window.setText(f"LowPass exceeds the Nyquist frequency boundary {float(self.AudioViewer.audio_samplerate)/2:.0f}")
            popup_window.exec()



        if not self.run_onset.isChecked():
            try:
                self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["onset"])
            except KeyError:
                pass
            self.AudioViewer.tg_dict_tp["onset"] = runPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "onset")
        else:
            self.AudioViewer.tg_dict_tp["onset"] = []

        if not self.run_offset.isChecked():
            try:
                self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["offset"])
            except KeyError:
                pass
            self.AudioViewer.tg_dict_tp["offset"] = runPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "offset")
        else:
            self.AudioViewer.tg_dict_tp["offset"] = []

        create_textgrid_with_time_point(self.file_path, self.AudioViewer.tg_dict_tp["onset"], self.AudioViewer.tg_dict_tp["offset"])
        self.readXset()
        self.showXsetNum()
        self.update_current_param()


    def testPraditorOnAudio(self):
        if float(self.MySliders.cutoff1_slider_onset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2 or \
            float(self.MySliders.cutoff1_slider_offset.value_label.text()) >= float(self.AudioViewer.audio_samplerate)/2:

            popup_window = QMessageBox()
            # popup_window.setWindowIcon(QMessageBox.Icon.Warning)
            popup_window.setWindowIcon(QIcon(get_resource_path('resources/icons/icon.png')))
            popup_window.setText(f"LowPass exceeds the Nyquist frequency boundary {float(self.AudioViewer.audio_samplerate)/2:.0f}")
            popup_window.exec()


        _test_tg_dict_tp = {"onset": [], "offset": []}
        if not self.run_onset.isChecked():
            _test_tg_dict_tp["onset"] = runPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "onset")
        else:
            _test_tg_dict_tp["onset"] = []

        if not self.run_offset.isChecked():
            _test_tg_dict_tp["offset"] = runPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "offset")
        else:
            _test_tg_dict_tp["offset"] = []
        


        if not _test_tg_dict_tp['onset']:
            self.run_onset.setText("Onset")
        else:
            self.run_onset.setText(f"Onset: {len(_test_tg_dict_tp['onset'])} ?")

        if not _test_tg_dict_tp['offset']:
            self.run_offset.setText("Offset")
        else:
            self.run_offset.setText(f"Offset: {len(_test_tg_dict_tp['offset'])} ?")



        # self.update_current_param()


    def update_current_param(self):
        current_params = self.MySliders.getParams()
        
        # 如果当前参数已经在列表中，移除它
        if current_params in self.param_sets:
            self.param_sets.remove(current_params)
        
        # 添加到列表末尾
        self.param_sets.append(current_params)
        
        # 限制最多保存10套参数
        if len(self.param_sets) > 10:
            self.param_sets = self.param_sets[-10:]
        
        # 更新当前索引为最后一个
        self.current_param_index = len(self.param_sets) - 1
        self.updateParamIndexLabel()
    
    def loadPreviousParams(self):
        """加载前一套参数"""
        if self.param_sets and self.current_param_index > 0:
            self.current_param_index -= 1
            self.MySliders.resetParams(self.param_sets[self.current_param_index])
            self.updateParamIndexLabel()
            print(f"Loaded previous params (index: {self.current_param_index})")
    
    def loadNextParams(self):
        """加载后一套参数"""
        if self.param_sets and self.current_param_index < len(self.param_sets) - 1:
            self.current_param_index += 1
            self.MySliders.resetParams(self.param_sets[self.current_param_index])
            self.updateParamIndexLabel()
            print(f"Loaded next params (index: {self.current_param_index})")
    
    def updateParamIndexLabel(self):
        """更新参数索引标签"""
        if hasattr(self, 'param_index_label'):
            # 当前索引从1开始显示，最多10套
            display_index = self.current_param_index + 1 if self.param_sets else 0
            total_count = len(self.param_sets) if self.param_sets else 0
            self.param_index_label.setText(f"{display_index}/{min(total_count, 10)}")
    
    def updateSaveResetButtonsState(self):
        """根据模式按钮的选中状态更新save和reset按钮的可用性和样式
        当三个模式按钮都未选中时，禁用save和reset按钮并将文字变为灰色
        """
        # 检查是否有任何模式按钮被选中
        any_mode_selected = self.default_btn.isChecked() or self.folder_btn.isChecked() or self.file_btn.isChecked()
        
        # 定义启用和禁用状态的样式
        enabled_style = "background-color: white; border: none; color: #333333; font-size: 13px; text-align: center; padding: 0; margin: 0 10px;"
        disabled_style = "background-color: white; border: none; color: #CCCCCC; font-size: 13px; text-align: center; padding: 0; margin: 0 10px;"
        
        # 更新save按钮
        self.save_btn.setEnabled(any_mode_selected)
        self.save_btn.setStyleSheet(enabled_style if any_mode_selected else disabled_style)
        
        # 更新reset按钮
        self.reset_svg_btn.setEnabled(any_mode_selected)
        self.reset_svg_btn.setStyleSheet(enabled_style if any_mode_selected else disabled_style)
    
    def onModeButtonClicked(self):
        """模式按钮点击事件处理，确保单选效果
        当点击一个按钮时，确保它是唯一选中的，除非是取消选中
        """
        sender = self.sender()
        
        # 如果点击的按钮当前是选中状态，取消选中
        if sender.isChecked():
            # 取消其他两个按钮的选中状态
            for btn in [self.default_btn, self.folder_btn, self.file_btn]:
                if btn != sender:
                    btn.setChecked(False)
        
        # 更新save和reset按钮状态
        self.updateSaveResetButtonsState()



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
        self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path)
        
        # 启用所有模式按钮
        self.default_btn.setEnabled(True)
        self.folder_btn.setEnabled(True)
        self.file_btn.setEnabled(True)
        
        # 三个按钮都不选中
        self.default_btn.setChecked(False)
        self.folder_btn.setChecked(False)
        self.file_btn.setChecked(False)
        
        # 更新save和reset按钮的可用性
        self.updateSaveResetButtonsState()
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
    
    def saveParamsWithFolderName(self):
        """保存参数到当前文件夹，文件名与文件夹同名"""
        if hasattr(self, 'file_path') and self.file_path:
            folder_path = os.path.dirname(self.file_path)
            folder_name = os.path.basename(folder_path)
            txt_file_path = os.path.join(folder_path, f"{folder_name}.txt")
            
            with open(txt_file_path, 'w') as txt_file:
                txt_file.write(f"{self.MySliders.getParams()}")
            print(f"Params saved to folder with name: {txt_file_path}")
    
    def saveParamsToExeLocation(self):
        """保存参数到exe所在位置"""
        # 获取当前脚本所在目录（相当于exe所在位置）
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        txt_file_path = os.path.join(exe_dir, "params.txt")
        
        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(f"{self.MySliders.getParams()}")
        print(f"Params saved to exe location: {txt_file_path}")
    
    def saveParamsWithFileName(self):
        """保存参数到file同名"""
        if hasattr(self, 'file_path') and self.file_path:
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
            
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
        
        # 填充主窗口背景
        main_rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(main_rect, radius, radius)
        painter.fillPath(path, background_color)
        
        # 调用父类的paintEvent确保其他部件正常绘制
        super().paintEvent(event)




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
