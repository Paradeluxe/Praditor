from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QSizePolicy, 
                               QLabel, QSpacerItem)
from PySide6.QtGui import QIcon, QCursor
from src.utils.resources import get_resource_path


class CustomTitleBar(QWidget):
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
        self.help_menu_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.help_menu_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.help_menu_btn.setToolTip("Open help documentation")
        
        # 连接菜单按钮信号
        self.help_menu_btn.clicked.connect(self.help_menu_clicked.emit)
        
        # 添加设置按钮到布局左侧
        layout.addWidget(self.help_menu_btn)
        
        # 添加标题按钮，设置居左显示（Windows风格）
        self.title_label = QPushButton("Praditor")
        self.title_label.setFlat(True)
        self.title_label.setFocusPolicy(Qt.NoFocus)
        self.title_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.title_label.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: #333333; 
                font-size: 13px; 
                font-weight: bold; 
                border: none; 
                padding: 5px 10px 5px 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: transparent; 
            }
            QPushButton:pressed {
                background-color: transparent; 
            }
        """)
        self.title_label.setToolTip("Select an audio file")
        self.title_label.clicked.connect(self.file_menu_clicked.emit)
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
        self.prev_audio_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.prev_audio_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.prev_audio_btn.setToolTip("Previous Audio")
        self.prev_audio_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.prev_audio_btn)
        
        # 添加后一个音频按钮
        self.next_audio_btn = QPushButton()
        self.next_audio_btn.setIcon(QIcon(get_resource_path('resources/icons/next_audio.svg')))
        self.next_audio_btn.setFixedSize(32, 32)
        self.next_audio_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.next_audio_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_audio_btn.setToolTip("Next Audio")
        self.next_audio_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.next_audio_btn)


        layout.addSpacing(8)  # 添加按钮之间的空格


        # 添加onset和offset按钮
        self.onset_btn = QPushButton("Onset")
        self.onset_btn.setFixedSize(80, 25)
        onset_color = "#1991D3"
        self.onset_btn.setStyleSheet(f"QPushButton {{ background: {onset_color}; color: white; font-weight: bold; border: 2px solid {onset_color}; border-radius: 5px; margin: 0px; font-size: 13px; }} QPushButton:pressed {{ background: #666666; color: {onset_color}; font-weight: bold; border: 2px solid {onset_color}; border-radius: 5px; margin: 0px; }} QPushButton:checked {{ background-color: white; color: {onset_color}; border: 2px solid {onset_color}; font-weight: bold; border-radius: 5px; margin: 0px; }}")
        self.onset_btn.setCheckable(True)
        self.onset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.onset_btn.setToolTip("Extract Onsets")
        self.onset_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.onset_btn)
        
        layout.addSpacing(8)
        
        self.offset_btn = QPushButton("Offset")
        self.offset_btn.setFixedSize(80, 25)
        offset_color = "#2AD25E"
        self.offset_btn.setStyleSheet(f"QPushButton {{ background: {offset_color}; color: white; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; font-size: 13px; }} QPushButton:pressed {{ background: #666666; color: {offset_color}; font-weight: bold; border: 2px solid {offset_color}; border-radius: 5px; margin: 0px; }} QPushButton:checked {{ background-color: white; color: {offset_color}; border: 2px solid {offset_color}; font-weight: bold; border-radius: 5px; margin: 0px; }}")
        self.offset_btn.setCheckable(True)
        self.offset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.offset_btn.setToolTip("Extract Offsets")
        self.offset_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.offset_btn)
        
        layout.addSpacing(8)  # 添加按钮之间的空格
        
        # 连接onset和offset按钮信号
        self.onset_btn.pressed.connect(self.onset_signal.emit)
        self.offset_btn.pressed.connect(self.offset_signal.emit)
        
        # 添加trash按钮（用于清除onsets和offsets）
        self.trash_btn = QPushButton()
        self.trash_btn.setIcon(QIcon(get_resource_path('resources/icons/trash.svg')))
        self.trash_btn.setFixedSize(32, 32)
        self.trash_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.trash_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.trash_btn.setToolTip("Clear onsets and offsets")
        self.trash_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.trash_btn)
        
        # 添加read按钮（用于显示onsets和offsets）
        self.read_btn = QPushButton()
        self.read_btn.setIcon(QIcon(get_resource_path('resources/icons/read.svg')))
        self.read_btn.setFixedSize(32, 32)
        self.read_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.read_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.read_btn.setToolTip("Display onsets and offsets")
        self.read_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.read_btn)
        
        # 添加运行按钮（类似IDE中的播放键）
        self.run_btn = QPushButton()
        self.run_btn.setIcon(QIcon(get_resource_path('resources/icons/play.svg')))
        self.run_btn.setFixedSize(32, 32)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.run_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.run_btn.setToolTip("Run Praditor on audio")
        self.run_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.run_btn)
        
        # 添加run-all按钮
        self.run_all_btn = QPushButton()
        self.run_all_btn.setIcon(QIcon(get_resource_path('resources/icons/run-all.svg')))
        self.run_all_btn.setFixedSize(32, 32)
        self.run_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.run_all_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.run_all_btn.setToolTip("Run Praditor on all audio files")
        self.run_all_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.run_all_btn)
        
        # 添加停止按钮
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon(get_resource_path('resources/icons/stop.svg')))
        self.stop_btn.setFixedSize(32, 32)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.stop_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.stop_btn.setToolTip("Stop Praditor detection")
        self.stop_btn.setEnabled(False)  # 初始禁用，只有在运行时才启用
        layout.addWidget(self.stop_btn)
        
        # 添加测试按钮
        self.test_btn = QPushButton()
        self.test_btn.setIcon(QIcon(get_resource_path('resources/icons/test.svg')))
        self.test_btn.setFixedSize(32, 32)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.test_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.test_btn.setToolTip("Test Praditor on audio")
        self.test_btn.setEnabled(False)  # 初始禁用
        layout.addWidget(self.test_btn)

        layout.addSpacing(8)  # 添加按钮之间的空格

        # 添加最小化按钮
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(QIcon(get_resource_path('resources/icons/minimize.svg')))
        self.minimize_btn.setFixedSize(32, 32)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.minimize_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.minimize_btn.setToolTip("Minimize window")
        layout.addWidget(self.minimize_btn)
        
        # 添加最大化按钮
        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(QIcon(get_resource_path('resources/icons/maximize.svg')))
        self.maximize_btn.setFixedSize(32, 32)
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E8E8E8; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.maximize_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.maximize_btn.setToolTip("Maximize window")
        layout.addWidget(self.maximize_btn)
        
        # 添加关闭按钮
        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon(get_resource_path('resources/icons/close.svg')))
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                border: none; 
                color: #333333; 
                font-size: 16px; 
                text-align: center;
            }
            QPushButton:hover {
                background-color: #FF6969; 
                border: none; 
                color: white; 
                font-size: 16px; 
                text-align: center;
            }
        """)
        self.close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_btn.setToolTip("Close window")
        layout.addWidget(self.close_btn)
        
        # 连接信号
        self.close_btn.clicked.connect(self.close_signal.emit)
        self.minimize_btn.clicked.connect(self.minimize_signal.emit)
        self.maximize_btn.clicked.connect(self.maximize_signal.emit)
        self.prev_audio_btn.clicked.connect(self.prev_audio_signal.emit)
        self.next_audio_btn.clicked.connect(self.next_audio_signal.emit)
        self.trash_btn.clicked.connect(self.trash_signal.emit)
        self.read_btn.clicked.connect(self.read_signal.emit)
        self.run_btn.clicked.connect(self.run_signal.emit)
        self.run_all_btn.clicked.connect(self.run_all_signal.emit)
        self.stop_btn.clicked.connect(self.stop_signal.emit)
        self.test_btn.clicked.connect(self.test_signal.emit)
        
        
    def mousePressEvent(self, event):
        """鼠标按下事件，用于拖拽窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent().frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，用于拖拽窗口"""
        if event.buttons() == Qt.LeftButton and self.drag_position != QPoint():
            self.parent().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件，结束拖拽"""
        self.drag_position = QPoint()
        event.accept()
    
    def set_title(self, title):
        """设置标题，确保Praditor部分加粗"""
        self.title_label.setText(title)
    
    def setButtonsEnabled(self, enabled):
        """设置按钮是否可用
        
        Args:
            enabled: 是否启用按钮
        """
        # 根据需要实现按钮启用/禁用逻辑
        pass
        
    def setIsRunning(self, is_running):
        """设置is_running状态，控制除stop、min、max、close之外的所有按钮"""
        # 收集所有需要管理的按钮
        buttons_to_manage = [
            self.help_menu_btn,
            self.title_label,
            self.prev_audio_btn,
            self.next_audio_btn,
            self.onset_btn,
            self.offset_btn,
            self.trash_btn,
            self.read_btn,
            self.run_btn,
            self.run_all_btn,
            self.test_btn
        ]
        
        for btn in buttons_to_manage:
            btn.setEnabled(not is_running)
        
        # 确保stop按钮在运行时可用
        self.stop_btn.setEnabled(is_running)
