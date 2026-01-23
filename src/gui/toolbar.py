from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtWidgets import (QGridLayout, QApplication, QMainWindow, QWidget, QLabel, QToolBar, 
                               QPushButton, QSizePolicy)
from PySide6.QtGui import QIcon, QCursor
from src.utils.resources import get_resource_path
from src.gui.styles import qss_save_location_button, qss_button_small_black


# 自定义QLabel类，实现hover时文字自动滑动效果
class ScrollingLabel(QLabel):
    """自定义QLabel类，实现hover时文字自动滑动效果"""
    def __init__(self, parent=None):
        """初始化滚动标签
        
        Args:
            parent: 父窗口部件
        """
        super().__init__(parent)
        self.setMouseTracking(True)
        self.original_text = ""
        self.scroll_offset = 0
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_text)
        self.scroll_speed = 5  # 滚动速度（像素/帧）
        self.scroll_delay = 50  # 滚动延迟（毫秒/帧）
        self.scroll_pause = 1000  # 滚动暂停时间（毫秒）
        self.is_hovered = False  # 鼠标悬停状态标记
        
    def setText(self, text):
        """设置标签文本，并保存原始文本用于滚动
        
        Args:
            text: 要显示的文本
        """
        self.original_text = text
        super().setText(text)
        
    def enterEvent(self, event):
        """鼠标进入事件处理
        
        当鼠标悬停时，开始滚动文本（如果文本长度超过标签宽度）
        
        Args:
            event: 鼠标事件对象
        """
        # 鼠标悬停时开始滚动
        self.is_hovered = True
        if self.text() and self.fontMetrics().boundingRect(self.text()).width() > self.width():
            # 等待1秒后开始滚动
            QTimer.singleShot(1000, self.start_scrolling)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件处理
        
        当鼠标离开时，停止滚动并重置文本位置
        
        Args:
            event: 鼠标事件对象
        """
        # 鼠标离开时停止滚动并重置
        self.is_hovered = False
        self.stop_scrolling()
        self.reset_scroll()
        super().leaveEvent(event)
        
    def start_scrolling(self):
        """开始文本滚动
        
        启动滚动计时器，触发scroll_text方法
        """
        self.scroll_timer.start(self.scroll_delay)
        
    def stop_scrolling(self):
        """停止文本滚动
        
        停止滚动计时器
        """
        self.scroll_timer.stop()
        
    def reset_scroll(self):
        """重置滚动位置
        
        将滚动偏移量重置为0，并恢复原始文本显示
        """
        self.scroll_offset = 0
        super().setText(self.original_text)
        
    def restart_scrolling(self):
        """重新开始文本滚动
        
        只有在鼠标悬停时才重新开始滚动
        """
        # 只有在鼠标悬停时才重新开始滚动
        if not self.is_hovered:
            return
            
        # 重置滚动偏移量
        self.scroll_offset = 0  # 从0开始，确保滚动重新开始
        # 开始滚动前停留1秒
        QTimer.singleShot(1500, self.start_scrolling)
        
    def scroll_text(self):
        """执行文本滚动逻辑
        
        根据滚动偏移量计算当前应该显示的文本部分，并更新标签显示
        """
        if not self.original_text:
            return
            
        # 获取完整文本的宽度
        text_width = self.fontMetrics().boundingRect(self.original_text).width()
        # 获取标签的实际宽度（减去内边距）
        label_width = self.width() - 16  # 减去左右内边距各8px
        
        # 如果文本宽度小于等于标签宽度，不需要滚动
        if text_width <= label_width:
            return
            
        # 计算滚动偏移
        self.scroll_offset += self.scroll_speed
        
        # 检查是否达到最大偏移量（当文字右侧触碰到标签右侧时）
        # 当滚动偏移量等于文本宽度减去标签宽度时，文字右侧刚好触碰到标签右侧
        max_scroll_offset = text_width - label_width
        
        if self.scroll_offset >= max_scroll_offset:
            # 停止当前滚动，保持当前显示的文本（文字右侧触碰到标签右侧的状态）
            self.stop_scrolling()
            # 滚完那一刻停留1.5秒
            QTimer.singleShot(1500, self.restart_scrolling_from_beginning)
            return
            
        # 计算当前应该显示的文本
        # 使用QLabel的setText方法配合QLabel的对齐方式来实现滚动效果
        # 这里我们使用QFontMetrics来计算需要显示的文本
        
        # 计算当前应该显示的文本起始位置
        # 我们需要显示从scroll_offset开始的文本，长度为label_width
        start_index = 0
        current_offset = 0
        
        # 找到与当前滚动偏移量对应的字符索引
        while start_index < len(self.original_text) and current_offset < self.scroll_offset:
            char_width = self.fontMetrics().boundingRect(self.original_text[start_index]).width()
            current_offset += char_width
            start_index += 1
        
        # 确保起始索引不超出范围
        start_index = min(start_index, len(self.original_text))
        
        # 从起始索引开始，截取能填满标签宽度的文本
        display_text = ""
        temp_width = 0
        
        for char in self.original_text[start_index:]:
            char_width = self.fontMetrics().boundingRect(char).width()
            if temp_width + char_width <= label_width:
                display_text += char
                temp_width += char_width
            else:
                break
        
        # 确保至少显示一个字符
        if not display_text and self.original_text:
            display_text = self.original_text[0]
        
        super().setText(display_text)
        
    def restart_scrolling_from_beginning(self):
        """从开头重新开始滚动
        
        重置滚动偏移量，恢复原始文本，然后开始滚动
        """
        # 重置滚动偏移量
        self.scroll_offset = 0
        # 恢复显示原始文本
        super().setText(self.original_text)
        # 开始滚动前停留1秒
        QTimer.singleShot(1000, self.start_scrolling)


class CustomToolBar(QToolBar):
    """自定义工具栏类，包含各种控制按钮和状态显示"""
    # 定义信号
    default_btn_clicked = Signal()
    folder_btn_clicked = Signal()
    file_btn_clicked = Signal()
    save_btn_clicked = Signal()
    reset_btn_clicked = Signal()
    backward_btn_clicked = Signal()
    forward_btn_clicked = Signal()
    vad_btn_clicked = Signal()
    
    def __init__(self, parent=None):
        """初始化自定义工具栏
        
        Args:
            parent: 父窗口部件
        """
        super().__init__("My main toolbar", parent)
        
        self.setMovable(False)
        self.setStyleSheet("""
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
        
        # 用于保存按钮状态的字典
        self._button_states = {}
        
        # 所有需要管理状态的按钮列表
        self._all_buttons = []
        
        # 添加自定义长度的spacer到最左侧
        left_spacer = QWidget()
        left_spacer.setFixedWidth(10)
        self.addWidget(left_spacer)
        
        # Default按钮
        self.default_btn = QPushButton("Default", self)
        self.default_btn.setCheckable(True)
        self.default_btn.setChecked(False)
        self.default_btn.setEnabled(False)
        self.default_btn.setStyleSheet(qss_save_location_button)
        self.default_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.default_btn.setToolTip("Use default parameters")
        self.default_btn.clicked.connect(self.default_btn_clicked)
        self.addWidget(self.default_btn)
        self._all_buttons.append(self.default_btn)
        
        # Folder按钮
        self.folder_btn = QPushButton("Folder", self)
        self.folder_btn.setCheckable(True)
        self.folder_btn.setStyleSheet(qss_save_location_button)
        self.folder_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.folder_btn.setEnabled(False)
        self.folder_btn.setToolTip("Use folder-specific parameters")
        self.folder_btn.clicked.connect(self.folder_btn_clicked)
        self.addWidget(self.folder_btn)
        self._all_buttons.append(self.folder_btn)
        
        # File按钮
        self.file_btn = QPushButton("File", self)
        self.file_btn.setCheckable(True)
        self.file_btn.setStyleSheet(qss_save_location_button)
        self.file_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.file_btn.setEnabled(False)
        self.file_btn.setToolTip("Use file-specific parameters")
        self.file_btn.clicked.connect(self.file_btn_clicked)
        self.addWidget(self.file_btn)
        self._all_buttons.append(self.file_btn)
                
        self.addSeparator()
        
        # 保存按钮
        self.save_btn = QPushButton("Save", self)
        self.save_btn.setIcon(QIcon(get_resource_path('resources/icons/save.svg')))
        self.save_btn.setToolTip("Save parameters to selected location")
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
            QPushButton:hover {
                background-color: #F0F0F0; 
            }
        """)
        self.save_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_btn.setEnabled(False)  # 初始禁用
        self.save_btn.clicked.connect(self.save_btn_clicked)
        self.addWidget(self.save_btn)
        self._all_buttons.append(self.save_btn)
        
        # Reset按钮
        self.reset_btn = QPushButton("Reset", self)
        self.reset_btn.setIcon(QIcon(get_resource_path('resources/icons/reset.svg')))
        self.reset_btn.setToolTip("Reset parameters to saved values")
        self.reset_btn.setStyleSheet("""
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
            QPushButton:hover {
                background-color: #F0F0F0; 
                border: none; 
                color: #333333; 
                font-size: 13px; 
                text-align: center; 
                padding: 8px 12px; 
                margin: 0;
            }
        """)
        self.reset_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.reset_btn.setEnabled(False)  # 初始禁用
        self.reset_btn.clicked.connect(self.reset_btn_clicked)
        self.addWidget(self.reset_btn)
        self._all_buttons.append(self.reset_btn)

        
        # Backward按钮
        self.backward_btn = QPushButton("Backward", self)
        self.backward_btn.setIcon(QIcon(get_resource_path('resources/icons/backward.svg')))
        self.backward_btn.setToolTip("Load previous parameters")
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
            QPushButton:hover {
                background-color: #F0F0F0; 
                border: none; 
                color: #333333; 
                font-size: 13px; 
                text-align: center; 
                padding: 8px 12px; 
                margin: 0;
            }
        """)
        self.backward_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.backward_btn.setEnabled(False)  # 初始禁用
        self.backward_btn.clicked.connect(self.backward_btn_clicked)
        self.addWidget(self.backward_btn)
        self._all_buttons.append(self.backward_btn)
        
        # Forward按钮
        self.forward_btn = QPushButton("Forward", self)
        self.forward_btn.setIcon(QIcon(get_resource_path('resources/icons/forward.svg')))
        self.forward_btn.setToolTip("Load next parameters")
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
            QPushButton:hover {
                background-color: #F0F0F0; 
                border: none; 
                color: #333333; 
                font-size: 13px; 
                text-align: center; 
                padding: 8px 12px; 
                margin: 0;
            }
        """)
        self.forward_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.forward_btn.setEnabled(False)  # 初始禁用
        self.forward_btn.clicked.connect(self.forward_btn_clicked)
        self.addWidget(self.forward_btn)
        self._all_buttons.append(self.forward_btn)
        
        # 添加伸缩空间，将参数索引标签推到右侧
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)
        
        # 添加VAD切换按钮
        self.vad_btn = QPushButton("VAD", self)
        self.vad_btn.setCheckable(True)
        self.vad_btn.setChecked(False)
        self.vad_btn.setStyleSheet(qss_button_small_black)
        self.vad_btn.setFixedHeight(25)
        self.vad_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.vad_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.vad_btn.setToolTip("Toggle VAD mode")
        self.vad_btn.setEnabled(False)  # 初始禁用
        self.vad_btn.clicked.connect(self.vad_btn_clicked)
        self.addWidget(self.vad_btn)
        self._all_buttons.append(self.vad_btn)
        
        # 添加spacer增加VAD按钮和output label之间的距离
        vad_output_spacer = QWidget()
        vad_output_spacer.setFixedWidth(15)  # 设置固定宽度为15px
        self.addWidget(vad_output_spacer)
        
        # 添加print输出显示label
        self.print_label = ScrollingLabel(self)
        self.print_label.setText("Print output: ")
        self.print_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 12px;
                border: 1px solid #E9EDF1;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: #F8F9FA;
            }
        """)
        self.print_label.setToolTip("Displays the most recent print output")
        # 固定output label的长度
        self.print_label.setFixedWidth(350)  # 固定宽度为350px
        self.print_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.print_label.setTextFormat(Qt.PlainText)
        self.addWidget(self.print_label)
        
        # 合并参数图标和索引标签为一个按钮
        self.params_btn = QPushButton(self)
        self.params_btn.setIcon(QIcon(get_resource_path('resources/icons/parameters.svg')))
        self.params_btn.setText("0/0")
        self.params_btn.setFixedHeight(24)
        self.params_btn.setToolTip("Parameters index")
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
        self.params_btn.setCursor(QCursor(Qt.ArrowCursor))
        self.addWidget(self.params_btn)
        self._all_buttons.append(self.params_btn)
        
        # 添加自定义长度的spacer到最右侧
        right_spacer = QWidget()
        right_spacer.setFixedWidth(8)  # 自定义宽度为8px
        self.addWidget(right_spacer)
        
    def updateParamsIndex(self, current, total):
        """更新参数索引显示
        
        Args:
            current: 当前参数索引
            total: 总参数数量
        """
        self.params_btn.setText(f"{current}/{total}")
        
    def updatePrintOutput(self, text):
        """更新打印输出显示
        
        Args:
            text: 要显示的打印输出文本
        """
        self.print_label.setText(f"{text}")
        
    def updateButtonStates(self, any_mode_selected, reset_enabled, backward_enabled, forward_enabled):
        """更新按钮状态和图标
        
        Args:
            any_mode_selected: 是否有任何模式按钮被选中
            reset_enabled: 重置按钮是否可用
            backward_enabled: 后退按钮是否可用
            forward_enabled: 前进按钮是否可用
        """
        # 更新保存按钮图标
        self.save_btn.setIcon(QIcon(get_resource_path(f'resources/icons/save{"_gray" if not any_mode_selected else ""}.svg')))
        # 更新重置按钮图标
        self.reset_btn.setIcon(QIcon(get_resource_path(f'resources/icons/reset{"_gray" if not reset_enabled else ""}.svg')))
        # 更新后退按钮图标
        self.backward_btn.setIcon(QIcon(get_resource_path(f'resources/icons/backward{"_gray" if not backward_enabled else ""}.svg')))
        # 更新前进按钮图标
        self.forward_btn.setIcon(QIcon(get_resource_path(f'resources/icons/forward{"_gray" if not forward_enabled else ""}.svg')))

    def setEnabled(self, enabled):
        """设置工具栏所有按钮的启用状态
        
        Args:
            enabled: 是否启用工具栏按钮
        """
        if not enabled:
            # 保存所有按钮的当前状态
            self._button_states.clear()
            for btn in self._all_buttons:
                self._button_states[btn] = {
                    'isEnabled': btn.isEnabled(),
                    'isChecked': btn.isChecked()
                }
            # 禁用所有按钮
            for btn in self._all_buttons:
                btn.setEnabled(False)
        else:
            # 按保存的按钮状态逐个恢复
            for btn, state in self._button_states.items():
                btn.setEnabled(state['isEnabled'])
                btn.setChecked(state['isChecked'])
