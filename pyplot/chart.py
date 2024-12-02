import sys

from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtWidgets import QApplication, QWidget
from pydub import AudioSegment


class PlotAudio(QWidget):

    def __init__(self, fpath=""):
        super().__init__()
        self.audio_obj = None


        self.fpath = fpath
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)

        self.chart.legend().hide()
        self.chart_view = QChartView(self.chart)
        # --------------------------------------------
        # --------------------------------------------


        self.setStyleSheet("""

                    QWidget {
                        background-color: RGB(35, 35, 35);
                        color: white;
                        font-weight: bold;
                    }


                """)

    def readAudio(self, new_path):
        # Always get the first channel
        self.audio_obj = AudioSegment.from_wav(new_path).split_to_mono()[0]



    def update_chart(self, new_path):

        timepoint = [i for i in range(len(self.thumbnail))]
        # 将数组数据一次性添加到序列中
        points = [(x, y) for x, y in zip(timepoint, self.thumbnail)]

        for p in points:
            this_series.append(*p)







if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PlotAudio(r"C:\Users\18357\Desktop\Py_GUI\test.wav")
    window.show()
    window.resize(800, 300)
    sys.exit(app.exec())