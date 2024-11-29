'''
Pyside6中提供的QSplitter控件的使用案例。
'''
import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from button.param_button import ParamButtons, OnOnffCheckBoxs
# from pyplot.pyplot_window import AudioSignalChart
from slider.slider_section import MySliders
from test import AudioPlot


class MySplitter(QWidget):
    def __init__(self, fpath=""):
        super().__init__()

        # 用于保存此段代码中创建的几个QSplitter控件的状态的字典变量
        self.setting = {}

        # 创建一个垂直布局对象，作为顶层布局
        layout = QVBoxLayout(self)

        self.audio_chart = AudioPlot()
        # self.audio_chart.setMinimumSize(600, 200)

        layout.addWidget(self.audio_chart)

        layout.addWidget(ParamButtons())

        self.param_sliders_splitter = QSplitter()
        self.param_sliders_splitter.addWidget(MySliders())
        layout.addWidget(self.param_sliders_splitter)


        # layout.addWidget(OnOnffCheckBoxs())

        # 把顶层布局添加到窗口中
        self.setLayout(layout)

    # 保存4个QSplitter的大小状态
    def saveSetting(self):
        self.setting.update({"splitter1": self.splitter1.saveState()})
        self.setting.update({"splitter2": self.splitter2.saveState()})

    # 恢复保存起来的4个QSplitter的大小状态
    def restoreSetting(self):
        self.splitter1.restoreState(self.setting["splitter1"])
        self.splitter2.restoreState(self.setting["splitter2"])

    # 响应执行按钮的槽函数，隐藏或显示文本框控件，则文本框隐藏后，空出来的空间将分配到其他控件上
    def buttonShowClick(self, button):
        if button.isChecked():
            self.lineEdit.show()
        else:
            self.lineEdit.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SplitterExample()
    demo.show()
    demo.saveSetting()
    sys.exit(app.exec())
