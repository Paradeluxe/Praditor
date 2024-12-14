import os.path
import sys
from datetime import datetime

from scipy.signal import butter, filtfilt
from textgrid import TextGrid


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
    try:
        b, a = butter(order, [low, high], btype='bandpass', output="ba")
        filtered_data = filtfilt(b, a, data)
    except ValueError:  # 如果设置的最高频率大于了可接受的范围，则变为（实际意义上的）高通滤波
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


def get_frm_points_from_textgrid(file_path):
    if not os.path.exists(file_path):
        return None
    tg = TextGrid(file_path)
    tg.read(file_path)
    dict_tg = {}

    for tier in tg.tiers:
        dict_tg[tier.name] = [p.time for p in tier]

    return dict_tg


def get_frm_points_from_01(file_path):
    if not os.path.exists(file_path):
        return None
    tg = TextGrid(file_path)
    tg.read(file_path)
    dict_tg = {}

    for tier in tg.tiers:
        dict_tg["onset"] = [p.minTime for p in tier if p.mark == "1"]
        dict_tg["offset"] = [p.maxTime for p in tier if p.mark == "1"]

    return dict_tg


def get_interval(file_path):
    tg = TextGrid(file_path)
    tg.read(file_path)

    tg_onsets = []
    tg_offsets = []

    for tier in tg.tiers:
        if tier.name == "onset":
            tg_onsets = [p.time * 1000 for p in tier]
        else:
            tg_offsets = [p.time * 1000 for p in tier]

    return list(zip(tg_onsets, tg_offsets))


def get_time(file_path):
    # 加载TextGrid文件
    tg = TextGrid(file_path)
    tg.read(file_path)
    # 找到名为'onset'的PointTier
    point_tier_onset = None

    for tier in tg.tiers:
        if tier.name == 'onset':
            point_tier_onset = tier
            break

    # 如果找到了PointTier，获取第一个点的时间
    if point_tier_onset:
        return point_tier_onset.points[0].time
        # print(f"The time of the first point in 'onset' tier is: {first_point_time}")
    else:
        return None