import sys

import matplotlib
import matplotlib.style as mplstyle
from PySide6.QtCore import Qt
from pydub import AudioSegment

mplstyle.use('fast')
matplotlib.use('QtAgg')  # 指定渲染后端

matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
matplotlib.rcParams['agg.path.chunksize'] = 100000
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

def audio_arr_with_time_range(path: str, start_time: int, duration: int):
    this_audio = AudioSegment.from_wav(path)
    # print(this_audio.frame_rate)
    this_arr = this_audio[start_time:start_time+duration].split_to_mono()[0].get_array_of_samples()

    return this_arr



class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=10, height=4, dpi=300):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#000000")
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

        self.axes.set_axis_off()
        fig.tight_layout()


        # self.axes.set_xticks([])
        # self.axes.set_yticks([])
        #
        # self.axes.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        # self.axes.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)


class AudioPlot(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Interactive Matplotlib in PySide6")
        # self.resize(800, 600)

        self.canvas = MplCanvas(self, width=10, height=4, dpi=150)

        # audio = AudioSegment.from_wav("test.wav").split_to_mono()[0].get_array_of_samples()
        # print(audio)
        self.canvas.axes.plot(
            audio_arr_with_time_range(r"/audio/test.wav", 50000, 1000),
            color="white",
            linewidth=0.8
        )#[10, 1, 20, 3, 40])

        # self.toolbar.toolmanager.remove_tool('forward')
        # only display the buttons we need
        # toolitems = [t for t in NavigationToolbar2GTKAgg.toolitems if
        #              t[0] in ('Home', 'Pan', 'Zoom', 'Save')]
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=False)
        layout.addWidget(self.toolbar, alignment=Qt.AlignmentFlag.AlignCenter)

        widget = QWidget()
        widget.setLayout(layout)

        widget.setStyleSheet("""

            QWidget {
                background-color: white;
            }

        """)


        self.setCentralWidget(widget)





if __name__ == '__main__':


    app = QApplication(sys.argv)
    mainWin = AudioPlot()
    mainWin.show()
    sys.exit(app.exec())