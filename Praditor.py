import ctypes
import os
import sys
import webbrowser

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt, QIODevice, QBuffer, QUrl
from PySide6.QtGui import QAction, QIcon
from PySide6.QtMultimedia import QAudioFormat, QAudioOutput, QAudioDevice, QMediaDevices, QAudioSink, QAudio, \
    QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QFileDialog, QWidget, QToolBar, QPushButton, QSizePolicy, QMessageBox
)

from QSS import *
from core import runPraditorWithTimeRange, create_textgrid_with_time_point
from sigplot.plot_audio import AudioViewer
from slider.slider_section import MySliders
from tool import isAudioFile, resource_path, get_frm_points_from_textgrid


plat = os.name.lower()

if plat == 'nt':  # Windows
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'Praditor') # arbitrary string


elif plat == 'posix':  # Unix-like systems (Linux, macOS)
    pass
else:
    pass


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # load window icon
        # self.setWindowIcon(QIcon(QPixmap(resource_path('icon.png'))))
        self.param_sets = []
        self.audio_sink = None
        self.buffer = None
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.file_paths = []
        self.file_path = None
        self.which_one = 0
        self.setWindowTitle("Praditor")
        self.setMinimumSize(900, 720)



        # 初始化媒体播放器和音频输出
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)

        self.player.setAudioOutput(self.audio_output)


        # icon = QIcon()
        # icon.addPixmap(QPixmap(resource_path("icon.png")), QIcon.Normal, QIcon.On)
        # self.setWindowIcon(icon)
        self.setStatusBar(QStatusBar(self))
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #7f0020;
                
            }
        
        """)
        self.statusBar().setFixedHeight(20)


        # MENU
        # --------------------------------------
        # self.menuBar().setFixedHeight(35)

        file_menu = self.menuBar().addMenu("&File")
        button_action = QAction("&Read file...", self)
        button_action.setStatusTip("Folder to store target audios")
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
        # --------------------------------------



        # TOOLBAR
        # ---------------------

        toolbar = QToolBar("My main toolbar")
        toolbar.setFixedHeight(40)
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
        QToolBar {
            background-color:white;
            spacing: 10px;
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
        # toolbar.setIconSize(QSize(16, 16))


        self.addToolBar(toolbar)
        # ---------------------------------------------------------------
        toolbar.addSeparator()

        clear_xset = QPushButton("Clear", self)
        clear_xset.setFixedSize(50, 25)
        clear_xset.setStatusTip("Clear Onsets and Offsets")
        clear_xset.setStyleSheet(qss_button_normal)
        clear_xset.pressed.connect(self.clearXset)
        toolbar.addWidget(clear_xset)


        read_xset = QPushButton("Read", self)
        read_xset.setFixedSize(50, 25)
        read_xset.setStatusTip("Import Onsets and Offsets")
        read_xset.setStyleSheet(qss_button_normal)
        read_xset.pressed.connect(self.readXset)
        toolbar.addWidget(read_xset)

        toolbar.addSeparator()

        prev_audio = QPushButton("Prev", self)
        prev_audio.setFixedSize(50, 25)
        prev_audio.setStatusTip("Go to PREVIOUS audio in the folder")
        prev_audio.setStyleSheet(qss_button_normal)
        prev_audio.pressed.connect(self.prevnext_audio)
        toolbar.addWidget(prev_audio)

        run_praditor = QPushButton("Extract", self)
        run_praditor.setFixedSize(65, 25)
        run_praditor.setStatusTip("Initiate Praditor to extract speech onsets/offsets")
        run_praditor.setStyleSheet(qss_button_normal)
        run_praditor.pressed.connect(self.runPraditorOnAudio)
        toolbar.addWidget(run_praditor)

        next_audio = QPushButton("Next", self)
        next_audio.setFixedSize(50, 25)
        next_audio.setStatusTip("Go to NEXT audio in the folder")
        next_audio.setStyleSheet(qss_button_normal)
        next_audio.pressed.connect(self.prevnext_audio)
        toolbar.addWidget(next_audio)
        toolbar.addSeparator()

        # ----------------------------------------------
        # ----------------------------------------------
        # ----------------------------------------------


        self.run_onset = QPushButton("Onset", self)
        self.run_onset.setStatusTip("Extract Onsets")
        self.run_onset.setFixedSize(60, 25)
        self.run_onset.pressed.connect(self.turnOnset)
        self.run_onset.setStyleSheet(qss_button_checkable_with_color())
        self.run_onset.setCheckable(True)
        # self.run_onset.setChecked(False)
        toolbar.addWidget(self.run_onset)

        self.run_offset = QPushButton("Offset", self)
        self.run_offset.setStatusTip("Extract Offsets")
        self.run_offset.setFixedSize(60, 25)
        self.run_offset.pressed.connect(self.turnOffset)
        self.run_offset.setStyleSheet(qss_button_checkable_with_color("#2AD25E"))
        self.run_offset.setCheckable(True)
        # self.run_offset.setChecked(False)
        toolbar.addWidget(self.run_offset)




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
        self.save_param.setStyleSheet(qss_button_checkable_with_color("#7f0020"))
        self.save_param.pressed.connect(self.saveParams)
        self.save_param.setCheckable(True)
        self.save_param.setChecked(True)
        toolbar.addWidget(self.save_param)

        self.reset_param = QPushButton("Reset", self)
        self.reset_param.setFixedSize(50, 25)
        self.reset_param.setStatusTip("Reset to params that has been saved")
        self.reset_param.setStyleSheet(qss_button_normal)
        self.reset_param.pressed.connect(self.resetParams)
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
        if not os.path.exists("params.txt"):
            with open("params.txt", 'w') as txt_file:
                txt_file.write(f"{self.MySliders.getParams()}")
        else:
            with open("params.txt", "r") as txt_file:
                self.MySliders.resetParams(eval(txt_file.read()))



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
        self.AudioViewer.tg_dict_tp = get_frm_points_from_textgrid(self.file_path)

        self.AudioViewer.updateXset(self.AudioViewer.tg_dict_tp)
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["onset"], isVisible=not self.run_onset.isChecked())
        self.AudioViewer.hideXset(self.AudioViewer.tg_dict_tp["offset"], isVisible=not self.run_offset.isChecked())


    def clearXset(self):
        self.AudioViewer.tg_dict_tp = get_frm_points_from_textgrid(self.file_path)

        if not self.run_onset.isChecked():
            self.AudioViewer.removeXset(self.AudioViewer.tg_dict_tp["onset"])
        if not self.run_offset.isChecked():
            self.AudioViewer.removeXset(self.AudioViewer.tg_dict_tp["offset"])



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
        if self.select_mode.text() == "Current":
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        else:  # if self.select_mode.text() == "Default":
            txt_file_path = "params.txt"

        try:
            with open(txt_file_path, 'r') as txt_file:
                self.MySliders.resetParams(eval(txt_file.read()))
            print(f"Params TXT file read from: {txt_file_path}")

        except FileNotFoundError:
            self.select_mode.setChecked(False)

            print("Go back to Default mode")


            self.showParams()

    def saveParams(self):
        # print(resource_path("params.txt"))
        if self.select_mode.text() == "Current":
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        else:  # if self.select_mode.text() == "Default":
            txt_file_path = "params.txt"

        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(f"{self.MySliders.getParams()}")
        print(self.save_param.isChecked())
        self.save_param.setChecked(False)


    def checkIfParamsExist(self):
        if self.select_mode.text() == "Current":
            txt_file_path = os.path.splitext(self.file_path)[0] + ".txt"
        else:  # if self.select_mode.text() == "Default":
            txt_file_path = "params.txt"

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
            if not os.path.exists(os.path.splitext(self.file_path)[0] + ".txt"):
                with open(os.path.splitext(self.file_path)[0] + ".txt", "w") as txt_file:
                    with open("params.txt", "r") as default_txt_file:
                        txt_file.write(default_txt_file.read())
        elif self.select_mode.text() == "Default":
            pass

        # 第四步 根据按钮文字呈现参数
        if self.select_mode.text() == "Current":
            with open(os.path.splitext(self.file_path)[0] + ".txt", 'r') as txt_file:
                self.MySliders.resetParams(eval(txt_file.read()))
            self.select_mode.setChecked(False)
        elif self.select_mode.text() == "Default":
            with open("params.txt", 'r') as txt_file:
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

            if os.path.exists(os.path.splitext(self.file_path)[0] + ".txt"):
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

        if not self.AudioViewer.tg_dict_tp['onset']:
            self.run_onset.setText("Onset")
        else:
            self.run_onset.setText(f"{len(self.AudioViewer.tg_dict_tp['onset'])}")

        if not self.AudioViewer.tg_dict_tp['offset']:
            self.run_offset.setText("Offset")
        else:
            self.run_offset.setText(f"{len(self.AudioViewer.tg_dict_tp['offset'])}")

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
            popup_window.setWindowIcon(QIcon(resource_path('icon.png')))
            popup_window.setText(f"LowPass exceeds the Nyquist frequency boundary {float(self.AudioViewer.audio_samplerate)/2:.0f}")
            popup_window.exec()



        if not self.run_onset.isChecked():
            self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["onset"])
            self.AudioViewer.tg_dict_tp["onset"] = runPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "onset")
        else:
            self.AudioViewer.tg_dict_tp["onset"] = []

        if not self.run_offset.isChecked():
            self.AudioViewer.removeXset(xsets=self.AudioViewer.tg_dict_tp["offset"])
            self.AudioViewer.tg_dict_tp["offset"] = runPraditorWithTimeRange(self.MySliders.getParams(), self.AudioViewer.audio_obj, "offset")
        else:
            self.AudioViewer.tg_dict_tp["offset"] = []

        create_textgrid_with_time_point(self.file_path, self.AudioViewer.tg_dict_tp["onset"], self.AudioViewer.tg_dict_tp["offset"])
        self.readXset()
        self.showXsetNum()
        self.update_current_param()

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
        self.setWindowTitle(f"Praditor - {self.file_path} ({self.which_one+1}/{len(self.file_paths)})")
        self.AudioViewer.tg_dict_tp = self.AudioViewer.readAudio(self.file_path)

        if os.path.exists(os.path.splitext(self.file_path)[0] + ".txt"):
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
print(resource_path('icon.ico'))
print(os.path.exists(resource_path("icon.ico")))
# 设置窗口图标
# window.setWindowIcon(QIcon(resource_path('icon.ico')))
window.show()

app.exec()