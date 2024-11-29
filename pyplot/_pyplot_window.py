import sys
from PySide6.QtCore import QPointF, QMargins
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QMainWindow, QApplication, QGraphicsLineItem
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import Qt
from pydub import AudioSegment
import numpy as np


def mean_downsampling_fixed_points(signal, target_points):
    """
    对一维信号进行平均降采样，以得到固定数量的数据点。

    参数:
    signal (numpy.ndarray): 输入的一维NumPy数组。
    target_points (int): 目标数据点数量。

    返回:
    numpy.ndarray: 降采样后的一维NumPy数组，包含target_points个数据点。
    """
    # 检查target_points是否为正整数
    if not isinstance(target_points, int) or target_points <= 0:
        raise ValueError("target_points must be a positive integer")

    # 计算需要的降采样因子
    scale_factor = len(signal) // target_points

    # 如果计算出的scale_factor为0，说明输入信号太短，无法达到目标点数
    if scale_factor == 0:
        raise ValueError("Input signal is too short to reach the target number of points")
    signal = np.array(signal).reshape(-1, 1)
    # 计算每个块的平均值
    downsampled_signal = signal[::scale_factor].mean(axis=1)

    return downsampled_signal



class AudioSignalChart(QMainWindow):
    def __init__(self, fpath=""):
        super().__init__()
        self.min_amp = None
        self.max_amp = None
        self.line = None
        self.cursor = None
        self.audio = None
        self.fpath = fpath
        self.series = QLineSeries()
        self.update_chart()

        # self.series.append(0, 6)
        # self.series.append(QPointF(20, 2))

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        # self._chart.createDefaultAxes()
        # self._chart.axisX().setLabelsVisible(False)
        # self._chart.axisY().setLabelsVisible(False)

        # self._chart.setTitle("Simple line _chart example")
        self.chart.setContentsMargins(QMargins(0, 0, 0, 0))

        self._chart_view = QChartView(self.chart)
        # self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._chart_view.setContentsMargins(QMargins(0, 0, 0, 0))

        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setCentralWidget(self._chart_view)



    def mousePressEvent(self, event):
        # 获取鼠标点击的位置
        point = event.position().toPoint()
        print(point)

        # 在点击位置添加竖着的红线
        self.addVerticalLine()
        super().mousePressEvent(event)
        event.accept()


    def addVerticalLine(self):

        self.chart.removeAllSeries()
        selected_series = QLineSeries()
        print(self.max_amp, self.min_amp)
        selected_series.append(2, 100)
        selected_series.append(2, -100)
        pen = QPen(Qt.red)
        pen.setWidth(2)
        selected_series.setPen(pen)
        self.chart.addSeries(selected_series)
        print(self.chart)
        self.chart.setContentsMargins(QMargins(0, 0, 0, 0))

        self._chart_view = QChartView(self.chart)
        # self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._chart_view.setContentsMargins(QMargins(0, 0, 0, 0))

        self.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setCentralWidget(self._chart_view)
        # self._chart_view.scene().removeItem(self.line)
        # # 创建QGraphicsLineItem对象
        # self.line = QGraphicsLineItem()
        # # print(x)
        # # 设置线的起点和终点
        # self.line.setLine(x, self._chart.plotArea().top(), x, self._chart.plotArea().bottom())
        # # 设置线的颜色和样式

        # # 将线添加到场景中
        # self._chart_view.scene().addItem(self.line)



    def update_chart(self):
        print(self.fpath)
        if self.fpath:
            audio = AudioSegment.from_wav(self.fpath).split_to_mono()[0].get_array_of_samples()#[50000:70000]
        else:
            audio = AudioSegment.from_wav(r"/audio/test.wav").split_to_mono()[0].get_array_of_samples()#[50000:55000]
        self.max_amp, self.min_amp = max(audio), min(audio)
        self.audio = audio
        self.thumbnail()
        timepoint = [i for i in range(len(self.audio))]
        # 将数组数据一次性添加到序列中
        points = [(x, y) for x, y in zip(timepoint, self.audio)]

        for p in points:
            self.series.append(*p)

    def thumbnail(self):
        self.audio = mean_downsampling_fixed_points(self.audio, 50000)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AudioSignalChart()
    window.show()
    window.resize(800, 300)
    sys.exit(app.exec())