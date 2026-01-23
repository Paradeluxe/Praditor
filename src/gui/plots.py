import sys

import numpy as np
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QMargins, Signal, Property
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import (QApplication, QSlider, QVBoxLayout, QLabel, QHBoxLayout, 
    QWidget, QGridLayout)

from src.utils.audio import ReadSound, get_frm_points_from_textgrid, get_frm_intervals_from_textgrid


def formatted_time(ms):
    """将毫秒转换为格式化的时间字符串
    
    Args:
        ms: 毫秒数
        
    Returns:
        格式化的时间字符串，格式为mm:ss.mmm
    """
    # 将毫秒转换成秒和毫秒
    seconds = ms // 1000
    milliseconds = ms % 1000

    # 将秒转换成分钟和秒
    minutes = seconds // 60
    seconds = seconds % 60

    # # 将分钟转换成小时和分钟
    # hours = minutes // 60
    # minutes = minutes % 60

    # 格式化输出
    return f"{minutes:d}:{seconds:02d}.{milliseconds:03d}"

def downsampleSignal(signal, max_limit):
    """对信号进行降采样，减少数据点数
    
    Args:
        signal: 原始信号数组
        max_limit: 最大数据点限制
        
    Returns:
        降采样后的信号数组
    """
    limit = max_limit if len(signal) > max_limit else len(signal)
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError(f"limit must be a positive integer, not {limit}")

    # 计算需要的降采样因子
    scale_factor = len(signal) // limit

    # 如果计算出的scale_factor为0，说明输入信号太短，无法达到目标点数
    if scale_factor == 0:
        raise ValueError("Input signal is too short to reach the target number of points")
    signal = np.array(signal).reshape(-1, 1)
    # 计算每个块的平均值
    downsampled_signal = signal[::scale_factor].mean(axis=1)

    return downsampled_signal

def downsampleXset(xsets, stime, duration, max_show_frm, samplerate):
    """对Xset数据进行降采样，适应显示需求
    
    Args:
        xsets: Xset数据列表
        stime: 开始时间
        duration: 持续时间
        max_show_frm: 最大显示帧数
        samplerate: 采样率
        
    Returns:
        降采样后的Xset数据列表
    """
    # print(max_show_frm, etime, stime)
    limit = max_show_frm if duration * samplerate > max_show_frm else int(duration * samplerate)


    scale_factor = duration * samplerate // limit # 计算需要的降采样因子
    # print(scale_factor)
    xsets = [x - stime for x in xsets if stime <= x <= stime+duration]
    return [round(x * samplerate / scale_factor) for x in xsets]


class AudioViewer(QWidget):
    """音频可视化组件，用于显示音频波形和检测结果
    
    包含音频波形显示、时间滑块、缩放功能和检测结果可视化
    """
    
    def __init__(self):#, interval_ms=40000, resolution=20000):
        """初始化AudioViewer组件
        
        Args:
            interval_ms: 初始时间窗口大小（毫秒）
            resolution: 显示分辨率
        """
        super().__init__()
        self.max_amp_ratio = 1.0
        self.tg_dict_tp = {"onset": [], "offset": []}
        self.audio_arr = None
        self.max_amp = None
        self.audio_clip = None
        self.time_unit = 441
        self.setMinimumHeight(400)  # 增大plot的最小高度
        self.setMinimumSize(800, 400)
        self.interval_ms = 1
        self.fpath = ""
        self.resolution = 1
        self.showOnset = True
        self.showOffset = True


        self.audio_obj = None
        self.audio_samplerate = None
        self.maximum = 1

        # --------------- line 0 -------------------

        self.slider_timerange = QSlider(Qt.Orientation.Horizontal)
        self.slider_timerange.setMinimum(0)
        self.slider_timerange.setMaximum(self.maximum-self.interval_ms)
        self.slider_timerange.setSingleStep(1)
        self.slider_timerange.valueChanged.connect(self.sliderValueChanged)


        # 只保留结束时间label，删除开始时间label
        self.audio_etime = QLabel(f"{formatted_time(self.maximum)}")
        self.audio_etime.setAlignment(Qt.AlignCenter)
        self.audio_etime.setFixedWidth(75)
        # 设置上面的label为灰色
        self.audio_etime.setStyleSheet("color: gray; font-weight: bold; background: transparent;")
        # --------------------------------------------
        # --------------------------------------------

        # -------------- line 1 ----------------


        self.label_stime = QLabel(f"{formatted_time(0)}")
        self.label_stime.setAlignment(Qt.AlignCenter)
        self.label_stime.setFixedWidth(75)
        # 设置下面的label为黑色，恢复原来的颜色
        self.label_stime.setStyleSheet("color: black; font-weight: bold;")
        
        self.label_etime = QLabel(f"{formatted_time(self.interval_ms)}")
        self.label_etime.setFixedWidth(75)
        self.label_etime.setAlignment(Qt.AlignCenter)
        # 设置下面的label为黑色，恢复原来的颜色
        self.label_etime.setStyleSheet("color: black; font-weight: bold;")

        self._chart = QChart()
        # self._chart.setBackgroundRoundness(8)
        # self._chart.setBorderColor(QColor('red'))
        self._chart.layout().setContentsMargins(0, 0, 0, 0)
        self._chart.setMargins(QMargins(0, 0, 0, 0))
        # self._chart.setBackgroundVisible(False)

        self._chart.legend().hide()
        self._axis_x = QValueAxis()
        self._axis_x.setVisible(False)

        self._axis_y = QValueAxis()
        self._axis_y.setVisible(False)

        self._chart.legend().hide()


        self.chart_view = QChartView(self._chart)
        # self.chart_view.setRenderHint(QPainter.LosslessImageRendering)
        # self.chart_view.setRenderHint(QPainter.TextAntialiasing)
        self.chart_view.setStyleSheet("background: transparent; border: none;")
        
        # 为图表添加拖动功能
        self.chart_view.setMouseTracking(True)  # 启用鼠标跟踪
        self.chart_view.mousePressEvent = self.chart_mouse_press_event
        self.chart_view.mouseMoveEvent = self.chart_mouse_move_event
        self.chart_view.mouseReleaseEvent = self.chart_mouse_release_event
        
        # 拖动状态变量
        self.is_dragging = False
        self.last_mouse_pos = 0

        # --------------------------------------------
        # --------------------------------------------

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建slider容器，使用QGridLayout实现label与slider重叠
        slider_container = QWidget()
        slider_layout = QGridLayout(slider_container)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(0)
        
        # 添加slider到网格布局，占据整个宽度
        slider_layout.addWidget(self.slider_timerange, 0, 0, 1, 3)
        
        self.layout.addWidget(slider_container)

        # 创建左上角的0:00.000标签
        self.label_zero = QLabel(f"0:00.000")
        self.label_zero.setFixedWidth(75)
        self.label_zero.setAlignment(Qt.AlignCenter)
        self.label_zero.setStyleSheet("color: gray; font-weight: bold; background: transparent;")
        
        # 创建图表容器，使用QGridLayout实现图表和时间标签的重叠布局
        chart_container = QWidget()
        chart_container.setStyleSheet("background: transparent;")
        chart_layout = QGridLayout(chart_container)
        chart_layout.setContentsMargins(0, 15, 0, 20)  # 增加内部上方padding 15px，下方20px
        chart_layout.setSpacing(0)
        
        # 添加图表到网格布局，占据整个宽度，高度设为1行
        chart_layout.addWidget(self.chart_view, 0, 0, 1, 3)
        
        # 添加左上角的0:00.000标签
        chart_layout.addWidget(self.label_zero, 0, 0, Qt.AlignLeft | Qt.AlignTop)
        
        # 添加右上角的总时长标签
        chart_layout.addWidget(self.audio_etime, 0, 2, Qt.AlignRight | Qt.AlignTop)
        
        # 将时间标签添加到网格布局，与图表重叠，定位在下方padding区域
        chart_layout.addWidget(self.label_stime, 0, 0, Qt.AlignLeft | Qt.AlignBottom)
        chart_layout.addWidget(self.label_etime, 0, 2, Qt.AlignRight | Qt.AlignBottom)
        
        # 设置标签样式，确保它们清晰可见
        self.label_stime.setStyleSheet("color: black; font-weight: bold; background: transparent;")
        self.label_etime.setStyleSheet("color: black; font-weight: bold; background: transparent;")
        self.label_zero.setStyleSheet("color: gray; font-weight: bold; background: transparent;")
        self.audio_etime.setStyleSheet("color: gray; font-weight: bold; background: transparent;")
        
        # 将图表容器添加到主布局
        self.layout.addWidget(chart_container)

        self.setStyleSheet("""
            QSlider {
                background: transparent;
            }
        """)
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 10)

        # 第二次设置初始值
        self.interval_ms = 100 * 128
        self.resolution = self.time_unit * 10  # 100 ms 的长度作为所有samplerate的分辨率




    def keyPressEvent(self, event):
        """处理键盘按键事件
        
        支持Ctrl+I和Ctrl+O快捷键，用于缩小和放大时间窗口
        
        Args:
            event: 键盘事件对象
        """

        if event.modifiers() == Qt.ControlModifier:
            # print(event)
            if event.key() == Qt.Key_I:
                self.interval_ms //= 2  #  缩小间隔
            elif event.key() == Qt.Key_O:
                self.interval_ms *= 2  #  放大间隔

            else:
                pass
        
        
        if self.interval_ms > 100 * 128:
            self.interval_ms = 100 * 128
        elif self.interval_ms < 100:
            self.interval_ms = 100
        
        # 只有当音频文件已加载时才调用readAudio
        if self.fpath and self.audio_obj:
            self.tg_dict_tp = self.readAudio(self.fpath)

        super().keyPressEvent(event)

    def wheelEvent(self, event):
        """处理鼠标滚轮事件
        
        支持Ctrl+滚轮缩放时间窗口，Shift+滚轮左右拖动，单独滚轮调整振幅显示
        
        Args:
            event: 鼠标滚轮事件对象
        """

        if not self.fpath or not self.audio_obj:
            return
        # print(event.modifiers())
        delta = event.angleDelta()
        # print(delta)
        # 判断是否为鼠标滚轮的固定步长（120 的倍数）
        if abs(delta.y()) % 120 == 0 and delta.x() == 0:  # 滚轮
            _x = delta.x()
            _y = delta.y()

        else:
            _x = delta.x()
            _y = -delta.y()


        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:  # 滚轮同时按下了Ctrl键
            if _y > 0:  # Scroll Up with CTRL
                self.interval_ms *= 2

            else:  # Scroll Down with CTRL
                self.interval_ms //= 2
            # print(self.interval_ms)

        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:  # 滚轮同时按下了Shift键
            if _y > 20:
                self.slider_timerange.setValue(self.slider_timerange.value() - 20)
            elif _y < -20:
                self.slider_timerange.setValue(self.slider_timerange.value() + 20)

        else:  # 单独的滚轮
            if _y > 20:
                self.max_amp_ratio -= 0.1  # Scroll Up

            elif _y < -20:
                self.max_amp_ratio += 0.1  # Scroll Down

            if _x > 100:
                self.slider_timerange.setValue(self.slider_timerange.value()-20)
            elif _x < -100:
                self.slider_timerange.setValue(self.slider_timerange.value()+20)



        if self.max_amp_ratio > 1.0:
            self.max_amp_ratio = 1.0
        elif self.max_amp_ratio < 0.1:
            self.max_amp_ratio = 0.1

        if self.interval_ms > 100 * 128:
            self.interval_ms = 100 * 128
        elif self.interval_ms < 100:
            self.interval_ms = 100
        # print(self.max_amp_ratio)
        # print(self.max_amp_ratio, self.interval_ms)

        self.tg_dict_tp = self.readAudio(self.fpath)
        super().wheelEvent(event)


    def adjustWinSizeResolution(self):
        """调整窗口大小和分辨率
        
        确保时间窗口不超过音频时长，且分辨率适应窗口大小
        """
        # 确保audio_obj已成功创建
        if not self.audio_obj:
            return
            
        # 首先，一个时间窗的最大时间不可以超过这个音频的时间；若超过，则调整为音频时间
        if self.audio_obj.duration_seconds * 1000 < self.interval_ms:
            self.interval_ms = int(self.audio_obj.duration_seconds * 1000)

        # 其次，当确定了时间窗的大小之后，若是该时间窗对应的帧数小于了帧数分辨率，则把最小分辨率定为该窗的帧大小
        if self.interval_ms/1000 * self.audio_samplerate < self.resolution:
            self.resolution = int(self.interval_ms/1000 * self.audio_samplerate)
        # self.resolution = len(self.audio_obj.get_array_of_samples()) if len(self.audio_obj.get_array_of_samples()) < self.resolution else self.resolution
        # print("-----", self.interval_ms, self.resolution)


    def readAudio(self, fpath, is_vad_mode=False):
        """读取音频文件并更新可视化
        
        Args:
            fpath: 音频文件路径
            is_vad_mode: 是否为VAD模式
            
        Returns:
            检测结果字典
        """
        # 确保文件路径有效
        if not fpath:
            return {"onset": [], "offset": []}
        
        # print(fpath)
        if self.fpath != fpath:
            self.fpath = fpath
            try:
                # self.audio_obj = AudioSegment.from_file(self.fpath, format=self.fpath.split(".")[-1]).split_to_mono()[0]
                self.audio_obj = ReadSound(self.fpath)
            except Exception as e:
                # 处理音频文件读取失败的情况
                self.audio_obj = None
                return {"onset": [], "offset": []}
        
        # 确保audio_obj已成功创建
        if not self.audio_obj:
            return {"onset": [], "offset": []}

        self.audio_samplerate = self.audio_obj.frame_rate
        self.max_amp = self.audio_obj.max * self.max_amp_ratio

        self.maximum = int(self.audio_obj.duration_seconds * 1000)
        self.time_unit = self.audio_samplerate // 100
        self.audio_etime.setText(f"{formatted_time(self.maximum)}")

        self.adjustWinSizeResolution()

        self._axis_x.setRange(0, self.resolution)
        self._axis_y.setRange(-self.max_amp, self.max_amp)

        self.updateSlider()
        self.updateChart()

        # 根据模式选择不同的函数读取结果
        if is_vad_mode:
            # VAD模式：读取_vad.TextGrid文件
            self.tg_dict_tp = get_frm_intervals_from_textgrid(self.fpath)
        else:
            # 默认模式：读取.TextGrid文件
            self.tg_dict_tp = get_frm_points_from_textgrid(self.fpath)

        self.updateXset(self.tg_dict_tp)

        return self.tg_dict_tp


    def updateSlider(self):
        """更新时间滑块
        
        根据音频时长和当前时间窗口大小，更新滑块的最大位置和样式
        """
        
        self.slider_timerange.setMaximum(self.maximum - self.interval_ms)
        # 计算slider宽度，确保有最小宽度20px，防止handler不可见，同时最大宽度不超过slider本身长度-1
        slider_width = int(max(20, self.slider_timerange.width() * self.interval_ms / self.maximum))
        # 设置滑块最大长度为slider本身长度-1
        slider_width = min(slider_width, self.slider_timerange.width() - 1)
        # print("滑块长度:", slider_width, "slider本身长度:", self.slider_timerange.width(), "滑轨最大长度:", self.slider_timerange.maximum(), "滑块位置:", self.slider_timerange.sliderPosition())
        
        # 根据是否导入音频决定滑块样式
        handle_bg = "transparent" if not self.fpath else "#333333"
        
        style = ""
        style += "QSlider::groove:horizontal { border: 1px solid #e0e0e0; border-radius: 3px; background: #ffffff; }"
        style += "QSlider::sub-page:horizontal { background: #ffffff; border-radius: 3px; padding-top:2px; padding-bottom:2px; }"
        style += "QSlider::add-page:horizontal { background: #ffffff; border-radius: 3px; padding-top:2px; padding-bottom:2px; }"
        style += f"QSlider::handle:horizontal {{ background: {handle_bg}; width: {slider_width}px; border-radius: 3px; padding-top:2px; padding-bottom:2px; }}"
        self.slider_timerange.setStyleSheet(style)



    def resizeEvent(self, event):  # 窗口大小改变时调用 (包括初始化设置写完之后)
        """处理窗口大小改变事件
        
        调整滑块样式以适应新的窗口大小
        
        Args:
            event: 窗口大小改变事件对象
        """
        slider_width = int(self.slider_timerange.width() * self.interval_ms / self.maximum) 
        
        # 根据是否导入音频决定滑块样式
        handle_bg = "transparent" if not self.fpath else "#333333"
        page_bg = "transparent" if not self.fpath else "#ffffff"
        
        style = ""
        style += "QSlider::groove:horizontal { border: 1px solid #e0e0e0; border-radius: 3px; background: #ffffff; }"
        style += f"QSlider::sub-page:horizontal {{ background: {page_bg}; border-radius: 3px; padding-top:2px; padding-bottom:2px; }}"
        style += f"QSlider::add-page:horizontal {{ background: {page_bg}; border-radius: 3px; padding-top:2px; padding-bottom:2px; }}"
        style += f"QSlider::handle:horizontal {{ background: {handle_bg}; width: {slider_width}px; border-radius: 3px; padding-top:2px; padding-bottom:2px; }}"
        self.slider_timerange.setStyleSheet(style)


    def updateChart(self):
        """更新图表显示
        
        根据当前时间窗口，更新音频波形的显示
        """
        self.label_stime.setText(f"{formatted_time(self.slider_timerange.sliderPosition())}")
        self.label_etime.setText(f"{formatted_time(self.slider_timerange.sliderPosition()+self.interval_ms)}")
        self.updateSlider()

        # 确保audio_obj已成功创建
        if not self.audio_obj:
            return
            
        this_series = QLineSeries()
        # this_series.setColor("rgb(193,204,208)")
        pen = QPen(QColor("grey"))
        pen.setWidth(1)  # 设置线条宽度为3像素
        this_series.setPen(pen)  # 应用这个笔刷到线条系列
        # print(self.slider_timerange.sliderPosition(), self.slider_timerange.sliderPosition()+self.interval_ms)
        self.audio_arr = np.array(self.audio_obj[self.slider_timerange.sliderPosition():self.slider_timerange.sliderPosition()+self.interval_ms].get_array_of_samples())
        thumbnail = downsampleSignal(self.audio_arr, self.resolution)
        timepoint = [i for i in range(len(thumbnail))]
        # 将数组数据一次性添加到序列中
        points = [(x, y) for x, y in zip(timepoint, thumbnail)]
        # self.series.replace(points)
        for p in points:
            this_series.append(*p)

        self._chart.removeAllSeries()
        self._chart.addSeries(this_series)
        self._chart.setAxisX(self._axis_x, this_series)
        self._chart.setAxisY(self._axis_y, this_series)
        self._axis_x.setRange(0, self.resolution)


    def hideXset(self, xsets=[], isVisible=True):
        """隐藏或显示Xset检测结果
        
        Args:
            xsets: Xset检测结果列表
            isVisible: 是否可见
        """
        stime = self.slider_timerange.sliderPosition() / 1000
        xsets = downsampleXset(xsets, stime, self.interval_ms/1000, self.resolution, self.audio_samplerate)
        for line in self._chart.series():
            if len(line.points()) == 2:
                point = line.points()[0]
                # print(point.x())
                if point.x() in xsets:
                    line.setVisible(isVisible)


    def removeXset(self, xsets=[]):
        """移除Xset检测结果
        
        Args:
            xsets: Xset检测结果列表
        """

        if not xsets:
            return

        stime = self.slider_timerange.sliderPosition() / 1000
        # etime = (self.slider_timerange.sliderPosition() + self.interval_ms) / 1000

        xsets = downsampleXset(xsets, stime, self.interval_ms/1000, self.resolution, self.audio_samplerate)
        # print(xsets)
        for line in self._chart.series():
            if len(line.points()) == 2:
                point = line.points()[0]
                # print(point.x())
                if point.x() in xsets:
                    self._chart.removeSeries(line)



    def updateXset(self, tg_dict):#, showOnset=True, showOffset=True):
        """更新Xset检测结果显示
        
        Args:
            tg_dict: 包含onset和offset检测结果的字典
        """

        if not tg_dict:
            return

        stime = self.slider_timerange.sliderPosition() / 1000
        # etime = (self.slider_timerange.sliderPosition() + self.interval_ms) / 1000

        for mode in tg_dict:
            # if (not showOnset and mode == "onset") or (not showOffset and mode == "offset"):
            #     continue
            xsets = tg_dict[mode]

            xsets = downsampleXset(xsets, stime, self.interval_ms/1000, self.resolution, self.audio_samplerate)

            for xset in xsets:
                test_series = QLineSeries()
                # test_series.setColor("#1991D3")
                if mode == "onset":
                    pen = QPen(QColor("#1991D3"))
                else:
                    pen = QPen(QColor("#2AD25E"))

                pen.setWidth(0)  # 设置线条宽度为3像素
                test_series.setPen(pen)  # 应用这个笔刷到线条系列

                test_series.append(xset, -self.max_amp)
                test_series.append(xset, self.max_amp)

                self._chart.addSeries(test_series)
                self._chart.setAxisX(self._axis_x, test_series)
                self._chart.setAxisY(self._axis_y, test_series)


        try:
            self.hideXset(self.tg_dict_tp["onset"], isVisible=self.showOnset)
        except KeyError:
            pass
        try:
            self.hideXset(self.tg_dict_tp["offset"], isVisible=self.showOffset)
        except KeyError:
            pass


    def sliderValueChanged(self):
        """滑块值变化事件处理
        
        当时间滑块值改变时，更新图表和Xset显示
        """
        self.updateChart()
        self.updateXset(self.tg_dict_tp)


    
    def chart_mouse_press_event(self, event):
        """处理图表鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_mouse_pos = event.position().x()
    
    def chart_mouse_move_event(self, event):
        """处理图表鼠标移动事件"""
        if self.is_dragging:
            current_pos = event.position().x()
            delta_x = current_pos - self.last_mouse_pos
            
            # 根据鼠标移动距离计算滑块需要移动的值
            chart_width = self.chart_view.width()
            if chart_width > 0:
                # 计算每像素对应的时间（毫秒）
                pixel_to_ms = (self.interval_ms) / chart_width
                # 计算滑块需要移动的值（取反，因为鼠标向右移动时，音频应该向前播放）
                # 增加拖动速度，并设置最小拖动速度，确保在interval_ms很小时也能正常拖动
                base_speed = 1.5
                min_speed = 20  # 最小拖动速度（毫秒/像素）
                # 计算实际速度，取设定的最小速度和计算速度的最大值
                actual_speed = max(min_speed, pixel_to_ms * base_speed)
                slider_delta = int(-delta_x * actual_speed)
                
                # 更新滑块值
                new_value = self.slider_timerange.value() + slider_delta
                # 确保滑块值在有效范围内
                new_value = max(0, min(new_value, self.maximum - self.interval_ms))
                self.slider_timerange.setValue(new_value)
                
                # 更新最后鼠标位置
                self.last_mouse_pos = current_pos
    
    def chart_mouse_release_event(self, event):
        """处理图表鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AudioViewer()#r"C:\Users\18357\Desktop\Py_GUI\test.wav")
    # window.readAudio(r"C:\Users\18357\Desktop\Py_GUI\test.wav")
    # window.show()
    # window.tgChanged.connect(lambda: print(f"值已改变: "))
    window.tg_dict_tp = {"onset": [], "offset": []}
    # window.resize(1200, 300)

    # sys.exit(app.exec())
