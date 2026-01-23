import ctypes
import os
import sys
import webbrowser
import io

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.logger import system_logger, player_logger, params_logger, file_logger

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
from src.core.detection import detectPraditor, create_textgrid_with_time_point, stop_flag, segment_audio
from src.gui.plots import AudioViewer
from src.gui.sliders import MySliders
from src.gui.toolbar import CustomToolBar
from src.gui.titlebar import CustomTitleBar
from src.utils.audio import isAudioFile, get_frm_points_from_textgrid, get_frm_intervals_from_textgrid
from src.utils.resources import get_resource_path



class ConsoleOutput(io.StringIO):  # 自定义输出流类，用于捕获print语句和logger输出
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



class DetectPraditorThread(QThread):  # 异步检测任务类
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
                system_logger.warning("Termination timed out")

        system_logger.info("Thread terminated")
        
    
    def run(self):
        from src.core import detection
        try:

            onset_results, offset_results = [], []

            system_logger.info("Segmenting...")  # 记录开始分段日志
            count = 0
            segments = segment_audio(self.audio_obj, segment_duration=15, params=self.params, min_pause=1, mode="vad")
            system_logger.info(f"Total segments: {len(segments)}")  # 记录总分段数
            for start, end in segments:

                # 设置全局停止标志
                from src.core import detection
                if detection.stop_flag:
                    break


                count += 1

                # 记录当前进度百分比
                progress = int((count / len(segments)) * 100)
                system_logger.info(f"Detection progress: {progress:.0f}%")
                clip_onset_results, clip_offset_results = [], []

                audio_clip = self.audio_obj[start:end]


                if self.params["onset"]:
                    clip_onset_results = detectPraditor(self.params, audio_clip, "onset", self.mode)
                    clip_onset_results = [x + start/1000 for x in clip_onset_results]


                if self.params["offset"]:
                    clip_offset_results = detectPraditor(self.params, audio_clip, "offset", self.mode)
                    clip_offset_results = [x + start/1000 for x in clip_offset_results]

                # 合并当前片段的结果
                onset_results.extend(clip_onset_results)
                offset_results.extend(clip_offset_results)


            self.finished.emit(onset_results, offset_results)


            
        except Exception as e:
            if not detection.stop_flag:
                system_logger.error(f"Error: {e}")
                self.finished.emit([], [])


   


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
        self.setMinimumSize(1200, 800)
        
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
        
        # 连接媒体状态变化信号
        self.player.mediaStatusChanged.connect(self.onMediaStatusChanged)



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

        
        # 使用自定义工具栏
        self.toolbar = CustomToolBar(self)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        # ---------------------------------------------------------------
        # 连接工具栏按钮信号
        self.toolbar.save_btn.clicked.connect(self.saveParams)
        self.toolbar.reset_btn.clicked.connect(self.resetParams)
        self.toolbar.backward_btn.clicked.connect(self.loadPreviousParams)
        self.toolbar.forward_btn.clicked.connect(self.loadNextParams)
        self.toolbar.vad_btn.clicked.connect(self.onVadButtonClicked)
        # 连接模式按钮信号
        self.toolbar.default_btn.clicked.connect(lambda: self.onModeButtonClicked(self.toolbar.default_btn))
        self.toolbar.folder_btn.clicked.connect(lambda: self.onModeButtonClicked(self.toolbar.folder_btn))
        self.toolbar.file_btn.clicked.connect(lambda: self.onModeButtonClicked(self.toolbar.file_btn))
        # 初始化输出流，将print语句重定向到GUI
        def update_print_label(text):
            # 更新print_label的文本，仅显示最后一行
            self.toolbar.print_label.setText(f"{text}")
        
        # 将update_print_label函数设置为logger的GUI回调
        from src.utils.logger import gui_callback as logger_gui_callback
        from src.utils.logger import gui_callback
        import src.utils.logger
        src.utils.logger.gui_callback = update_print_label
        
        # 创建输出流实例
        self.console_output = ConsoleOutput(update_print_label)
        # 保存原始stdout
        self.original_stdout = sys.stdout
        # 重定向stdout到自定义输出流
        sys.stdout = self.console_output
        
        # 测试print输出功能
        system_logger.info("Praditor started successfully!")
        
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
        self.toolbar.default_btn.clicked.connect(lambda: self.onModeButtonClicked(self.toolbar.default_btn))
        self.toolbar.folder_btn.clicked.connect(lambda: self.onModeButtonClicked(self.toolbar.folder_btn))
        self.toolbar.file_btn.clicked.connect(lambda: self.onModeButtonClicked(self.toolbar.file_btn))
        
        # 初始化时检查一次参数匹配，确保刚载入GUI时也能显示下划线
        self.checkIfParamsExist()
        
        # 初始化时更新save和reset按钮状态
        self.updateToolbarButtonsState()
        
    def onVadButtonClicked(self):
        """处理VAD按钮点击事件"""
        self.toggleVadMode(self.toolbar.vad_btn.isChecked())
    
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
        
        
        self.updateParamIndexLabel()  # 切换模式后更新参数索引标签，确保显示当前模式的参数
        
        self.showParams()  # 按照File→Folder→Default优先级加载参数
        
        self.checkIfParamsExist()  # 检查参数文件是否存在，更新按钮状态

        # 切换模式后，不选中任何按钮
        self.toolbar.default_btn.setChecked(False)
        self.toolbar.folder_btn.setChecked(False)
        self.toolbar.file_btn.setChecked(False)
        
        # 重新读取音频结果，根据当前模式选择不同的结果文件
        if hasattr(self, 'file_path') and self.file_path:
            self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=is_vad_enabled)
            self.showXsetNum(is_test=False)
        
        
        self.MySliders.updateTooltips(is_vad_enabled)  # 更新滑块的tooltip文本



    def keyPressEvent(self, event):
        """处理键盘按键事件，实现空格键或F5键控制音频播放/暂停
        
        Args:
            event: 键盘事件对象
        """

        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.playSound()
        else:
            if event.key() == Qt.Key_F5:
                self.playSound()

        super().keyPressEvent(event)

    def playSound(self):
        """控制音频播放/暂停
        
        如果音频正在播放则停止，否则开始播放当前打开的音频文件
        """
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.stop()  # 如果正在播放则暂停
            player_logger.info("Stop")
        else:
            self.player.setSource(QUrl.fromLocalFile(self.file_path))
            self.player.play()    # 开始/恢复播放
            player_logger.info("Playing...")

    def onMediaStatusChanged(self, status):
        """处理媒体状态变化事件
        
        Args:
            status: 媒体状态对象
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            player_logger.info("Playback finished")



    def readXset(self):
        """读取音频文件对应的TextGrid结果文件
        
        根据当前模式（普通/VAD）选择不同的结果文件格式
        """
        if self.toolbar.vad_btn.isChecked():
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
        """清除当前显示的检测结果
        
        根据当前选中的Onset/Offset按钮状态，清除对应的检测结果
        """
        if not self.run_onset.isChecked():
            self.AudioViewer.removeXset(self.AudioViewer.tg_dict_tp["onset"])
        if not self.run_offset.isChecked():
            self.AudioViewer.removeXset(self.AudioViewer.tg_dict_tp["offset"])
        self.AudioViewer.tg_dict_tp = {}



    def turnOnset(self):
        """切换Onset检测状态
        
        根据Onset按钮状态，更新滑块颜色、禁用状态和检测结果显示
        """
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
        """切换Offset检测状态
        
        根据Offset按钮状态，更新滑块颜色、禁用状态和检测结果显示
        """
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
        """重置参数到当前选中模式的默认值
        
        根据当前选中的模式（Default/Folder/File），从对应的参数文件中加载参数
        """
        # 由于按钮可以同时被选中，我们需要确定优先读取哪个位置的参数
        # 优先级：File > Folder > Default
        txt_file_path = None
        
        # 检查是否处于VAD模式
        is_vad_mode = self.toolbar.vad_btn.isChecked()
        file_suffix = "_vad" if is_vad_mode else ""
        
        if self.toolbar.file_btn.isChecked():
            # File模式：从file同名的txt文件读取
            txt_file_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
        elif self.toolbar.folder_btn.isChecked():
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
            params_logger.info(f"TXT file read from: {txt_file_path}")

        except FileNotFoundError:
            # 切换到Default模式
            self.toolbar.default_btn.setChecked(True)
            params_logger.info("Go back to Default mode")
            self.showParams()


    def saveParams(self):
        """保存当前参数到所有选中模式的参数文件
        
        根据当前选中的模式（Default/Folder/File），将参数保存到对应的文件中
        """
        # 检查每个按钮的状态，如果被选中就保存到相应位置
        if self.toolbar.default_btn.isChecked():
            # Default模式：保存到应用程序所在位置
            self.saveParamsToExeLocation()
        if self.toolbar.folder_btn.isChecked():
            # Folder模式：保存到当前文件夹，文件名与文件夹同名
            self.saveParamsWithFolderName()
        if self.toolbar.file_btn.isChecked():
            # File模式：保存到file同名
            self.saveParamsWithFileName()
        
        
        self.checkIfParamsExist()  # 保存参数后检查是否与任何模式匹配，更新下划线
        
        
        self.updateToolbarButtonsState()  # 更新工具栏按钮状态，确保Reset按钮在参数文件保存后显示为可用


    def checkIfParamsExist(self):
        """
        检查不同模式下的参数文件是否存在，以及当前参数是否与文件中保存的参数匹配
        
        该方法会检查三种模式的参数文件：
        1. Default模式：检查应用程序目录下的params.txt或params_vad.txt文件
        2. Folder模式：检查当前打开文件所在目录下的params.txt或params_vad.txt文件
        3. File模式：检查与当前打开文件同名的.txt参数文件
        
        同时会根据VAD模式状态，决定使用带_vad后缀的参数文件还是普通参数文件
        检查结果会通过按钮属性反映，用于UI样式显示（如按钮颜色变化）
        """
        # 获取当前滑块参数的字符串表示
        current_params = str(self.MySliders.getParams())
        # current_params_dict = self.MySliders.getParams()
        
        # 检查是否处于VAD模式，决定参数文件后缀
        is_vad_mode = self.toolbar.vad_btn.isChecked()
        file_suffix = "_vad" if is_vad_mode else ""
        
        # ======================== Default模式检查 ========================
        # 构建默认参数文件路径：首先检查当前目录，若不存在则检查资源路径
        default_params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"params{file_suffix}.txt")
        if not os.path.exists(default_params_path):
            default_params_path = get_resource_path(f"src/app/params{file_suffix}.txt")
        
        default_params_match = False  # 默认参数是否匹配
        if os.path.exists(default_params_path):
            try:
                with open(default_params_path, 'r') as txt_file:
                    # 读取并解析默认参数文件内容，转换为字符串进行比较
                    default_params = str(eval(txt_file.read()))
                    default_params_match = (current_params == default_params)
            except Exception as e:
                # 解析失败时忽略错误
                pass
        
        # 设置默认按钮的属性，用于样式显示（如文件存在状态和参数匹配状态）
        self.toolbar.default_btn.setProperty("file_exists", os.path.exists(default_params_path))
        self.toolbar.default_btn.setProperty("param_matched", default_params_match)
        self.toolbar.default_btn.style().polish(self.toolbar.default_btn)  # 刷新按钮样式，应用新属性
        
        # ======================== Folder模式检查 ========================
        folder_params_exists = False  # 文件夹参数文件是否存在
        folder_params_match = False  # 文件夹参数是否与当前参数匹配
        if self.file_path:  # 仅当有打开文件时才检查
            folder_path = os.path.dirname(self.file_path)  # 获取当前文件所在文件夹
            folder_params_path = os.path.join(folder_path, f"params{file_suffix}.txt")  # 构建文件夹参数文件路径
            
            if os.path.exists(folder_params_path):
                folder_params_exists = True
                try:
                    with open(folder_params_path, 'r') as txt_file:
                        # 读取并解析文件夹参数文件内容，转换为字符串进行比较
                        folder_params = str(eval(txt_file.read()))
                        folder_params_match = (current_params == folder_params)
                except Exception as e:
                    # 解析失败时忽略错误
                    pass
        
        # 设置文件夹按钮的属性，用于样式显示
        self.toolbar.folder_btn.setProperty("file_exists", folder_params_exists)
        self.toolbar.folder_btn.setProperty("param_matched", folder_params_match)
        self.toolbar.folder_btn.style().polish(self.toolbar.folder_btn)  # 刷新按钮样式，应用新属性
        
        # ======================== File模式检查 ========================
        file_params_exists = False  # 文件参数文件是否存在
        file_params_match = False  # 文件参数是否与当前参数匹配
        if self.file_path:  # 仅当有打开文件时才检查
            # 构建与当前文件同名的参数文件路径（替换扩展名）
            file_params_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
            
            if os.path.exists(file_params_path):
                file_params_exists = True
                try:
                    with open(file_params_path, 'r') as txt_file:
                        # 读取并解析文件参数内容，转换为字符串进行比较
                        file_params = str(eval(txt_file.read()))
                        file_params_match = (current_params == file_params)
                except Exception as e:
                    # 解析失败时忽略错误
                    pass
        
        # 设置文件按钮的属性，用于样式显示
        self.toolbar.file_btn.setProperty("file_exists", file_params_exists)
        self.toolbar.file_btn.setProperty("param_matched", file_params_match)
        self.toolbar.file_btn.style().polish(self.toolbar.file_btn)  # 刷新按钮样式，应用新属性

    def showParams(self):
        """显示参数，按照File→Folder→Default优先级加载参数
        
        根据当前打开的音频文件，从不同位置加载参数并应用到滑块上
        """
        # 简化版showParams，处理多种参数模式
        if self.file_path is None:
            return
        
        # 检查是否处于VAD模式
        is_vad_mode = self.toolbar.vad_btn.isChecked()
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
        """加载上一套参数
        
        从当前模式的参数集中加载上一套参数
        """
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.toolbar.vad_btn.isChecked() else "default"

        if len(self.param_sets[current_mode]) == 2:
            self.MySliders.resetParams(self.param_sets[current_mode][-2])
            self.param_sets[current_mode].reverse()


    def openFileDialog(self):
        """打开文件选择对话框，选择音频文件
        
        支持多种音频格式，选择后加载音频并显示相关信息
        """

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
            file_logger.info(f"Selected file: {self.file_path}")
            self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.toolbar.vad_btn.isChecked())
            
            # 启用所有模式按钮
            self.toolbar.default_btn.setEnabled(True)
            self.toolbar.folder_btn.setEnabled(True)
            self.toolbar.file_btn.setEnabled(True)
            
            # 三个按钮都不选中
            self.toolbar.default_btn.setChecked(False)
            self.toolbar.folder_btn.setChecked(False)
            self.toolbar.file_btn.setChecked(False)
            
            # 更新save和reset按钮的可用性
            self.updateToolbarButtonsState()
            self.showParams()

            self.checkIfParamsExist()  # 检查参数匹配，更新下划线

            dir_name = os.path.basename(os.path.dirname(self.file_path))
            base_name = os.path.basename(self.file_path)
            self.setWindowTitle(f"Praditor - {dir_name}/{base_name} ({self.which_one+1}/{len(self.file_paths)})")

            self.showXsetNum(is_test=False)

        else:
            file_logger.warning("Empty folder")


    def showXsetNum(self, is_test=False):
        """更新onset/offset按钮的显示文本，包含检测结果数量
        
        Args:
            is_test: 是否为测试模式，测试模式下显示问号标记
        """
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
        """打开帮助文档
        
        使用默认浏览器打开GitHub上的Praditor使用说明
        """
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

        # 直接启用所有带图标按钮
        icon_buttons_map = {
            self.title_bar.trash_btn: 'trash',
            self.title_bar.read_btn: 'read',
            self.title_bar.run_btn: 'play',
            self.title_bar.run_all_btn: 'run-all',
            self.title_bar.test_btn: 'test',
            self.title_bar.prev_audio_btn: 'prev_audio',
            self.title_bar.next_audio_btn: 'next_audio',
            self.title_bar.help_menu_btn: 'question',
            self.toolbar.save_btn: 'save',
            self.toolbar.reset_btn: 'reset',
            self.toolbar.backward_btn: 'backward',
            self.toolbar.forward_btn: 'forward',
        }
        for btn, icon_name in icon_buttons_map.items():
            self._setButtonEnabled(btn, icon_name, True)

        # 直接启用所有仅状态按钮
        state_only_buttons = [
            self.title_bar.title_label,
            self.title_bar.onset_btn,
            self.title_bar.offset_btn,
            self.toolbar.file_btn,
            self.toolbar.folder_btn,
            self.toolbar.default_btn,
            self.toolbar.vad_btn
        ]
        for btn in state_only_buttons:
            btn.setEnabled(True)

        # 启用滑块、工具栏和模式按钮
        self.MySliders.setEnabled(True)
        self.toolbar.setEnabled(True)
        self.toolbar.default_btn.setEnabled(True)
        self.toolbar.folder_btn.setEnabled(True)
        self.toolbar.file_btn.setEnabled(True)
        self.toolbar.vad_btn.setEnabled(True)

        
        self.updateToolbarButtonsState()  # 更新工具栏按钮状态

        system_logger.info("Abort")  # 记录手动停止日志，确保Reset按钮在参数文件保存后显示为可用
        
    

    
    def on_detect_finished(self, onset_results, offset_results):
        """检测任务完成后的处理
        
        Args:
            onset_results: Onset检测结果列表
            offset_results: Offset检测结果列表
        """
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
        """依次对所有音频文件执行Praditor检测
        
        按照顺序处理文件夹中的所有音频文件，检测完成后自动切换到下一个文件
        """
        """Run Praditor on all audio files sequentially, displaying one audio after current detection finishes"""
        if not hasattr(self, 'file_paths') or len(self.file_paths) == 0:
            return
        
        # 禁用除最小化、最大化、关闭、停止以外的所有按钮
        self.setButtonsEnabled(False)
        self.MySliders.setEnabled(False)
        self.toolbar.setEnabled(False)
        
        # 设置run-all标志和起始索引
        self.is_running_all = True
        self.run_all_current_index = 0  # 从第一个音频开始
        
        # 重置stop_flag
        from src.core import detection
        detection.stop_flag = False
        
        # 显示第一个音频
        self.which_one = self.run_all_current_index
        self.file_path = self.file_paths[self.which_one]
        dir_name = os.path.basename(os.path.dirname(self.file_path))
        base_name = os.path.basename(self.file_path)
        self.setWindowTitle(f"Praditor - {dir_name}/{base_name} ({self.which_one+1}/{len(self.file_paths)})")
        self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.toolbar.vad_btn.isChecked())
        self.showXsetNum(is_test=False)
        
        
        # 启动检测
        self.execPraditor(is_test=False)



    
    def on_run_signal(self):
        """处理run信号，开始执行检测
        
        设置stop_flag为False，然后执行检测
        """
        """处理run_signal信号，在执行检测前设置stop_flag = False"""
        from src.core import detection
        detection.stop_flag = False
        self.execPraditor(is_test=False)

    
    def on_test_signal(self):
        """处理test信号，开始测试检测
        
        设置stop_flag为False，然后执行测试检测
        """
        """处理test_signal信号，在执行检测前设置stop_flag = False"""
        from src.core import detection
        detection.stop_flag = False
        self.execPraditor(is_test=True)

    
    def process_detection_results(self):
        """处理检测结果
        
        对检测结果进行后处理，包括结果筛选、排序和保存
        """
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
            # self.update_current_param()
        # 
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
                self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.toolbar.vad_btn.isChecked())
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
                
                # 直接启用所有带图标按钮，与stopDetection方法保持一致
                icon_buttons_map = {
                    self.title_bar.trash_btn: 'trash',
                    self.title_bar.read_btn: 'read',
                    self.title_bar.run_btn: 'play',
                    self.title_bar.run_all_btn: 'run-all',
                    self.title_bar.test_btn: 'test',
                    self.title_bar.prev_audio_btn: 'prev_audio',
                    self.title_bar.next_audio_btn: 'next_audio',
                    self.title_bar.help_menu_btn: 'question',
                    self.toolbar.save_btn: 'save',
                    self.toolbar.reset_btn: 'reset',
                    self.toolbar.backward_btn: 'backward',
                    self.toolbar.forward_btn: 'forward',
                }
                for btn, icon_name in icon_buttons_map.items():
                    self._setButtonEnabled(btn, icon_name, True)

                # 直接启用所有仅状态按钮，与stopDetection方法保持一致
                state_only_buttons = [
                    self.title_bar.title_label,
                    self.title_bar.onset_btn,
                    self.title_bar.offset_btn,
                    self.toolbar.file_btn,
                    self.toolbar.folder_btn,
                    self.toolbar.default_btn,
                    self.toolbar.vad_btn
                ]
                for btn in state_only_buttons:
                    btn.setEnabled(True)

                # 启用滑块、工具栏和模式按钮
                self.MySliders.setEnabled(True)
                self.toolbar.setEnabled(True)
                self.toolbar.default_btn.setEnabled(True)
                self.toolbar.folder_btn.setEnabled(True)
                self.toolbar.file_btn.setEnabled(True)
                self.toolbar.vad_btn.setEnabled(True)
                self.updateToolbarButtonsState()
                
                # 发射run完成信号
                self.run_current_done.emit()
        else:
            # 单个文件处理完成
            # 直接启用所有带图标按钮，与stopDetection方法保持一致
            icon_buttons_map = {
                self.title_bar.trash_btn: 'trash',
                self.title_bar.read_btn: 'read',
                self.title_bar.run_btn: 'play',
                self.title_bar.run_all_btn: 'run-all',
                self.title_bar.test_btn: 'test',
                self.title_bar.prev_audio_btn: 'prev_audio',
                self.title_bar.next_audio_btn: 'next_audio',
                self.title_bar.help_menu_btn: 'question',
                self.toolbar.save_btn: 'save',
                self.toolbar.reset_btn: 'reset',
                self.toolbar.backward_btn: 'backward',
                self.toolbar.forward_btn: 'forward',
            }
            for btn, icon_name in icon_buttons_map.items():
                self._setButtonEnabled(btn, icon_name, True)

            # 直接启用所有仅状态按钮，与stopDetection方法保持一致
            state_only_buttons = [
                self.title_bar.title_label,
                self.title_bar.onset_btn,
                self.title_bar.offset_btn,
                self.toolbar.file_btn,
                self.toolbar.folder_btn,
                self.toolbar.default_btn,
                self.toolbar.vad_btn
            ]
            for btn in state_only_buttons:
                btn.setEnabled(True)

            # 启用滑块、工具栏和模式按钮
            self.MySliders.setEnabled(True)
            self.toolbar.setEnabled(True)
            self.toolbar.default_btn.setEnabled(True)
            self.toolbar.folder_btn.setEnabled(True)
            self.toolbar.file_btn.setEnabled(True)
            self.toolbar.vad_btn.setEnabled(True)
            self.updateToolbarButtonsState()
            
            # 发射run完成信号
            self.run_current_done.emit()
        


    def execPraditor(self, is_test: bool):
        """执行Praditor检测
        
        Args:
            is_test: 是否为测试模式，测试模式下不保存结果
        """

        from src.core import detection
        detection.stop_flag = False

        self.update_current_param()


        # 禁用所有滑块
        self.setButtonsEnabled(False)  # 禁用除最小化、最大化、关闭、停止以外的所有按钮
        self.MySliders.setEnabled(False)
        self.toolbar.setEnabled(False)
        

        # 检测当前模式，直接使用detectPraditor函数
        is_vad_mode = self.toolbar.vad_btn.isChecked()
        
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
        """更新当前参数集
        
        将当前滑块参数添加到参数集中，限制最多保存10套参数
        """
        current_params = self.MySliders.getParams()
        
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.toolbar.vad_btn.isChecked() else "default"
        
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
        """加载前一套参数
        
        从当前模式的参数集中加载上一套参数
        """
        """加载前一套参数"""
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.toolbar.vad_btn.isChecked() else "default"
        if self.param_sets[current_mode] and self.current_param_index[current_mode] > 0:
            self.current_param_index[current_mode] -= 1
            self.MySliders.resetParams(self.param_sets[current_mode][self.current_param_index[current_mode]])
            self.updateParamIndexLabel()
            # print(f"Loaded previous params (index: {self.current_param_index[current_mode]})")
    

    def loadNextParams(self):
        """加载后一套参数
        
        从当前模式的参数集中加载下一套参数
        """
        """加载后一套参数"""
        # 获取当前模式（默认或VAD）
        current_mode = "vad" if self.toolbar.vad_btn.isChecked() else "default"
        if self.param_sets[current_mode] and self.current_param_index[current_mode] < len(self.param_sets[current_mode]) - 1:
            self.current_param_index[current_mode] += 1
            self.MySliders.resetParams(self.param_sets[current_mode][self.current_param_index[current_mode]])
            self.updateParamIndexLabel()
            # print(f"Loaded next params (index: {self.current_param_index[current_mode]})")
    

    def updateParamIndexLabel(self):
        """更新参数索引标签
        
        更新工具栏上显示的当前参数索引和总数
        """
        """更新参数索引标签"""
        # print(self.param_sets)
        if hasattr(self.toolbar, 'params_btn'):
            # 获取当前模式（默认或VAD）
            current_mode = "vad" if self.toolbar.vad_btn.isChecked() else "default"
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
            self.toolbar.params_btn.setText(f"{display_index}/{min(total_count, 10)}")
    

    def updateToolbarButtonsState(self):
        """根据模式按钮的选中状态和音频导入状态更新按钮的可用性和样式
        - save按钮：依赖模式按钮的选中状态
        - reset按钮：必须选中的模式存在对应的参数文件
        - forward和backward按钮：必须成功导入音频且有两套及以上的参数
        """

        # 检查是否有任何模式按钮被选中
        any_mode_selected = self.toolbar.default_btn.isChecked() or self.toolbar.folder_btn.isChecked() or self.toolbar.file_btn.isChecked()
        
        # 检查音频是否已成功导入
        audio_imported = hasattr(self, 'file_path') and self.file_path is not None and len(self.file_path) > 0
        
        # 检查是否有两套及以上的参数
        current_mode = "vad" if self.toolbar.vad_btn.isChecked() else "default"
        has_multiple_params = len(self.param_sets[current_mode]) >= 2
        
        # 检查当前选中的模式是否存在对应的参数文件
        reset_enabled = False
        if any_mode_selected:
            # 检查是否处于VAD模式
            is_vad_mode = self.toolbar.vad_btn.isChecked()
            file_suffix = "_vad" if is_vad_mode else ""
            
            if self.toolbar.default_btn.isChecked():
                # Default模式：检查应用程序所在目录的params文件
                default_params_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"params{file_suffix}.txt")
                if not os.path.exists(default_params_path):
                    default_params_path = get_resource_path(f"src/app/params{file_suffix}.txt")
                reset_enabled = os.path.exists(default_params_path)
            elif self.toolbar.folder_btn.isChecked() and audio_imported:
                # Folder模式：检查当前文件夹的params文件
                folder_path = os.path.dirname(self.file_path)
                folder_params_path = os.path.join(folder_path, f"params{file_suffix}.txt")
                reset_enabled = os.path.exists(folder_params_path)
            elif self.toolbar.file_btn.isChecked() and audio_imported:
                # File模式：检查文件同名的params文件
                file_params_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
                reset_enabled = os.path.exists(file_params_path)
        
        # 更新save按钮
        self.toolbar.save_btn.setEnabled(any_mode_selected)
        self.toolbar.save_btn.setIcon(QIcon(get_resource_path(f'resources/icons/save{"_gray" if not any_mode_selected else ""}.svg')))
        
        # 更新reset按钮
        self.toolbar.reset_btn.setEnabled(reset_enabled)
        self.toolbar.reset_btn.setIcon(QIcon(get_resource_path(f'resources/icons/reset{"_gray" if not reset_enabled else ""}.svg')))
        
        # 更新backward按钮 - 必须音频导入成功且有两套及以上的参数
        backward_enabled = audio_imported and has_multiple_params
        self.toolbar.backward_btn.setEnabled(backward_enabled)
        self.toolbar.backward_btn.setIcon(QIcon(get_resource_path(f'resources/icons/backward{"_gray" if not backward_enabled else ""}.svg')))

        # 更新forward按钮 - 必须音频导入成功且有两套及以上的参数
        forward_enabled = audio_imported and has_multiple_params
        self.toolbar.forward_btn.setEnabled(forward_enabled)
        self.toolbar.forward_btn.setIcon(QIcon(get_resource_path(f'resources/icons/forward{"_gray" if not forward_enabled else ""}.svg')))
    
    def _setButtonEnabled(self, button, icon_name, enabled):
        """设置按钮是否可用，并自动切换图标
        
        Args:
            button (QPushButton): 要设置的按钮
            icon_name (str): 图标名称（不带.svg后缀）
            enabled (bool): 是否可用
        """
        # 设置按钮可用性
        button.setEnabled(enabled)
        
        button.setIcon(QIcon(get_resource_path(f'resources/icons/{icon_name}{"_gray" if not enabled else ""}.svg')))
    
    def setButtonsEnabled(self, enabled: bool):
        """设置按钮的启用状态
        Args:
            btns_esc: 要排除的按钮列表
            enabled: True表示恢复原始状态，False表示禁用
            禁用除了最小化、最大化、关闭、停止以外的所有按键
        """
        # 分类管理按钮 

        # 1. 带图标需要切换的按钮映射
        icon_buttons_map = {
            self.title_bar.trash_btn: 'trash',
            self.title_bar.read_btn: 'read',
            self.title_bar.run_btn: 'play',
            self.title_bar.run_all_btn: 'run-all',
            self.title_bar.test_btn: 'test',
            self.title_bar.prev_audio_btn: 'prev_audio',
            self.title_bar.next_audio_btn: 'next_audio',
            self.title_bar.help_menu_btn: 'question',
            self.toolbar.save_btn: 'save',
            self.toolbar.reset_btn: 'reset',
            self.toolbar.backward_btn: 'backward',
            self.toolbar.forward_btn: 'forward',
        }
        
        # 2. 仅需控制状态的按钮列表
        state_only_buttons = [
            self.title_bar.title_label,
            self.title_bar.onset_btn,
            self.title_bar.offset_btn,
            self.toolbar.file_btn,
            self.toolbar.folder_btn,
            self.toolbar.default_btn,
            self.toolbar.vad_btn
        ]
        
        # 3. 所有需要切换状态的按钮
        all_buttons = list(icon_buttons_map.keys()) + state_only_buttons
        
        if not enabled:
            # 禁用逻辑：保存原始状态并禁用所有按钮
            # 使用字典推导式简化状态保存
            self._button_original_states = {btn: btn.isEnabled() for btn in all_buttons}
            
            # 处理带图标按钮（切换图标+禁用）
            for btn, icon_name in icon_buttons_map.items():
                self._setButtonEnabled(btn, icon_name, False)
                print(icon_name)
            
            # 处理仅状态按钮（直接禁用）
            for btn in state_only_buttons:
                btn.setEnabled(False)
        else:
            # 启用逻辑：恢复原始状态
            # 处理带图标按钮
            for btn, icon_name in icon_buttons_map.items():
                self._setButtonEnabled(btn, icon_name, self._button_original_states.get(btn, True))
                print(icon_name)
            
            # 处理仅状态按钮
            for btn in state_only_buttons:
                btn.setEnabled(self._button_original_states.get(btn, True))
        
        # 确保窗口控制和停止按钮始终可用
        always_enabled_buttons = [
            self.title_bar.minimize_btn,
            self.title_bar.maximize_btn,
            self.title_bar.close_btn,
            self.title_bar.stop_btn
        ]
        for btn in always_enabled_buttons:
            btn.setEnabled(True)
        
        # 设置titlebar的is_running状态
        # 当enabled为False时，表示正在运行；为True时，表示已停止
        self.title_bar.setIsRunning(not enabled)




    def onModeButtonClicked(self, clicked_btn):
        """模式按钮点击事件处理
        
        确保一次只能选中一个模式按钮
        
        Args:
            clicked_btn: 被点击的模式按钮
        """
        """模式按钮点击事件处理，确保一次只能选中一个模式"""
        
        for btn in [self.toolbar.default_btn, self.toolbar.folder_btn, self.toolbar.file_btn]:  # 取消其他两个按钮的选中状态
            if btn != clicked_btn:
                btn.setChecked(False)
        
        self.updateToolbarButtonsState()  # 更新save和reset按钮状态


    def prevnext_audio(self, direction=None):
        """处理音频切换
        
        Args:
            direction: 切换方向，"prev"表示上一个，"next"表示下一个
        """
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
        self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path, is_vad_mode=self.toolbar.vad_btn.isChecked())
        
        # 启用所有模式按钮
        self.toolbar.default_btn.setEnabled(True)
        self.toolbar.folder_btn.setEnabled(True)
        self.toolbar.file_btn.setEnabled(True)
        
        # 三个按钮都不选中
        self.toolbar.default_btn.setChecked(False)
        self.toolbar.folder_btn.setChecked(False)
        self.toolbar.file_btn.setChecked(False)
        
        # 更新save和reset按钮的可用性
        self.updateToolbarButtonsState()
        self.showParams()

        # 检查参数匹配，更新下划线
        self.checkIfParamsExist()
        self.showXsetNum()


    def stopSound(self):
        """停止音频播放
        
        停止当前正在播放的音频
        """
        try:
            if self.audio_sink.state() == QAudio.State.ActiveState:
                self.audio_sink.stop()
                self.buffer.close()
                player_logger.info("Audio stopped")
        except AttributeError:
            pass
    

    def saveParamsWithFolderName(self):
        """保存参数到当前文件夹
        
        文件名为params.txt或params_vad.txt（VAD模式下）
        """
        """保存参数到当前文件夹，文件名为params.txt或params_vad.txt（VAD模式下）"""
        if hasattr(self, 'file_path') and self.file_path:
            # 检查是否处于VAD模式
            is_vad_mode = self.toolbar.vad_btn.isChecked()
            file_suffix = "_vad" if is_vad_mode else ""
            
            folder_path = os.path.dirname(self.file_path)
            txt_file_path = os.path.join(folder_path, f"params{file_suffix}.txt")
            
            with open(txt_file_path, 'w') as txt_file:
                txt_file.write(f"{self.MySliders.getParams()}")
            params_logger.info(f"Saved to folder as params{file_suffix}.txt: {txt_file_path}")
    
    def saveParamsToExeLocation(self):
        """保存参数到应用程序所在位置
        
        文件名为params.txt或params_vad.txt（VAD模式下）
        """
        """保存参数到exe所在位置，文件名为params.txt或params_vad.txt（VAD模式下）"""
        # 获取当前脚本所在目录（相当于exe所在位置）
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 检查是否处于VAD模式
        is_vad_mode = self.toolbar.vad_btn.isChecked()
        file_suffix = "_vad" if is_vad_mode else ""
        
        txt_file_path = os.path.join(exe_dir, f"params{file_suffix}.txt")
        
        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(f"{self.MySliders.getParams()}")
        params_logger.info(f"Saved to exe location: {txt_file_path}")
    
    def saveParamsWithFileName(self):
        """保存参数到音频文件同名文件
        
        文件名与当前音频文件同名，后缀为.txt或_vad.txt（VAD模式下）
        """
        """保存参数到file同名，文件名后缀为.txt或_vad.txt（VAD模式下）"""
        if hasattr(self, 'file_path') and self.file_path:
            # 检查是否处于VAD模式
            is_vad_mode = self.toolbar.vad_btn.isChecked()
            file_suffix = "_vad" if is_vad_mode else ""
            
            txt_file_path = os.path.splitext(self.file_path)[0] + f"{file_suffix}.txt"
            
            with open(txt_file_path, 'w') as txt_file:
                txt_file.write(f"{self.MySliders.getParams()}")
            params_logger.info(f"Saved with file name: {txt_file_path}")
    
    def toggleMaximize(self):
        """切换窗口最大化/还原状态
        
        根据当前窗口状态，切换到最大化或还原状态
        """
        # 切换窗口最大化/还原状态
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def setWindowTitle(self, title):
        """设置窗口标题
        
        同时更新自定义标题栏的标题
        
        Args:
            title: 新的窗口标题
        """
        # 重写setWindowTitle方法，同时更新自定义标题栏
        super().setWindowTitle(title)
        if hasattr(self, 'title_bar'):
            self.title_bar.set_title(title)
    
    def paintEvent(self, event):
        """重绘窗口背景
        
        绘制带有抗锯齿的圆角背景和阴影效果
        
        Args:
            event: 绘图事件对象
        """
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
        """处理鼠标按下事件
        
        当点击主窗口背景时，将焦点设置到主窗口，使QLineEdit失去焦点
        
        Args:
            event: 鼠标事件对象
        """
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
# print(get_resource_path('resources/icons/icon.ico'))
# print(os.path.exists(get_resource_path("resources/icons/icon.ico")))
# 设置窗口图标
# window.setWindowIcon(QIcon(resource_path('icon.ico')))
window.show()

app.exec()
