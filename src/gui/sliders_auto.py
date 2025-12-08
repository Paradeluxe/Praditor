from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QGridLayout, QApplication, QMainWindow, QWidget, QLabel

from src.gui.slider_single import SingleSlider


class MySliders(QMainWindow):
    anySliderValueChanged = Signal(bool)

    def __init__(self):
        super().__init__()

        # 创建滑块实例，移除param_name参数
        self.amp_slider_onset = SingleSlider(100, 1, 300, scale=0.01, default=147, color="#999999")
        self.cutoff0_slider_onset = SingleSlider(0, 1, 500, default=60, color="#999999")
        self.cutoff1_slider_onset = SingleSlider(4000, 1, 20000, default=10800, color="#999999")
        self.numValid_slider_onset = SingleSlider(0, 1, 8000, default=475, color="#999999")
        # self.win_size_slider_onset = SingleSlider(2, 1, 500, default=152)
        # self.ratio_slider_onset = SingleSlider(50, 1, 100, scale=0.01, default=97)
        # self.penalty_slider_onset = SingleSlider(0, 1, 200, scale=0.1, default=147)
        # self.ref_len_slider_onset = SingleSlider(1, 1, 2000, default=1000)
        self.eps_ratio_slider_onset = SingleSlider(0, 1, 300, scale=0.001, default=20, color="#999999")

        # self.amp_slider_offset = SingleSlider(100, 1, 300, scale=0.01, color="#2AD25E", default=194)
        # self.cutoff0_slider_offset = SingleSlider(1, 1, 500, color="#2AD25E", default=200)
        # self.cutoff1_slider_offset = SingleSlider(4000, 1, 20000, color="#2AD25E", default=10200)
        # self.numValid_slider_offset = SingleSlider(0, 1, 8000, color="#2AD25E", default=3335)
        # # self.win_size_slider_offset = SingleSlider(2, 1, 500, color="#2AD25E", default=102)
        # # self.ratio_slider_offset = SingleSlider(50, 1, 100, scale=0.01, color="#2AD25E", default=87)
        # # self.penalty_slider_offset = SingleSlider(0, 1, 200, scale=0.1, color="#2AD25E", default=108)
        # # self.ref_len_slider_offset = SingleSlider(1, 1, 2000, color="#2AD25E", default=1000)
        # self.eps_ratio_slider_offset = SingleSlider(0, 1, 300, scale=0.001, color="#2AD25E", default=15)

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 75, 0)

        # 创建名称标签并添加到第一列
        self.name_labels = {
            "Threshold": QLabel("Threshold"),
            "NetActive": QLabel("NetActive"),
            "EPS%": QLabel("EPS%"),
            "LowPass": QLabel("LowPass"),
            "HighPass": QLabel("HighPass")
        }

        # 设置标签样式
        for label in self.name_labels.values():
            label.setFixedWidth(90)
            label.setFixedHeight(25)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            # 默认样式：黑色文字
            label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    background-color: RGB(35, 35, 35);
                    font-weight: bold;
                    color: #272727;
                }
            """)
        
        # 将特定标签设置为灰色文字
        gray_labels = ["EPS%", "HighPass", "LowPass"]
        for label_name in gray_labels:
            if label_name in self.name_labels:
                self.name_labels[label_name].setStyleSheet("""
                    QLabel {
                        font-size: 13px;
                        background-color: RGB(35, 35, 35);
                        font-weight: bold;
                        color: #888888;
                    }
                """)

        # 添加标签到第一列，滑块到第二列
        layout.addWidget(self.name_labels["Threshold"], 0, 0)
        layout.addWidget(self.amp_slider_onset, 0, 1)

        layout.addWidget(self.name_labels["NetActive"], 1, 0)
        layout.addWidget(self.numValid_slider_onset, 1, 1)

        # layout.addWidget(self.name_labels["Penalty"], 2, 0)
        # layout.addWidget(self.penalty_slider_onset, 2, 1)
        # layout.addWidget(self.name_labels["RefLen"], 3, 0)
        # layout.addWidget(self.ref_len_slider_onset, 3, 1)

        # layout.addWidget(self.name_labels["KernelFrm%"], 4, 0)
        # layout.addWidget(self.ratio_slider_onset, 4, 1)
        # layout.addWidget(self.name_labels["KernelSize"], 5, 0)
        # layout.addWidget(self.win_size_slider_onset, 5, 1)

        layout.addWidget(self.name_labels["EPS%"], 2, 0)
        layout.addWidget(self.eps_ratio_slider_onset, 2, 1)

        layout.addWidget(self.name_labels["LowPass"], 3, 0)
        layout.addWidget(self.cutoff1_slider_onset, 3, 1)

        layout.addWidget(self.name_labels["HighPass"], 4, 0)
        layout.addWidget(self.cutoff0_slider_onset, 4, 1)




        self.amp_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.numValid_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.ref_len_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.ratio_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.win_size_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.penalty_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.eps_ratio_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.cutoff0_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        self.cutoff1_slider_onset.single_slider_value_changed.connect(self.sliderValueDidChange)
        
        
        # self.amp_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.numValid_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.ref_len_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.ratio_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.win_size_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.penalty_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.eps_ratio_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.cutoff0_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        # self.cutoff1_slider_offset.single_slider_value_changed.connect(self.sliderValueDidChange)
        
        

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
        # self.get_params()

    
    def sliderValueDidChange(self):
        self.anySliderValueChanged.emit(1)
    

    def getParams(self):
        params = {
            "onset": {
                "amp": self.amp_slider_onset.value_label.text(),
                "cutoff0": self.cutoff0_slider_onset.value_label.text(),
                "cutoff1": self.cutoff1_slider_onset.value_label.text(),
                "numValid": self.numValid_slider_onset.value_label.text(),
                # "win_size": self.win_size_slider_onset.value_label.text(),
                # "ratio": self.ratio_slider_onset.value_label.text(),
                # "penalty": self.penalty_slider_onset.value_label.text(),
                # "ref_len": self.ref_len_slider_onset.value_label.text(),
                "eps_ratio": self.eps_ratio_slider_onset.value_label.text()

            },
            "offset": {
                "amp": self.amp_slider_onset.value_label.text(),
                "cutoff0": self.cutoff0_slider_onset.value_label.text(),
                "cutoff1": self.cutoff1_slider_onset.value_label.text(),
                "numValid": self.numValid_slider_onset.value_label.text(),
                # "win_size": self.win_size_slider_onset.value_label.text(),
                # "ratio": self.ratio_slider_onset.value_label.text(),
                # "penalty": self.penalty_slider_onset.value_label.text(),
                # "ref_len": self.ref_len_slider_onset.value_label.text(),
                "eps_ratio": self.eps_ratio_slider_onset.value_label.text()

            },
            # "offset": {
            #     "amp": self.amp_slider_offset.value_label.text(),
            #     "cutoff0": self.cutoff0_slider_offset.value_label.text(),
            #     "cutoff1": self.cutoff1_slider_offset.value_label.text(),
            #     "numValid": self.numValid_slider_offset.value_label.text(),
            #     # "win_size": self.win_size_slider_offset.value_label.text(),
            #     # "ratio": self.ratio_slider_offset.value_label.text(),
            #     # "penalty": self.penalty_slider_offset.value_label.text(),
            #     # "ref_len": self.ref_len_slider_offset.value_label.text(),
            #     "eps_ratio": self.eps_ratio_slider_offset.value_label.text()

            # }

        }

        # print(params)
        return params


    def resetParams(self, params):
        # 重置Onset参数，只处理params字典中实际存在的键
        onset_params = params.get("onset", {})
        
        if "amp" in onset_params:
            self.amp_slider_onset.param_slider.setValue(round(eval(onset_params["amp"]) / self.amp_slider_onset.scale))
        if "cutoff0" in onset_params:
            self.cutoff0_slider_onset.param_slider.setValue(round(eval(onset_params["cutoff0"]) / self.cutoff0_slider_onset.scale))
        if "cutoff1" in onset_params:
            self.cutoff1_slider_onset.param_slider.setValue(round(eval(onset_params["cutoff1"]) / self.cutoff1_slider_onset.scale))
        if "numValid" in onset_params:
            self.numValid_slider_onset.param_slider.setValue(round(eval(onset_params["numValid"]) / self.numValid_slider_onset.scale))
        # if "win_size" in onset_params:
        #     self.win_size_slider_onset.param_slider.setValue(round(eval(onset_params["win_size"]) / self.win_size_slider_onset.scale))
        # if "ratio" in onset_params:
        #     self.ratio_slider_onset.param_slider.setValue(round(eval(onset_params["ratio"]) / self.ratio_slider_onset.scale))
        # if "penalty" in onset_params:
        #     self.penalty_slider_onset.param_slider.setValue(round(eval(onset_params["penalty"]) / self.penalty_slider_onset.scale))
        # if "ref_len" in onset_params:
        #     self.ref_len_slider_onset.param_slider.setValue(round(eval(onset_params["ref_len"]) / self.ref_len_slider_onset.scale))
        if "eps_ratio" in onset_params:
            self.eps_ratio_slider_onset.param_slider.setValue(round(eval(onset_params["eps_ratio"]) / self.eps_ratio_slider_onset.scale))

        # 重置Offset参数，只处理params字典中实际存在的键
        offset_params = params.get("offset", {})
        
        # if "amp" in offset_params:
        #     self.amp_slider_offset.param_slider.setValue(round(eval(offset_params["amp"]) / self.amp_slider_offset.scale))
        # if "cutoff0" in offset_params:
        #     self.cutoff0_slider_offset.param_slider.setValue(round(eval(offset_params["cutoff0"]) / self.cutoff0_slider_offset.scale))
        # if "cutoff1" in offset_params:
        #     self.cutoff1_slider_offset.param_slider.setValue(round(eval(offset_params["cutoff1"]) / self.cutoff1_slider_offset.scale))
        # if "numValid" in offset_params:
        #     self.numValid_slider_offset.param_slider.setValue(round(eval(offset_params["numValid"]) / self.numValid_slider_offset.scale))
        # # if "win_size" in offset_params:
        # #     self.win_size_slider_offset.param_slider.setValue(round(eval(offset_params["win_size"]) / self.win_size_slider_offset.scale))
        # # if "ratio" in offset_params:
        # #     self.ratio_slider_offset.param_slider.setValue(round(eval(offset_params["ratio"]) / self.ratio_slider_offset.scale))
        # # if "penalty" in offset_params:
        # #     self.penalty_slider_offset.param_slider.setValue(round(eval(offset_params["penalty"]) / self.penalty_slider_offset.scale))
        # # if "ref_len" in offset_params:
        # #     self.ref_len_slider_offset.param_slider.setValue(round(eval(offset_params["ref_len"]) / self.ref_len_slider_offset.scale))
        # if "eps_ratio" in offset_params:
        #     self.eps_ratio_slider_offset.param_slider.setValue(round(eval(offset_params["eps_ratio"]) / self.eps_ratio_slider_offset.scale))

        
        
if __name__ == '__main__':
    app = QApplication()
    ins = MySliders()
    ins.show()
    app.exec()