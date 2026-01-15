from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QGridLayout, QApplication, QMainWindow, QWidget, QLabel

from src.gui.slider_single import SingleSlider


class MySliders(QWidget):
    anySliderValueChanged = Signal(bool)

    def __init__(self):
        super().__init__()

        # 创建滑块实例，移除param_name参数
        self.amp_slider_onset = SingleSlider(100, 1, 300, scale=0.01, default=147, tooltip="Onset | Threshold for detecting onset")
        self.cutoff0_slider_onset = SingleSlider(1, 1, 500, default=60, tooltip="Onset | Lower cutoff frequency of bandpass filter")
        self.cutoff1_slider_onset = SingleSlider(4000, 1, 20000, default=10800, tooltip="Onset | Higher cutoff frequency of bandpass filter")
        self.numValid_slider_onset = SingleSlider(0, 1, 8000, default=475, tooltip="Onset | NetActive | Minimum number of valid frames to trigger onset")
        self.win_size_slider_onset = SingleSlider(2, 1, 500, default=152, tooltip="Onset | KernelSize | Size of the kernel (in frames)")
        self.ratio_slider_onset = SingleSlider(50, 1, 100, scale=0.01, default=97, tooltip="Onset | KernelFrm% | % of frames retained in the kernel")
        self.penalty_slider_onset = SingleSlider(0, 1, 200, scale=0.1, default=147, tooltip="Onset | Penalty for below-threshold frames")
        self.ref_len_slider_onset = SingleSlider(1, 1, 2000, default=1000, tooltip="Onset | RefLen | Length of the reference segment used to generate baseline")
        self.eps_ratio_slider_onset = SingleSlider(0, 1, 300, scale=0.001, default=20, tooltip="Onset | EPS% | Neighborhood radius in DBSCAN clustering")

        self.amp_slider_offset = SingleSlider(100, 1, 300, scale=0.01, color="#2AD25E", default=194, tooltip="Offset | Threshold for detecting offset")
        self.cutoff0_slider_offset = SingleSlider(1, 1, 500, color="#2AD25E", default=200, tooltip="Offset | Lower cutoff frequency of bandpass filter")
        self.cutoff1_slider_offset = SingleSlider(4000, 1, 20000, color="#2AD25E", default=10200, tooltip="Offset | Higher cutoff frequency of bandpass filter")
        self.numValid_slider_offset = SingleSlider(0, 1, 8000, color="#2AD25E", default=3335, tooltip="Offset | NetActive | Minimum number of valid frames to trigger offset")
        self.win_size_slider_offset = SingleSlider(2, 1, 500, color="#2AD25E", default=102, tooltip="Offset | KernelSize | Size of the kernel (in frames)")
        self.ratio_slider_offset = SingleSlider(50, 1, 100, scale=0.01, color="#2AD25E", default=87, tooltip="Offset | KernelFrm% | % of frames retained in the kernel")
        self.penalty_slider_offset = SingleSlider(0, 1, 200, scale=0.1, color="#2AD25E", default=108, tooltip="Offset | Penalty for below-threshold frames")
        self.ref_len_slider_offset = SingleSlider(1, 1, 2000, color="#2AD25E", default=1000, tooltip="Offset | RefLen | Length of the reference segment used to generate baseline")
        self.eps_ratio_slider_offset = SingleSlider(0, 1, 300, scale=0.001, color="#2AD25E", default=15, tooltip="Offset | EPS% | Neighborhood radius in DBSCAN clustering")

        layout = QGridLayout()
        layout.setHorizontalSpacing(35)  # 增加水平间距，使onset和offset sliders之间距离更大
        layout.setVerticalSpacing(5)    # 保持垂直间距
        layout.setContentsMargins(0, 0, 0, 0)  # 调整左右边距，与AudioViewer保持一致
        
        # 设置列宽，确保onset和offset sliders尺寸一致
        layout.setColumnStretch(0, 0)  # name labels列，不拉伸
        layout.setColumnStretch(1, 1)  # onset sliders列，拉伸
        layout.setColumnStretch(2, 1)  # offset sliders列，拉伸
        layout.setColumnMinimumWidth(1, 200)  # 设置onset sliders列的最小宽度
        layout.setColumnMinimumWidth(2, 200)  # 设置offset sliders列的最小宽度，与onset列保持一致

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
            label.setFixedWidth(80)  # 减小宽度，缩小name label和slider之间的距离
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
        
        # 添加tooltip到标签
        self.name_labels["Threshold"].setToolTip("Threshold for detecting onset/offset")
        self.name_labels["NetActive"].setToolTip("Minimum number of valid frames to trigger onset/offset")
        self.name_labels["Penalty"].setToolTip("Penalty for below-threshold frames")
        self.name_labels["RefLen"].setToolTip("Length of the reference segment used to generate baseline")
        self.name_labels["KernelFrm%"].setToolTip("% of frames retained in the kernel")
        self.name_labels["KernelSize"].setToolTip("Size of the kernel (in frames)")
        self.name_labels["EPS%"].setToolTip("Neighborhood radius in DBSCAN clustering")
        self.name_labels["LowPass"].setToolTip("Lower cutoff frequency of bandpass filter")
        self.name_labels["HighPass"].setToolTip("Higher cutoff frequency of bandpass filter")
        
        # 将特定标签设置为灰色文字
        gray_labels = ["RefLen", "EPS%", "HighPass", "LowPass"]
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
            "onset": {},
            "offset": {}
        }
        
        # 检查Onset滑块可见性并添加参数
        if self.amp_slider_onset.isVisible():
            params["onset"]["amp"] = self.amp_slider_onset.value_edit.text()
        if self.cutoff0_slider_onset.isVisible():
            params["onset"]["cutoff0"] = self.cutoff0_slider_onset.value_edit.text()
        if self.cutoff1_slider_onset.isVisible():
            params["onset"]["cutoff1"] = self.cutoff1_slider_onset.value_edit.text()
        if self.numValid_slider_onset.isVisible():
            params["onset"]["numValid"] = self.numValid_slider_onset.value_edit.text()
        if self.win_size_slider_onset.isVisible():
            params["onset"]["win_size"] = self.win_size_slider_onset.value_edit.text()
        if self.ratio_slider_onset.isVisible():
            params["onset"]["ratio"] = self.ratio_slider_onset.value_edit.text()
        if self.penalty_slider_onset.isVisible():
            params["onset"]["penalty"] = self.penalty_slider_onset.value_edit.text()
        if self.ref_len_slider_onset.isVisible():
            params["onset"]["ref_len"] = self.ref_len_slider_onset.value_edit.text()
        if self.eps_ratio_slider_onset.isVisible():
            params["onset"]["eps_ratio"] = self.eps_ratio_slider_onset.value_edit.text()
        
        # 检查Offset滑块可见性并添加参数
        if self.amp_slider_offset.isVisible():
            params["offset"]["amp"] = self.amp_slider_offset.value_edit.text()
        if self.cutoff0_slider_offset.isVisible():
            params["offset"]["cutoff0"] = self.cutoff0_slider_offset.value_edit.text()
        if self.cutoff1_slider_offset.isVisible():
            params["offset"]["cutoff1"] = self.cutoff1_slider_offset.value_edit.text()
        if self.numValid_slider_offset.isVisible():
            params["offset"]["numValid"] = self.numValid_slider_offset.value_edit.text()
        if self.win_size_slider_offset.isVisible():
            params["offset"]["win_size"] = self.win_size_slider_offset.value_edit.text()
        if self.ratio_slider_offset.isVisible():
            params["offset"]["ratio"] = self.ratio_slider_offset.value_edit.text()
        if self.penalty_slider_offset.isVisible():
            params["offset"]["penalty"] = self.penalty_slider_offset.value_edit.text()
        if self.ref_len_slider_offset.isVisible():
            params["offset"]["ref_len"] = self.ref_len_slider_offset.value_edit.text()
        if self.eps_ratio_slider_offset.isVisible():
            params["offset"]["eps_ratio"] = self.eps_ratio_slider_offset.value_edit.text()

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
        if "win_size" in onset_params:
            self.win_size_slider_onset.param_slider.setValue(round(eval(onset_params["win_size"]) / self.win_size_slider_onset.scale))
        if "ratio" in onset_params:
            self.ratio_slider_onset.param_slider.setValue(round(eval(onset_params["ratio"]) / self.ratio_slider_onset.scale))
        if "penalty" in onset_params:
            self.penalty_slider_onset.param_slider.setValue(round(eval(onset_params["penalty"]) / self.penalty_slider_onset.scale))
        if "ref_len" in onset_params:
            self.ref_len_slider_onset.param_slider.setValue(round(eval(onset_params["ref_len"]) / self.ref_len_slider_onset.scale))
        if "eps_ratio" in onset_params:
            self.eps_ratio_slider_onset.param_slider.setValue(round(eval(onset_params["eps_ratio"]) / self.eps_ratio_slider_onset.scale))

        # 重置Offset参数，只处理params字典中实际存在的键
        offset_params = params.get("offset", {})
        
        if "amp" in offset_params:
            self.amp_slider_offset.param_slider.setValue(round(eval(offset_params["amp"]) / self.amp_slider_offset.scale))
        if "cutoff0" in offset_params:
            self.cutoff0_slider_offset.param_slider.setValue(round(eval(offset_params["cutoff0"]) / self.cutoff0_slider_offset.scale))
        if "cutoff1" in offset_params:
            self.cutoff1_slider_offset.param_slider.setValue(round(eval(offset_params["cutoff1"]) / self.cutoff1_slider_offset.scale))
        if "numValid" in offset_params:
            self.numValid_slider_offset.param_slider.setValue(round(eval(offset_params["numValid"]) / self.numValid_slider_offset.scale))
        if "win_size" in offset_params:
            self.win_size_slider_offset.param_slider.setValue(round(eval(offset_params["win_size"]) / self.win_size_slider_offset.scale))
        if "ratio" in offset_params:
            self.ratio_slider_offset.param_slider.setValue(round(eval(offset_params["ratio"]) / self.ratio_slider_offset.scale))
        if "penalty" in offset_params:
            self.penalty_slider_offset.param_slider.setValue(round(eval(offset_params["penalty"]) / self.penalty_slider_offset.scale))
        if "ref_len" in offset_params:
            self.ref_len_slider_offset.param_slider.setValue(round(eval(offset_params["ref_len"]) / self.ref_len_slider_offset.scale))
        if "eps_ratio" in offset_params:
            self.eps_ratio_slider_offset.param_slider.setValue(round(eval(offset_params["eps_ratio"]) / self.eps_ratio_slider_offset.scale))


    def updateTooltips(self, is_vad_mode):
        """更新滑块的tooltip文本，根据是否为VAD模式"""
        if is_vad_mode:
            # VAD模式下的tooltip
            self.amp_slider_onset.param_slider.setToolTip("VAD | Threshold for detecting speech activity")
            self.cutoff0_slider_onset.param_slider.setToolTip("VAD | Lower cutoff frequency of bandpass filter")
            self.cutoff1_slider_onset.param_slider.setToolTip("VAD | Higher cutoff frequency of bandpass filter")
            self.numValid_slider_onset.param_slider.setToolTip("VAD | Minimum number of valid frames to detect speech")
            self.eps_ratio_slider_onset.param_slider.setToolTip("VAD | Neighborhood radius in DBSCAN clustering")
        else:
            # 非VAD模式下的tooltip
            self.amp_slider_onset.param_slider.setToolTip("Onset | Threshold for detecting onset")
            self.cutoff0_slider_onset.param_slider.setToolTip("Onset | Lower cutoff frequency of bandpass filter")
            self.cutoff1_slider_onset.param_slider.setToolTip("Onset | Higher cutoff frequency of bandpass filter")
            self.numValid_slider_onset.param_slider.setToolTip("Onset | NetActive | Minimum number of valid frames to trigger onset")
            self.win_size_slider_onset.param_slider.setToolTip("Onset | KernelSize | Size of the kernel (in frames)")
            self.ratio_slider_onset.param_slider.setToolTip("Onset | KernelFrm% | % of frames retained in the kernel")
            self.penalty_slider_onset.param_slider.setToolTip("Onset | Penalty for below-threshold frames")
            self.ref_len_slider_onset.param_slider.setToolTip("Onset | RefLen | Length of the reference segment used to generate baseline")
            self.eps_ratio_slider_onset.param_slider.setToolTip("Onset | EPS% | Neighborhood radius in DBSCAN clustering")
            
            # 恢复Offset滑块的tooltip
            self.amp_slider_offset.param_slider.setToolTip("Offset | Threshold for detecting offset")
            self.cutoff0_slider_offset.param_slider.setToolTip("Offset | Lower cutoff frequency of bandpass filter")
            self.cutoff1_slider_offset.param_slider.setToolTip("Offset | Higher cutoff frequency of bandpass filter")
            self.numValid_slider_offset.param_slider.setToolTip("Offset | NetActive | Minimum number of valid frames to trigger offset")
            self.win_size_slider_offset.param_slider.setToolTip("Offset | KernelSize | Size of the kernel (in frames)")
            self.ratio_slider_offset.param_slider.setToolTip("Offset | KernelFrm% | % of frames retained in the kernel")
            self.penalty_slider_offset.param_slider.setToolTip("Offset | Penalty for below-threshold frames")
            self.ref_len_slider_offset.param_slider.setToolTip("Offset | RefLen | Length of the reference segment used to generate baseline")
            self.eps_ratio_slider_offset.param_slider.setToolTip("Offset | EPS% | Neighborhood radius in DBSCAN clustering")

        
        
if __name__ == '__main__':
    app = QApplication()
    ins = MySliders()
    ins.show()
    app.exec()