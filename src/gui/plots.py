import sys

import numpy as np
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QMargins, Signal, Property
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import (QApplication, QSlider, QVBoxLayout, QLabel, QHBoxLayout, 
    QWidget, QGridLayout)

from src.utils.audio import ReadSound, get_frm_points_from_textgrid


def formatted_time(ms):
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
    # print(max_show_frm, etime, stime)
    limit = max_show_frm if duration * samplerate > max_show_frm else int(duration * samplerate)


    scale_factor = duration * samplerate // limit # 计算需要的降采样因子
    # print(scale_factor)
    xsets = [x - stime for x in xsets if stime <= x <= stime+duration]
    return [round(x * samplerate / scale_factor) for x in xsets]


class AudioViewer(QWidget):
    # 添加信号，用于通知MainWindow执行prev/next操作
    prevClicked = Signal()
    nextClicked = Signal()

    def __init__(self):#, interval_ms=40000, resolution=20000):
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
        # self.slider_timerange.sliderMoved.connect(slider_mouse_changed)
        # self.slider_timerange.sliderPressed.connect(self.slider_pressed_h)
        # self.slider_timerange.sliderReleased.connect(self.slider_released_h)

        # 只保留结束时间label，删除开始时间label
        self.audio_etime = QLabel(f"{formatted_time(self.maximum)}")
        self.audio_etime.setAlignment(Qt.AlignCenter)
        self.audio_etime.setFixedWidth(75)
        self.audio_etime.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手形
        self.audio_etime.mousePressEvent = self.on_next_clicked  # 连接点击事件
        # 设置上面的label为灰色
        self.audio_etime.setStyleSheet("color: gray; font-weight: bold; background: transparent;")
        # --------------------------------------------
        # --------------------------------------------

        # -------------- line 1 ----------------


        self.label_stime = QLabel(f"{formatted_time(0)}")
        self.label_stime.setAlignment(Qt.AlignCenter)
        self.label_stime.setFixedWidth(75)
        self.label_stime.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手形
        self.label_stime.mousePressEvent = self.on_prev_clicked  # 连接点击事件
        # 设置下面的label为黑色，恢复原来的颜色
        self.label_stime.setStyleSheet("color: black; font-weight: bold;")
        
        self.label_etime = QLabel(f"{formatted_time(self.interval_ms)}")
        self.label_etime.setFixedWidth(75)
        self.label_etime.setAlignment(Qt.AlignCenter)
        self.label_etime.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手形
        self.label_etime.mousePressEvent = self.on_next_clicked  # 连接点击事件
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
        
        # 只添加结束时间label，删除开始时间label
        slider_layout.addWidget(self.audio_etime, 0, 2, Qt.AlignRight | Qt.AlignVCenter)
        
        self.layout.addWidget(slider_container)

        # 创建图表容器，使用QGridLayout实现图表和时间标签的重叠布局
        chart_container = QWidget()
        chart_container.setStyleSheet("background: transparent;")
        chart_layout = QGridLayout(chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 20)  # 增加内部下方padding 20px
        chart_layout.setSpacing(0)
        
        # 添加图表到网格布局，占据整个宽度，高度设为1行
        chart_layout.addWidget(self.chart_view, 0, 0, 1, 3)
        
        # 将时间标签添加到网格布局，与图表重叠，定位在下方padding区域
        chart_layout.addWidget(self.label_stime, 0, 0, Qt.AlignLeft | Qt.AlignBottom)
        chart_layout.addWidget(self.label_etime, 0, 2, Qt.AlignRight | Qt.AlignBottom)
        
        # 设置标签样式，确保它们清晰可见
        self.label_stime.setStyleSheet("color: black; font-weight: bold; background: transparent;")
        self.label_etime.setStyleSheet("color: black; font-weight: bold; background: transparent;")
        
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
        self.tg_dict_tp = self.readAudio(self.fpath)

        super().keyPressEvent(event)

    def wheelEvent(self, event):

        if not self.fpath:
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

    def resizeEvent(self, event):
        slider_width = self.slider_timerange.width() * self.interval_ms / self.maximum
        style = ""
        style += "QSlider::groove:horizontal { border: 0px solid #bbb; }"
        style += "QSlider::sub-page:horizontal { background: rgb(255,255, 255); border-radius: 2px; margin-top:2px; margin-bottom:2px; }"
        style += "QSlider::add-page:horizontal { background: rgb(255,255, 255); border-radius: 2px; margin-top:2px; margin-bottom:2px; }"
        style += f"QSlider::handle:horizontal {{ background: #333333; width: {slider_width}px; border-radius: 1px; margin-top:2px; margin-bottom:2px; }}"
        self.slider_timerange.setStyleSheet(style)

    def adjustWinSizeResolution(self):
        # 首先，一个时间窗的最大时间不可以超过这个音频的时间；若超过，则调整为音频时间
        if self.audio_obj.duration_seconds * 1000 < self.interval_ms:
            self.interval_ms = int(self.audio_obj.duration_seconds * 1000)

        # 其次，当确定了时间窗的大小之后，若是该时间窗对应的帧数小于了帧数分辨率，则把最小分辨率定为该窗的帧大小
        if self.interval_ms/1000 * self.audio_samplerate < self.resolution:
            self.resolution = int(self.interval_ms/1000 * self.audio_samplerate)
        # self.resolution = len(self.audio_obj.get_array_of_samples()) if len(self.audio_obj.get_array_of_samples()) < self.resolution else self.resolution
        # print("-----", self.interval_ms, self.resolution)


    def readAudio(self, fpath):
        # print(fpath)
        # self.tg_dict_tp = {"onset": [], "offset": []}
        if self.fpath != fpath:
            self.fpath = fpath
            # self.audio_obj = AudioSegment.from_file(self.fpath, format=self.fpath.split(".")[-1]).split_to_mono()[0]
            self.audio_obj = ReadSound(self.fpath)

            self.tg_dict_tp = {"Onset": {}, "Offset": {}}

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

        if not self.tg_dict_tp:
            pass
        else:
            self.tg_dict_tp = get_frm_points_from_textgrid(self.fpath)

        self.updateXset(self.tg_dict_tp)

        return self.tg_dict_tp


    def updateSlider(self):
        self.slider_timerange.setMaximum(self.maximum - self.interval_ms)
        # 计算slider宽度，确保有最小宽度20px，防止handler不可见
        slider_width = max(20, self.slider_timerange.width() * self.interval_ms / self.maximum)
        style = ""
        style += "QSlider::groove:horizontal { border: 0px solid #bbb; }"
        style += "QSlider::sub-page:horizontal { background: rgb(255,255, 255); border-radius: 2px; margin-top:2px; margin-bottom:2px; }"
        style += "QSlider::add-page:horizontal { background: rgb(255,255, 255); border-radius: 2px; margin-top:2px; margin-bottom:2px; }"
        style += f"QSlider::handle:horizontal {{ background: #333333; width: {slider_width}px; border-radius: 1px; margin-top:2px; margin-bottom:2px; }}"
        self.slider_timerange.setStyleSheet(style)

    def updateChart(self):
        self.label_stime.setText(f"{formatted_time(self.slider_timerange.sliderPosition())}")
        self.label_etime.setText(f"{formatted_time(self.slider_timerange.sliderPosition()+self.interval_ms)}")
        self.updateSlider()

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
        stime = self.slider_timerange.sliderPosition() / 1000
        xsets = downsampleXset(xsets, stime, self.interval_ms/1000, self.resolution, self.audio_samplerate)
        for line in self._chart.series():
            if len(line.points()) == 2:
                point = line.points()[0]
                # print(point.x())
                if point.x() in xsets:
                    line.setVisible(isVisible)


    def removeXset(self, xsets=[]):

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
        self.updateChart()
        self.updateXset(self.tg_dict_tp)

    def on_prev_clicked(self, event):
        """处理prev按钮点击事件"""
        self.prevClicked.emit()
    
    def on_next_clicked(self, event):
        """处理next按钮点击事件"""
        self.nextClicked.emit()
    
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
