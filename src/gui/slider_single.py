from PySide6.QtCore import Qt, QMargins, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSlider, QHBoxLayout, \
    QWidget, QLabel)

from src.gui.styles import qss_slider_with_color


class SingleSlider(QWidget):
    single_slider_value_changed = Signal(int)

    def __init__(self, minimum, step, maximum, color="#1991D3", scale=1, default=None):
        super().__init__()
        self.scale = scale
        try:
            self.digit = len(str(self.scale).split(".")[1])
        except IndexError:
            self.digit = 0
        
        self.setFixedHeight(35)
        
        # 设置主布局为水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)  # 减小slider和值label之间的距离
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.param_slider = QSlider(Qt.Orientation.Horizontal)
        self.param_slider.setFixedHeight(20)
        self.param_slider.setMinimum(minimum)
        self.param_slider.setSingleStep(step)
        self.param_slider.setMaximum(maximum)
        self.param_slider.valueChanged.connect(self.slider_value_changed)
        
        # #2AD25E #1991D3
        self.param_slider.setStyleSheet(qss_slider_with_color(color))
        
        self.value_label = QLabel(f"{self.param_slider.sliderPosition()}")
        self.value_label.setFixedWidth(50)
        self.value_label.setFixedHeight(25)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                background-color: RGB(35, 35, 35);
                color: #272727;
            }
        """)

        if default is not None:
            self.param_slider.setValue(default)
            self.value_label.setText(f"{(self.param_slider.sliderPosition() * self.scale):.{self.digit}f}")

        # 将滑块和标签添加到布局中
        layout.addWidget(self.param_slider)
        layout.addWidget(self.value_label)
        
        # 设置组件的布局
        self.setLayout(layout)




    def slider_value_changed(self):


        self.value_label.setText(f"{(self.param_slider.sliderPosition() * self.scale):.{self.digit}f}")
        self.single_slider_value_changed.emit(1)





if __name__ == '__main__':
    app = QApplication()
    ins = SingleSlider("default_slider", 1, 1, 100)
    ins.show()
    app.exec()