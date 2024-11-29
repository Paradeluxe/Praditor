from PySide6.QtCore import Qt, QMargins
from PySide6.QtWidgets import (
    QGridLayout, QApplication, QLayout, QMainWindow, QSlider, QVBoxLayout, QHBoxLayout, \
    QWidget, QLabel)

from QSS import qss_slider_with_color


class SingleSlider(QMainWindow):
    def __init__(self, param_name, minimum, step, maximum, color="#1991D3", scale=1, default=None):
        super().__init__()
        # self.setWindowTitle('Slider App')
        self.scale = scale
        try:
            self.digit = len(str(self.scale).split(".")[1])
        except IndexError:
            self.digit = 0
        self.setMaximumHeight(40)


        self.name_label = QLabel(param_name)
        self.name_label.setFixedSize(90, 20)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.name_label.setStyleSheet("""

            QLabel {
                font-size: 14px;
                background-color: RGB(35, 35, 35);
                font-weight: bold;
                color: #272727;
            }


        """)

        # QLabel
        # {
        #     font - size: 14px;
        # background - color: RGB(35, 35, 35);
        # font - weight: bold;
        # color:  # 272727;
        # }

        self.param_slider = QSlider(Qt.Orientation.Horizontal)
        self.param_slider.setFixedHeight(20)
        self.param_slider.setMinimum(minimum)
        self.param_slider.setSingleStep(step)
        self.param_slider.setMaximum(maximum)
        # self.param_slider.setMinimumHeight(20)
        self.param_slider.valueChanged.connect(self.slider_value_changed)
        # self.param_slider.grab()

        # #2AD25E #1991D3
        self.param_slider.setStyleSheet(qss_slider_with_color(color))



        # self.param_slider.sliderMoved.connect(slider_mouse_changed)
        # self.param_slider.sliderPressed.connect(self.slider_pressed_h)
        # self.param_slider.sliderReleased.connect(self.slider_released_h)

        self.value_label = QLabel(f"{self.param_slider.sliderPosition()}")
        self.value_label.setFixedSize(50, 20)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_label.setStyleSheet("""

            QLabel {
                font-size: 14px;
                background-color: RGB(35, 35, 35);
                color: #272727;
            }


        """)

        if default is not None:
            self.param_slider.setValue(default)
            self.value_label.setText(f"{(self.param_slider.sliderPosition() * self.scale):.{self.digit}f}")




        layout = QHBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.param_slider)
        layout.addWidget(self.value_label)
        container = QWidget()
        container.setLayout(layout)


        self.setCentralWidget(container)
        self.setContentsMargins(QMargins(0, 0, 0, 0))

    def slider_value_changed(self):


        self.value_label.setText(f"{(self.param_slider.sliderPosition() * self.scale):.{self.digit}f}")





if __name__ == '__main__':
    app = QApplication()
    ins = SingleSlider("default_slider", 1, 1, 100)
    ins.show()
    app.exec()