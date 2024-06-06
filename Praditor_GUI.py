import os
import platform

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from pydub import AudioSegment

from Praditor_run import process_items_with_params
from Praditor_tool import get_frm_points_from_textgrid, isAudioFile, get_frm_points_from_01

plat = platform.system().lower()

if plat == 'windows':
    AudioSegment.ffmpeg = f".\\ffmpeg\\{plat}\\ffmpeg.exe"
elif plat == "darwin":  # macOS
    AudioSegment.ffmpeg = f".\\ffmpeg\\{plat}\\ffmpeg"
elif plat == 'linux':
    pass
else:
    pass


folder_audios = input("Tell me where you store all you audios: ")  # D:\Corpus\Project_Praditor\audio2

# Create the figure and the line that we will manipulate
fig, ax = plt.subplots(
    figsize=(12, 7)
    # facecolor='lightgrey'
)

# ax.set_title('Simple plot')
fig.canvas.manager.set_window_title('Praditor')

# adjust the main plot to make room for the sliders
fig.subplots_adjust(right=0.95, bottom=0.52, left=0.05, top=0.88)

top_line = 0.45
left_bound = 0.16
step = 0.04
color = "royalblue"
label_color = "black"
# AMP slider
axamp = fig.add_axes([left_bound, top_line, 0.2, 0.02])
amp_slider = Slider(
    ax=axamp,
    label="y1_amp_factor    ",
    valmin=1.,
    valmax=50.,
    valinit=1.,
    orientation="horizontal",
    valstep=0.01,
    color=color
)
amp_slider.label.set_color(label_color)
amp_slider.valtext.set_color(color)
# amp_slider.valtext.set_fontproperties(font_digit)

# CUTOFF range slider
axamp = fig.add_axes([left_bound, top_line - step, 0.2, 0.02])
cutoff0_slider = Slider(
    ax=axamp,
    label="Filter_Cutoff[0]    ",
    valmin=0.,
    valmax=500.,
    valinit=0.,
    orientation="horizontal",
    valstep=10.,
    color=color
)
cutoff0_slider.label.set_color(label_color)
cutoff0_slider.valtext.set_color(color)

axamp = fig.add_axes([left_bound, top_line - step * 2, 0.2, 0.02])
cutoff1_slider = Slider(
    ax=axamp,
    label="Filter_Cutoff[1]    ",
    valmin=8000.,
    valmax=20000.,
    valinit=8000.,
    orientation="horizontal",
    valstep=200,
    color=color
)
cutoff1_slider.label.set_color(label_color)
cutoff1_slider.valtext.set_color(color)

# numValid slider
axamp = fig.add_axes([left_bound, top_line - step * 3, 0.2, 0.02])
numValid_slider = Slider(
    ax=axamp,
    label="Num_ValidFrm    ",
    valmin=0.,
    valmax=8000.,
    valinit=0.,
    orientation="horizontal",
    valstep=1.,
    color=color
)
numValid_slider.label.set_color(label_color)
numValid_slider.valtext.set_color(color)

# window_size slider
axamp = fig.add_axes([left_bound, top_line - step * 4, 0.2, 0.02])
window_size_slider = Slider(
    ax=axamp,
    label="Kernel_Size    ",
    valmin=2.,
    valmax=500.,
    valinit=2.,
    orientation="horizontal",
    valstep=5,
    color=color
)
window_size_slider.label.set_color(label_color)
window_size_slider.valtext.set_color(color)

# noise ratio slider
axamp = fig.add_axes([left_bound, top_line - step * 5, 0.2, 0.02])
ratio_slider = Slider(
    ax=axamp,
    label="Signal_Ratio    ",
    valmin=.5,
    valmax=1.,
    valinit=.5,
    orientation="horizontal",
    valstep=.01,
    color=color
)
ratio_slider.label.set_color(label_color)
ratio_slider.valtext.set_color(color)

# penalty slider
axamp = fig.add_axes([left_bound, top_line - step * 6, 0.2, 0.02])
penalty_slider = Slider(
    ax=axamp,
    label="Penalty    ",
    valmin=0.,
    valmax=20.,
    valinit=0.,
    orientation="horizontal",
    valstep=.1,
    color=color
)
penalty_slider.label.set_color(label_color)
penalty_slider.valtext.set_color(color)

# ref length slider
axamp = fig.add_axes([left_bound, top_line - step * 7, 0.2, 0.02])
ref_length_slider = Slider(
    ax=axamp,
    label="Ref_Length    ",
    valmin=0.,
    valmax=2000.,
    valinit=0.,
    orientation="horizontal",
    valstep=50.,
    color=color
)
ref_length_slider.label.set_color(label_color)
ref_length_slider.valtext.set_color(color)

axamp = fig.add_axes([left_bound, top_line - step * 8, 0.2, 0.02])
eps_ratio_slider = Slider(
    ax=axamp,
    label="eps_Ratio    ",
    valmin=0.,
    valmax=.05,
    valinit=0.,
    orientation="horizontal",
    valstep=.001,
    color=color
)
eps_ratio_slider.label.set_color(label_color)
eps_ratio_slider.valtext.set_color(color)
# ------------------------------------------


top_line = 0.45
step = 0.04
left_bound = 0.43
color = "green"
# AMP slider
axamp = fig.add_axes([left_bound, top_line, 0.2, 0.02])
r_amp_slider = Slider(
    ax=axamp,
    label="",
    valmin=1.,
    valmax=2.,
    valinit=0.,
    orientation="horizontal",
    valstep=0.01,
    color=color
)
r_amp_slider.valtext.set_color(color)

# CUTOFF range slider
axamp = fig.add_axes([left_bound, top_line - step, 0.2, 0.02])
r_cutoff0_slider = Slider(
    ax=axamp,
    label="",
    valmin=0.,
    valmax=500.,
    valinit=0.,
    orientation="horizontal",
    valstep=10.,
    color=color
)
r_cutoff0_slider.valtext.set_color(color)

axamp = fig.add_axes([left_bound, top_line - step * 2, 0.2, 0.02])
r_cutoff1_slider = Slider(
    ax=axamp,
    label="",
    valmin=8000.,
    valmax=20000.,
    valinit=8000.,
    orientation="horizontal",
    valstep=200,
    color=color
)
r_cutoff1_slider.valtext.set_color(color)

# numValid slider
axamp = fig.add_axes([left_bound, top_line - step * 3, 0.2, 0.02])
r_numValid_slider = Slider(
    ax=axamp,
    label="",
    valmin=0.,
    valmax=8000.,
    valinit=0.,
    orientation="horizontal",
    valstep=5,
    color=color
)
r_numValid_slider.valtext.set_color(color)

# window_size slider
axamp = fig.add_axes([left_bound, top_line - step * 4, 0.2, 0.02])
r_window_size_slider = Slider(
    ax=axamp,
    label="",
    valmin=2.,
    valmax=500.,
    valinit=2.,
    orientation="horizontal",
    valstep=5,
    color=color
)
r_window_size_slider.valtext.set_color(color)

# noise ratio slider
axamp = fig.add_axes([left_bound, top_line - step * 5, 0.2, 0.02])
r_ratio_slider = Slider(
    ax=axamp,
    label="",
    valmin=.5,
    valmax=1.,
    valinit=.5,
    orientation="horizontal",
    valstep=.01,
    color=color
)
r_ratio_slider.valtext.set_color(color)

# penalty slider
axamp = fig.add_axes([left_bound, top_line - step * 6, 0.2, 0.02])
r_penalty_slider = Slider(
    ax=axamp,
    label="",
    valmin=0.,
    valmax=20.,
    valinit=0.,
    orientation="horizontal",
    valstep=.1,
    color=color
)
r_penalty_slider.valtext.set_color(color)

# ref length slider
axamp = fig.add_axes([left_bound, top_line - step * 7, 0.2, 0.02])
r_ref_length_slider = Slider(
    ax=axamp,
    label="",
    valmin=0.,
    valmax=2000.,
    valinit=0.,
    orientation="horizontal",
    valstep=50.,
    color=color
)
r_ref_length_slider.valtext.set_color(color)

axamp = fig.add_axes([left_bound, top_line - step * 8, 0.2, 0.02])
r_eps_ratio_slider = Slider(
    ax=axamp,
    label="",
    valmin=0.,
    valmax=.05,
    valinit=0.,
    orientation="horizontal",
    valstep=.001,
    color=color
)
r_eps_ratio_slider.valtext.set_color(color)

# ------------------------------
# ------------------------------
# ------------------------------


top_line = 0.43
left_bound = 0.75
vstep = 0.06
hstep = 0.07

axamp = fig.add_axes([left_bound, top_line, 0.06, 0.04])
prev_button = Button(
    ax=axamp,
    label="Prev"
)

axamp = fig.add_axes([left_bound + hstep, top_line, 0.06, 0.04])
confirm_button = Button(
    ax=axamp,
    label="Confirm",
    hovercolor="pink"
)

axamp = fig.add_axes([left_bound + hstep * 2, top_line, 0.06, 0.04])
next_button = Button(
    ax=axamp,
    label="Next"
)

axamp = fig.add_axes([left_bound, top_line - vstep, 0.2, 0.04])
default_config_button = Button(
    ax=axamp,
    label="DefaultConfig",
    hovercolor="pink"
)

axamp = fig.add_axes([left_bound, top_line - vstep * 2, 0.095, 0.04])
save_default_button = Button(
    ax=axamp,
    label="SaveDefault",
)

axamp = fig.add_axes([left_bound + .105, top_line - vstep * 2, 0.095, 0.04])  # +0.11
save_single_button = Button(
    ax=axamp,
    label="SaveSingle",
    hovercolor="pink"
)

axamp = fig.add_axes([0.21, top_line - step * 9, 0.1, 0.04])
show_onset_button = Button(
    ax=axamp,
    label="ShowOnset",
    hovercolor="lightblue"
)

axamp = fig.add_axes([0.49, top_line - step * 9, 0.1, 0.04])
show_offset_button = Button(
    ax=axamp,
    label="ShowOffset",
    hovercolor="lightgreen"
)


# -------------------------------------------
class RecPac:
    def __init__(self):

        self.is_show_default_config = False

        self.if_onset_visible = True
        self.if_offset_visible = False
        if self.if_offset_visible:
            show_offset_button.color = "lightgreen"
        if self.if_onset_visible:
            show_onset_button.color = "lightblue"

        self.order = 0
        self.folder_audios = folder_audios
        self.paths_audio = [os.path.join(self.folder_audios, f) for f in os.listdir(self.folder_audios) if
                            isAudioFile(f)]
        self.path_audio = self.paths_audio[self.order]
        self.path_textgrid = os.path.splitext(self.path_audio)[0] + ".TextGrid"
        self.path_txt = os.path.splitext(self.path_audio)[0] + ".txt"
        self.fname = os.path.basename(os.path.splitext(self.path_audio)[0])

        self.show_current_audio_arr()

        self.onset_vlines = None
        self.offset_vlines = None
        try:
            self.draw_vlines(get_frm_points_from_textgrid(self.path_textgrid))
        except AttributeError:
            self.draw_vlines(get_frm_points_from_01(self.path_textgrid))

        # standard answer
        self.folder_golden_answer = r"C:\Users\18357\PycharmProjects\RecPac_6\golden_ans"  # r".\golden_ans"
        try:
            self.draw_golden_vlines(
                get_frm_points_from_textgrid(os.path.join(self.folder_golden_answer, self.fname + ".TextGrid")))
        except AttributeError:
            self.draw_golden_vlines(
                get_frm_points_from_01(os.path.join(self.folder_golden_answer, self.fname + ".TextGrid")))

        # 默认的config display
        self.show_current_config()

    def show_single_config(self):
        self.is_show_default_config = not self.is_show_default_config
        default_config_button.label.set_text("SingleConfig")
        default_config_button.color = "pink"

        with open(self.path_txt, "r", encoding="utf-8") as txt:
            params = eval(txt.read())

        amp_slider.set_val(params["onset"][0])
        cutoff0_slider.set_val(params["onset"][1])
        cutoff1_slider.set_val(params["onset"][2])
        numValid_slider.set_val(params["onset"][3])
        window_size_slider.set_val(params["onset"][4])
        ratio_slider.set_val(params["onset"][5])
        penalty_slider.set_val(params["onset"][6])
        ref_length_slider.set_val(params["onset"][7])
        eps_ratio_slider.set_val(params["onset"][8])

        r_amp_slider.set_val(params["offset"][0])
        r_cutoff0_slider.set_val(params["offset"][1])
        r_cutoff1_slider.set_val(params["offset"][2])
        r_numValid_slider.set_val(params["offset"][3])
        r_window_size_slider.set_val(params["offset"][4])
        r_ratio_slider.set_val(params["offset"][5])
        r_penalty_slider.set_val(params["offset"][6])
        r_ref_length_slider.set_val(params["offset"][7])
        r_eps_ratio_slider.set_val(params["offset"][8])

        fig.canvas.draw_idle()  # 刷新fig

    def show_default_config(self) -> None:
        self.is_show_default_config = not self.is_show_default_config
        default_config_button.label.set_text("DefaultConfig")
        default_config_button.color = "0.85"
        # default_config_button.hovercolor = ""

        with open("parameters.txt", "r", encoding="utf-8") as txt:
            params = eval(txt.read())

        amp_slider.set_val(params["onset"][0])
        cutoff0_slider.set_val(params["onset"][1])
        cutoff1_slider.set_val(params["onset"][2])
        numValid_slider.set_val(params["onset"][3])
        window_size_slider.set_val(params["onset"][4])
        ratio_slider.set_val(params["onset"][5])
        penalty_slider.set_val(params["onset"][6])
        ref_length_slider.set_val(params["onset"][7])
        eps_ratio_slider.set_val(params["onset"][8])

        r_amp_slider.set_val(params["offset"][0])
        r_cutoff0_slider.set_val(params["offset"][1])
        r_cutoff1_slider.set_val(params["offset"][2])
        r_numValid_slider.set_val(params["offset"][3])
        r_window_size_slider.set_val(params["offset"][4])
        r_ratio_slider.set_val(params["offset"][5])
        r_penalty_slider.set_val(params["offset"][6])
        r_ref_length_slider.set_val(params["offset"][7])
        r_eps_ratio_slider.set_val(params["offset"][8])

        fig.canvas.draw_idle()  # 刷新fig

    def draw_golden_vlines(self, time_points) -> None:
        print(time_points)
        if time_points is None:
            return None
        self.onsets_gold = [int(i * self.obj_audio.frame_rate) for i in time_points["onset"]]
        try:
            self.offsets_gold = [int(i * self.obj_audio.frame_rate) for i in time_points["offset"]]
        except KeyError:
            self.offsets_gold = []
        # print(onsets)
        # print(offsets)
        # print(time_points)
        # ax.vlines.clear()
        ax.vlines(self.onsets_gold, ymin=min(self.arr_audio), ymax=max(self.arr_audio), color="blue", alpha=.3)
        ax.vlines(self.offsets_gold, ymin=min(self.arr_audio), ymax=max(self.arr_audio), color="green", alpha=.3)
        # fig.canvas.draw_idle()  # 刷新fig

    def show_current_audio_arr(self) -> None:

        self.obj_audio = AudioSegment.from_wav(self.path_audio)  # , format=os.path.splitext(self.path_audio)[-1])
        self.arr_audio = self.obj_audio.split_to_mono()[0].get_array_of_samples()

        ax.cla()
        # ax.update(self.arr_audio)
        ax.plot(self.arr_audio, alpha=0.5, label=self.path_audio)
        ax.legend(loc="lower right", framealpha=1.)
        # plt.setp(ax.get_xticklabels(), va="top")#visible=False)
        ax.xaxis.tick_top()
        plt.setp(ax.get_yticklabels(), visible=False)
        ax.grid(alpha=.3)
        # ax.set_ylim(bottom=0)
        ax.set_xlim(left=0, right=len(self.arr_audio))
        # ax.tick_params(axis='both', which='both', length=0)
        fig.canvas.draw_idle()  # 刷新fig

    def draw_vlines(self, time_points) -> None:
        if not os.path.exists(self.path_textgrid):
            return None
        onsets = [int(i * self.obj_audio.frame_rate) for i in time_points["onset"]]
        offsets = [int(i * self.obj_audio.frame_rate) for i in time_points["offset"]]
        # print(onsets)
        # print(offsets)
        # print(time_points)
        # ax.vlines.clear()
        if self.offset_vlines is not None:
            self.offset_vlines.remove()
        if self.onset_vlines is not None:
            self.onset_vlines.remove()
        self.onset_vlines = ax.vlines(onsets, ymin=min(self.arr_audio), ymax=max(self.arr_audio), color="blue")
        self.offset_vlines = ax.vlines(offsets, ymin=min(self.arr_audio), ymax=max(self.arr_audio), color="green")

        self.onset_vlines.set_visible(self.if_onset_visible)
        self.offset_vlines.set_visible(self.if_offset_visible)

        fig.canvas.draw_idle()  # 刷新fig

    def show_current_config(self):
        # print(os.path.exists(self.path_txt))
        # if not os.path.exists(self.path_txt):
        #     self.is_show_default_config = True
        self.is_show_default_config = not os.path.exists(self.path_txt)
        if self.is_show_default_config:
            self.show_default_config()
        else:
            self.show_single_config()

    def switch_config(self):
        # print(os.path.exists(self.path_txt))
        if not os.path.exists(self.path_txt):
            self.is_show_default_config = True
        if self.is_show_default_config:
            self.show_default_config()
        else:
            self.show_single_config()

    # ------------------------------
    # ------------------------------
    # ------------------------------

    def select_config(self, event):
        self.switch_config()

    def get_info_dict(self, event) -> None:
        self.params_getinfo = {
            "onset": [
                amp_slider.val,
                cutoff0_slider.val,
                cutoff1_slider.val,
                numValid_slider.val,
                window_size_slider.val,
                ratio_slider.val,
                penalty_slider.val,
                ref_length_slider.val,
                eps_ratio_slider.val
            ],
            "offset": [
                r_amp_slider.val,
                r_cutoff0_slider.val,
                r_cutoff1_slider.val,
                r_numValid_slider.val,
                r_window_size_slider.val,
                r_ratio_slider.val,
                r_penalty_slider.val,
                r_ref_length_slider.val,
                r_eps_ratio_slider.val
            ]
        }

        time_points = process_items_with_params(
            params_procitems=self.params_getinfo,
            audio_file=self.path_audio
        )
        self.draw_vlines(time_points)

        onset_diffs = [min(abs(t - i / self.obj_audio.frame_rate) for t in time_points["onset"]) for i in
                       self.onsets_gold]
        print(onset_diffs)

        ax.set_title(f"Acc_1ms: {len([i for i in onset_diffs if i < 0.001]) / len(onset_diffs):.4f} "
                     f"Acc_5ms: {len([i for i in onset_diffs if i < 0.005]) / len(onset_diffs):.4f} "
                     f"Acc_10ms: {len([i for i in onset_diffs if i < 0.01]) / len(onset_diffs):.4f} "
                     f"Acc_20ms: {len([i for i in onset_diffs if i < 0.02]) / len(onset_diffs):.4f} ")

        # f" and {len(onset_diffs)/len(time_points["onset"]):.2f}")

    def prev_page(self, event) -> None:
        self.order -= 1
        self.order = self.order % len(self.paths_audio)
        self.path_audio = self.paths_audio[self.order]

        self.path_txt = os.path.splitext(self.path_audio)[0] + ".txt"
        self.path_textgrid = os.path.splitext(self.path_audio)[0] + ".TextGrid"
        self.fname = os.path.basename(os.path.splitext(self.path_audio)[0])

        self.show_current_config()
        self.show_current_audio_arr()

        try:
            self.draw_golden_vlines(
                get_frm_points_from_textgrid(os.path.join(self.folder_golden_answer, self.fname + ".TextGrid")))
        except AttributeError:
            self.draw_golden_vlines(
                get_frm_points_from_01(os.path.join(self.folder_golden_answer, self.fname + ".TextGrid")))

        try:
            self.draw_vlines(get_frm_points_from_textgrid(self.path_textgrid))
        except AttributeError:
            self.draw_vlines(get_frm_points_from_01(self.path_textgrid))
        print(self.order)

    def next_page(self, event) -> None:

        self.order += 1
        self.order = self.order % len(self.paths_audio)
        self.path_audio = self.paths_audio[self.order]

        self.path_txt = os.path.splitext(self.path_audio)[0] + ".txt"
        self.path_textgrid = os.path.splitext(self.path_audio)[0] + ".TextGrid"
        self.fname = os.path.basename(os.path.splitext(self.path_audio)[0])

        self.show_current_config()
        self.show_current_audio_arr()

        try:
            self.draw_golden_vlines(
                get_frm_points_from_textgrid(os.path.join(self.folder_golden_answer, self.fname + ".TextGrid")))
        except AttributeError:
            self.draw_golden_vlines(
                get_frm_points_from_01(os.path.join(self.folder_golden_answer, self.fname + ".TextGrid")))

        try:
            self.draw_vlines(get_frm_points_from_textgrid(self.path_textgrid))
        except AttributeError:
            self.draw_vlines(get_frm_points_from_01(self.path_textgrid))

        print(self.order)

    def save_single_config(self, event) -> None:
        self.params_getinfo = {
            "onset": [
                amp_slider.val,
                cutoff0_slider.val,
                cutoff1_slider.val,
                numValid_slider.val,
                window_size_slider.val,
                ratio_slider.val,
                penalty_slider.val,
                ref_length_slider.val,
                eps_ratio_slider.val
            ],
            "offset": [
                r_amp_slider.val,
                r_cutoff0_slider.val,
                r_cutoff1_slider.val,
                r_numValid_slider.val,
                r_window_size_slider.val,
                r_ratio_slider.val,
                r_penalty_slider.val,
                r_ref_length_slider.val,
                r_eps_ratio_slider.val
            ]
        }
        print(self.path_txt)
        with open(self.path_txt, "w", encoding="utf-8") as txt:
            txt.write(str(self.params_getinfo))

    def save_default_config(self, event) -> None:
        self.params_getinfo = {
            "onset": [
                amp_slider.val,
                cutoff0_slider.val,
                cutoff1_slider.val,
                numValid_slider.val,
                window_size_slider.val,
                ratio_slider.val,
                penalty_slider.val,
                ref_length_slider.val,
                eps_ratio_slider.val
            ],
            "offset": [
                r_amp_slider.val,
                r_cutoff0_slider.val,
                r_cutoff1_slider.val,
                r_numValid_slider.val,
                r_window_size_slider.val,
                r_ratio_slider.val,
                r_penalty_slider.val,
                r_ref_length_slider.val,
                r_eps_ratio_slider.val
            ]
        }
        print("parameters.txt")
        with open("parameters.txt", "w", encoding="utf-8") as txt:
            txt.write(str(self.params_getinfo))

    def change_offset_show_status(self, event) -> None:
        self.if_offset_visible = not self.if_offset_visible
        # print(self.offset_vlines)
        self.offset_vlines.set_visible(self.if_offset_visible)
        if self.if_offset_visible:
            show_offset_button.color = "lightgreen"
        else:
            show_offset_button.color = "0.85"
        fig.canvas.draw_idle()  # 刷新fig

    def change_onset_show_status(self, event) -> None:
        self.if_onset_visible = not self.if_onset_visible
        # print(self.onset_vlines)
        self.onset_vlines.set_visible(self.if_onset_visible)
        if self.if_onset_visible:
            show_onset_button.color = "lightblue"
        else:
            show_onset_button.color = "0.85"
        fig.canvas.draw_idle()  # 刷新fig


# -------------------------------------------
callback = RecPac()

confirm_button.on_clicked(callback.get_info_dict)
prev_button.on_clicked(callback.prev_page)
next_button.on_clicked(callback.next_page)

default_config_button.on_clicked(callback.select_config)
save_default_button.on_clicked(callback.save_default_config)
save_single_button.on_clicked(callback.save_single_config)

show_offset_button.on_clicked(callback.change_offset_show_status)
show_onset_button.on_clicked(callback.change_onset_show_status)

# -------------------------------------------

plt.show()

# -----> wait to do
# set all font
