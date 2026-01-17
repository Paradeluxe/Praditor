import os.path
import sys
from datetime import datetime

import numpy as np
from scipy.signal import butter, filtfilt
from textgrid import TextGrid
import soundfile as sf


class ReadSound:
    def __init__(self, fpath=None, arr=None, duration_seconds=None, frame_rate=None):


        if fpath is None:
            if arr is None:
                raise ValueError("Need audio input. Receive None.")
            else:
                self.arr = arr
                self.duration_seconds = duration_seconds
                self.frame_rate = frame_rate

        else:  # 如果有fpath
            self.fpath = fpath
            self.info = sf.info(fpath)
            # print(self.info)

            self.duration_seconds = self.info.duration
            self.arr, self.frame_rate = sf.read(fpath, dtype='int16')



        try:
            self.arr = self.arr[:, 0]
        except IndexError:
            pass

        self.max = np.max(np.abs(self.arr))

    def __getitem__(self, ms):


        start = int(ms.start * self.frame_rate / 1000) if ms.start is not None else 0
        end = int(ms.stop * self.frame_rate / 1000) if ms.stop is not None else len(self.arr)

        start = min(start, len(self.arr))
        end = min(end, len(self.arr))


        return ReadSound(arr=self.arr[start:end], duration_seconds=(end - start) / 1000, frame_rate=self.frame_rate)

    def get_array_of_samples(self):
        return self.arr



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_current_time():
    # 获取当前时间
    now = datetime.now()
    # 格式化时间字符串
    formatted_time = now.strftime("%H:%M:%S.%f")[:-3]  # 去掉微秒部分的最后3个字符
    return formatted_time


def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    if low == 0:
        b, a = butter(order, high, btype='low', output="ba")
        filtered_data = filtfilt(b, a, data)
    else:
        try:
            b, a = butter(order, [low, high], btype='bandpass', output="ba")
            filtered_data = filtfilt(b, a, data)
        except ValueError:  # 如果设置的最高频率大于了可接受的范围
            b, a = butter(order, [low, 1], btype='bandpass', output="ba")
            filtered_data = filtfilt(b, a, data)
    return filtered_data


def lowpass_filter(data, highcut, fs, order=4):
    nyquist = 0.5 * fs
    high = highcut / nyquist
    b, a = butter(order, high, btype='low', output="ba")
    filtered_data = filtfilt(b, a, data)
    return filtered_data


def isAudioFile(fpath):
    # 所有的音频后缀
    audio_extensions = [
        '.mp3',  # MPEG Audio Layer-3
        '.wav',   # Waveform Audio File Format
        ".WAV",
        '.ogg',   # Ogg
        '.flac',  # Free Lossless Audio Codec
        '.aac',   # Advanced Audio Codec
        '.m4a',   # MPEG-4 Audio Layer
        '.alac',  # Apple Lossless Audio Codec
        '.aiff',  # Audio Interchange File Format
        '.au',    # Sun/NeXT Audio File Format
        '.aup',   # Audio Unix/NeXT
        '.ra',    # RealAudio
        '.ram',   # RealAudio Metafile
        '.rv64',  # Raw 64-bit float (AIFF/AIFF-C)
        '.spx',   # Ogg Speex
        '.voc',   # Creative Voice
        '.webm',  # WebM (audio part)
        '.wma',   # Windows Media Audio
        '.xm',    # FastTracker 2 audio module
        '.it',    # Impulse Tracker audio module
        '.mod',   # Amiga module (MOD)
        '.s3m',   # Scream Tracker 3 audio module
        '.mtm',   # MultiTracker audio module
        '.umx',   # FastTracker 2 extended module
        '.dxm',   # Digital Tracker (DTMF) audio module
        '.f4a',   # FAudio (FMOD audio format)
        '.opus',  # Opus Interactive Audio Codec
    ]
    if any(fpath.endswith(ext) for ext in audio_extensions):
        return True
    else:
        return False


def get_frm_points_from_textgrid(audio_file_path):

    audio_dir = os.path.dirname(os.path.abspath(audio_file_path))
    audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
    tg_file_path = os.path.join(audio_dir, audio_filename + ".TextGrid")

    dict_tg_time = {"onset":[], "offset": []}
    if not os.path.exists(tg_file_path):
        return dict_tg_time
    # print("hahah")
    tg = TextGrid()
    tg.read(tg_file_path)
    for tier in tg.tiers:
        dict_tg_time[tier.name] = [p.time for p in tier]
    return dict_tg_time


def get_frm_intervals_from_textgrid(audio_file_path):
    audio_dir = os.path.dirname(os.path.abspath(audio_file_path))
    audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
    tg_file_path = os.path.join(audio_dir, audio_filename + "_vad.TextGrid")

    dict_tg_time = {"onset": [], "offset": []}
    if not os.path.exists(tg_file_path):
        return dict_tg_time

    tg = TextGrid(tg_file_path)
    tg.read(tg_file_path)
    tier = tg.tiers[0]

    dict_tg_time["onset"] = [interval.minTime for interval in tier if interval.mark == "sound"]
    dict_tg_time["offset"] = [interval.maxTime for interval in tier if interval.mark == "sound"]

    return dict_tg_time
