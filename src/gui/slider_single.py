from PySide6.QtCore import Qt, QMargins, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSlider, QHBoxLayout, \
    QWidget, QLineEdit)

from src.gui.styles import qss_slider_with_color


class SingleSlider(QWidget):
    single_slider_value_changed = Signal(int)

    def __init__(self, minimum, step, maximum, color="#1991D3", scale=1, default=None, tooltip=None):
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
        layout.setSpacing(10)  # 减小slider和值label之间的距离
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.param_slider = QSlider(Qt.Orientation.Horizontal)
        self.param_slider.setFixedHeight(20)
        self.param_slider.setMinimum(minimum)
        self.param_slider.setSingleStep(step)
        self.param_slider.setMaximum(maximum)
        self.param_slider.valueChanged.connect(self.slider_value_changed)
        
        # 添加tooltip
        if tooltip:
            self.param_slider.setToolTip(tooltip)
        
        # #2AD25E #1991D3
        self.param_slider.setStyleSheet(qss_slider_with_color(color))
        
        self.value_edit = QLineEdit(f"{self.param_slider.sliderPosition()}")
        self.value_edit.setFixedWidth(50)
        self.value_edit.setFixedHeight(25)
        self.value_edit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_edit.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                background-color: transparent;
                color: black;
                border: none;
            }
            QLineEdit:focus {
                border: none;
                background-color: white;
            }
        """)
        self.value_edit.editingFinished.connect(self.edit_value_changed)

        if default is not None:
            self.param_slider.setValue(default)
            self.value_edit.setText(f"{(self.param_slider.sliderPosition() * self.scale):.{self.digit}f}")

        # 将滑块和编辑框添加到布局中
        layout.addWidget(self.param_slider)
        layout.addWidget(self.value_edit)
        
        # 设置组件的布局
        self.setLayout(layout)

    def slider_value_changed(self):
        self.value_edit.setText(f"{(self.param_slider.sliderPosition() * self.scale):.{self.digit}f}")
        self.single_slider_value_changed.emit(1)

    def edit_value_changed(self):
        try:
            # 获取用户输入的值
            input_value = float(self.value_edit.text())
            # 将输入值转换为滑块位置
            slider_pos = round(input_value / self.scale)
            
            # 确保滑块位置在有效范围内
            slider_pos = max(self.param_slider.minimum(), min(self.param_slider.maximum(), slider_pos))
            
            # 更新滑块位置
            self.param_slider.setValue(slider_pos)
            
            # 更新显示值（确保显示的是滑块实际位置对应的值）
            self.value_edit.setText(f"{(slider_pos * self.scale):.{self.digit}f}")
            
            # 发出值已更改的信号
            self.single_slider_value_changed.emit(1)
        except ValueError:
            # 如果输入无效，恢复为当前滑块位置对应的值
            current_value = self.param_slider.sliderPosition() * self.scale
            self.value_edit.setText(f"{current_value:.{self.digit}f}")





if __name__ == '__main__':
    app = QApplication()
    ins = SingleSlider("default_slider", 1, 1, 100)
    ins.show()
    app.exec()