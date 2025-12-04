from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QGridLayout, QApplication, QMainWindow, QWidget, QLabel

from src.gui.slider_single import SingleSlider


class MySliders(QWidget):
    anySliderValueChanged = Signal(bool)

    def __init__(self):
        super().__init__()

        # 创建滑块实例，移除param_name参数
        self.amp_slider_onset = SingleSlider(100, 1, 300, scale=0.01, default=147)
        self.cutoff0_slider_onset = SingleSlider(1, 1, 500, default=60)
        self.cutoff1_slider_onset = SingleSlider(4000, 1, 20000, default=10800)
        self.numValid_slider_onset = SingleSlider(0, 1, 8000, default=475)
        self.win_size_slider_onset = SingleSlider(2, 1, 500, default=152)
        self.ratio_slider_onset = SingleSlider(50, 1, 100, scale=0.01, default=97)
        self.penalty_slider_onset = SingleSlider(0, 1, 200, scale=0.1, default=147)
        self.ref_len_slider_onset = SingleSlider(1, 1, 2000, default=1000)
        self.eps_ratio_slider_onset = SingleSlider(0, 1, 300, scale=0.001, default=20)

        self.amp_slider_offset = SingleSlider(100, 1, 300, scale=0.01, color="#2AD25E", default=194)
        self.cutoff0_slider_offset = SingleSlider(1, 1, 500, color="#2AD25E", default=200)
        self.cutoff1_slider_offset = SingleSlider(4000, 1, 20000, color="#2AD25E", default=10200)
        self.numValid_slider_offset = SingleSlider(0, 1, 8000, color="#2AD25E", default=3335)
        self.win_size_slider_offset = SingleSlider(2, 1, 500, color="#2AD25E", default=102)
        self.ratio_slider_offset = SingleSlider(50, 1, 100, scale=0.01, color="#2AD25E", default=87)
        self.penalty_slider_offset = SingleSlider(0, 1, 200, scale=0.1, color="#2AD25E", default=108)
        self.ref_len_slider_offset = SingleSlider(1, 1, 2000, color="#2AD25E", default=1000)
        self.eps_ratio_slider_offset = SingleSlider(0, 1, 300, scale=0.001, color="#2AD25E", default=15)

        layout = QGridLayout()
        layout.setHorizontalSpacing(25)  # 增加水平间距，使onset和offset sliders之间距离更大
        layout.setVerticalSpacing(5)    # 保持垂直间距
        layout.setContentsMargins(0, 0, 0, 0)  # 调整左右边距，与AudioViewer保持一致
        
        # 设置列宽，确保onset和offset sliders尺寸一致
        layout.setColumnStretch(1, 1)  # onset sliders列
        layout.setColumnStretch(2, 1)  # offset sliders列

        # 创建名称标签并添加到第一列
        self.name_labels = {
            "Threshold": QLabel("Threshold"),
            "NetActive": QLabel("NetActive"),
            "Penalty": QLabel("Penalty"),
            "RefLen": QLabel("RefLen"),
            "KernelFrm%": QLabel("KernelFrm%"),
            "KernelSize": QLabel("KernelSize"),
            "EPS%": QLabel("EPS%"),
            "LowPass": QLabel("LowPass"),
            "HighPass": QLabel("HighPass")
        }

        # 设置标签样式
        for label in self.name_labels.values():
            label.setFixedWidth(100)  # 增加宽度，增大name label和slider之间的距离
            label.setFixedHeight(25)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    background-color: RGB(35, 35, 35);
                    font-weight: bold;
                    color: #272727;
                }
            """)

        # 添加标签到第一列，滑块到第二列和第三列
        layout.addWidget(self.name_labels["Threshold"], 0, 0)
        layout.addWidget(self.amp_slider_onset, 0, 1)
        layout.addWidget(self.amp_slider_offset, 0, 2)

        layout.addWidget(self.name_labels["NetActive"], 1, 0)
        layout.addWidget(self.numValid_slider_onset, 1, 1)
        layout.addWidget(self.numValid_slider_offset, 1, 2)

        layout.addWidget(self.name_labels["Penalty"], 2, 0)
        layout.addWidget(self.penalty_slider_onset, 2, 1)
        layout.addWidget(self.penalty_slider_offset, 2, 2)

        layout.addWidget(self.name_labels["RefLen"], 3, 0)
        layout.addWidget(self.ref_len_slider_onset, 3, 1)
        layout.addWidget(self.ref_len_slider_offset, 3, 2)

        layout.addWidget(self.name_labels["KernelFrm%"], 4, 0)
        layout.addWidget(self.ratio_slider_onset, 4, 1)
        layout.addWidget(self.ratio_slider_offset, 4, 2)

        layout.addWidget(self.name_labels["KernelSize"], 5, 0)
        layout.addWidget(self.win_size_slider_onset, 5, 1)
        layout.addWidget(self.win_size_slider_offset, 5, 2)

        layout.addWidget(self.name_labels["EPS%"], 6, 0)
        layout.addWidget(self.eps_ratio_slider_onset, 6, 1)
        layout.addWidget(self.eps_ratio_slider_offset, 6, 2)

        layout.addWidget(self.name_labels["LowPass"], 7, 0)
        layout.addWidget(self.cutoff1_slider_onset, 7, 1)
        layout.addWidget(self.cutoff1_slider_offset, 7, 2)

        layout.addWidget(self.name_labels["HighPass"], 8, 0)
        layout.addWidget(self.cutoff0_slider_onset, 8, 1)
        layout.addWidget(self.cutoff0_slider_offset, 8, 2)

        
        self.amp_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.numValid_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.ref_len_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.ratio_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.win_size_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.penalty_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.eps_ratio_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.cutoff0_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.cutoff1_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        
        
        self.amp_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.numValid_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.ref_len_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.ratio_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.win_size_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.penalty_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.eps_ratio_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.cutoff0_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.cutoff1_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        
        

        # 直接设置布局，不使用container和setCentralWidget
        self.setLayout(layout)
        # self.get_params()

    
    def sliderValueDidChange(self):
        self.anySliderValueChanged.emit(1)
    

    def getParams(self):
        params = {
            "onset": {
                "amp": self.amp_slider_onset.value_edit.text(),
                "cutoff0": self.cutoff0_slider_onset.value_edit.text(),
                "cutoff1": self.cutoff1_slider_onset.value_edit.text(),
                "numValid": self.numValid_slider_onset.value_edit.text(),
                "win_size": self.win_size_slider_onset.value_edit.text(),
                "ratio": self.ratio_slider_onset.value_edit.text(),
                "penalty": self.penalty_slider_onset.value_edit.text(),
                "ref_len": self.ref_len_slider_onset.value_edit.text(),
                "eps_ratio": self.eps_ratio_slider_onset.value_edit.text()

            },

            "offset": {
                "amp": self.amp_slider_offset.value_edit.text(),
                "cutoff0": self.cutoff0_slider_offset.value_edit.text(),
                "cutoff1": self.cutoff1_slider_offset.value_edit.text(),
                "numValid": self.numValid_slider_offset.value_edit.text(),
                "win_size": self.win_size_slider_offset.value_edit.text(),
                "ratio": self.ratio_slider_offset.value_edit.text(),
                "penalty": self.penalty_slider_offset.value_edit.text(),
                "ref_len": self.ref_len_slider_offset.value_edit.text(),
                "eps_ratio": self.eps_ratio_slider_offset.value_edit.text()

            }

        }

        # print(params)
        return params


    def resetParams(self, params):
        self.amp_slider_onset.param_slider.setValue(round(eval(params["onset"]["amp"]) / self.amp_slider_onset.scale))
        self.cutoff0_slider_onset.param_slider.setValue(round(eval(params["onset"]["cutoff0"]) / self.cutoff0_slider_onset.scale))
        self.cutoff1_slider_onset.param_slider.setValue(round(eval(params["onset"]["cutoff1"]) / self.cutoff1_slider_onset.scale))
        self.numValid_slider_onset.param_slider.setValue(round(eval(params["onset"]["numValid"]) / self.numValid_slider_onset.scale))
        self.win_size_slider_onset.param_slider.setValue(round(eval(params["onset"]["win_size"]) / self.win_size_slider_onset.scale))
        self.ratio_slider_onset.param_slider.setValue(round(eval(params["onset"]["ratio"]) / self.ratio_slider_onset.scale))
        self.penalty_slider_onset.param_slider.setValue(round(eval(params["onset"]["penalty"]) / self.penalty_slider_onset.scale))
        self.ref_len_slider_onset.param_slider.setValue(round(eval(params["onset"]["ref_len"]) / self.ref_len_slider_onset.scale))
        self.eps_ratio_slider_onset.param_slider.setValue(round(eval(params["onset"]["eps_ratio"]) / self.eps_ratio_slider_onset.scale))

        self.amp_slider_offset.param_slider.setValue(round(eval(params["offset"]["amp"]) / self.amp_slider_offset.scale))
        self.cutoff0_slider_offset.param_slider.setValue(round(eval(params["offset"]["cutoff0"]) / self.cutoff0_slider_offset.scale))
        self.cutoff1_slider_offset.param_slider.setValue(round(eval(params["offset"]["cutoff1"]) / self.cutoff1_slider_offset.scale))
        self.numValid_slider_offset.param_slider.setValue(round(eval(params["offset"]["numValid"]) / self.numValid_slider_offset.scale))
        self.win_size_slider_offset.param_slider.setValue(round(eval(params["offset"]["win_size"]) / self.win_size_slider_offset.scale))
        self.ratio_slider_offset.param_slider.setValue(round(eval(params["offset"]["ratio"]) / self.ratio_slider_offset.scale))
        self.penalty_slider_offset.param_slider.setValue(round(eval(params["offset"]["penalty"]) / self.penalty_slider_offset.scale))
        self.ref_len_slider_offset.param_slider.setValue(round(eval(params["offset"]["ref_len"]) / self.ref_len_slider_offset.scale))
        self.eps_ratio_slider_offset.param_slider.setValue(round(eval(params["offset"]["eps_ratio"]) / self.eps_ratio_slider_offset.scale))

        
        
if __name__ == '__main__':
    app = QApplication()
    ins = MySliders()
    ins.show()
    app.exec()