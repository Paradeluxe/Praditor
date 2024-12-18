from PySide6.QtWidgets import QGridLayout, QApplication, QMainWindow, QWidget

from slider.slider_single import SingleSlider


class MySliders(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle('Slider App')

        self.amp_slider_onset = SingleSlider("Threshold", 100, 1, 300, scale=0.01, default=147)
        self.cutoff0_slider_onset = SingleSlider("HighPass", 1, 1, 500, default=60, font_color="#7F7F7F")
        self.cutoff1_slider_onset = SingleSlider("LowPass", 8000, 1, 20000, default=10800, font_color="#7F7F7F")
        self.numValid_slider_onset = SingleSlider("CountValid", 0, 1, 8000, default=475)
        self.win_size_slider_onset = SingleSlider("KernelSize", 2, 1, 500, default=152)
        self.ratio_slider_onset = SingleSlider("KernelFrm%", 50, 1, 100, scale=0.01, default=97)
        self.penalty_slider_onset = SingleSlider("Penalty", 0, 1, 200, scale=0.1, default=147)
        self.ref_len_slider_onset = SingleSlider("RefLen", 1, 1, 2000, default=1000, font_color="#7F7F7F")
        self.eps_ratio_slider_onset = SingleSlider("EPS%", 0, 1, 100, scale=0.001, default=20, font_color="#7F7F7F")

        self.amp_slider_offset = SingleSlider("", 100, 1, 300, scale=0.01, color="#2AD25E", default=194)
        self.cutoff0_slider_offset = SingleSlider("", 1, 1, 500, color="#2AD25E", default=200)
        self.cutoff1_slider_offset = SingleSlider("", 8000, 1, 20000, color="#2AD25E", default=10200)
        self.numValid_slider_offset = SingleSlider("", 0, 1, 8000, color="#2AD25E", default=3335)
        self.win_size_slider_offset = SingleSlider("", 2, 1, 500, color="#2AD25E", default=102)
        self.ratio_slider_offset = SingleSlider("", 50, 1, 100, scale=0.01, color="#2AD25E", default=87)
        self.penalty_slider_offset = SingleSlider("", 0, 1, 200, scale=0.1, color="#2AD25E", default=108)
        self.ref_len_slider_offset = SingleSlider("", 1, 1, 2000, color="#2AD25E", default=1000)
        self.eps_ratio_slider_offset = SingleSlider("", 0, 1, 100, scale=0.001, color="#2AD25E", default=15)

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(75, 0, 75, 0)

        layout.addWidget(self.amp_slider_onset, 0, 0)
        layout.addWidget(self.numValid_slider_onset, 1, 0)
        layout.addWidget(self.ref_len_slider_onset, 2, 0)
        
        layout.addWidget(self.ratio_slider_onset, 3, 0)
        layout.addWidget(self.win_size_slider_onset, 4, 0)
        layout.addWidget(self.penalty_slider_onset, 5, 0)

        layout.addWidget(self.eps_ratio_slider_onset, 6, 0)
        layout.addWidget(self.cutoff0_slider_onset, 7, 0)
        layout.addWidget(self.cutoff1_slider_onset, 8, 0)


        layout.addWidget(self.amp_slider_offset, 0, 1)
        layout.addWidget(self.numValid_slider_offset, 1, 1)
        layout.addWidget(self.ref_len_slider_offset, 2, 1)

        layout.addWidget(self.ratio_slider_offset, 3, 1)
        layout.addWidget(self.win_size_slider_offset, 4, 1)
        layout.addWidget(self.penalty_slider_offset, 5, 1)

        layout.addWidget(self.eps_ratio_slider_offset, 6, 1)
        layout.addWidget(self.cutoff0_slider_offset, 7, 1)
        layout.addWidget(self.cutoff1_slider_offset, 8, 1)


        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
        # self.get_params()


    def getParams(self):
        params = {
            "onset": {
                "amp": self.amp_slider_onset.value_label.text(),
                "cutoff0": self.cutoff0_slider_onset.value_label.text(),
                "cutoff1": self.cutoff1_slider_onset.value_label.text(),
                "numValid": self.numValid_slider_onset.value_label.text(),
                "win_size": self.win_size_slider_onset.value_label.text(),
                "ratio": self.ratio_slider_onset.value_label.text(),
                "penalty": self.penalty_slider_onset.value_label.text(),
                "ref_len": self.ref_len_slider_onset.value_label.text(),
                "eps_ratio": self.eps_ratio_slider_onset.value_label.text()

            },

            "offset": {
                "amp": self.amp_slider_offset.value_label.text(),
                "cutoff0": self.cutoff0_slider_offset.value_label.text(),
                "cutoff1": self.cutoff1_slider_offset.value_label.text(),
                "numValid": self.numValid_slider_offset.value_label.text(),
                "win_size": self.win_size_slider_offset.value_label.text(),
                "ratio": self.ratio_slider_offset.value_label.text(),
                "penalty": self.penalty_slider_offset.value_label.text(),
                "ref_len": self.ref_len_slider_offset.value_label.text(),
                "eps_ratio": self.eps_ratio_slider_offset.value_label.text()

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