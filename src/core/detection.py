import gc
import math
import os
import csv

import numpy as np
from sklearn.cluster import DBSCAN
from textgrid import TextGrid, PointTier, Point, IntervalTier, Interval

from src.utils.audio import bandpass_filter, get_current_time, ReadSound


global stop_flag  # 全局停止变量
stop_flag = False


def detectPraditor(params, audio_obj, which_set, mode="general", stime=0, etime=-1):
    """
    合并后的检测函数
    
    Args:
        params: 检测参数
        audio_obj: 音频对象
        which_set: "onset"或"offset"
        mode: "general"（通用模式）或"vad"（VAD模式）
        stime: 开始时间（毫秒），默认0
        etime: 结束时间（毫秒），默认-1表示整个音频
    """
    global stop_flag

    if stop_flag:
        return []

    # 导入数据，并且遵循一定之格式
    for xset in params:
        for item in params[xset]:
            # print(1)
            try:
                params[xset][item] = eval(params[xset][item])
            except Exception:
                pass
            # print(2)

    # VAD模式特殊处理：强制将offset参数设为与onset相同
    if mode == "vad":
        params["offset"] = params["onset"]

    params = params[which_set]  # 选择是onset还是offset

    # VAD模式固定参数
    if mode == "vad":
        params.update({
            "ratio": 0.9,
            "win_size": 50,
            "ref_len": 250,
            "penalty": 10
        })

    # 处理时间范围
    if etime != -1:
        audio_obj = audio_obj[stime*1000:etime*1000]    
    # 检查是否需要停止
    if stop_flag:
        return []
    
    _answer_frames = []
    _audio_obj = audio_obj
    _audio_samplerate = audio_obj.frame_rate

    _audio_arr_filtered = bandpass_filter(
        np.array(audio_obj.get_array_of_samples()),
        lowcut=params["cutoff0"],
        highcut=params["cutoff1"],
        fs=_audio_obj.frame_rate
    )

    # warning or auto change?
    if which_set == "offset":
        _audio_arr_filtered = np.flip(_audio_arr_filtered)

    # 1.1. 降采样
    # 把一秒钟的音频分成n=40份
    _dsFactor = _audio_obj.frame_rate // 40

    # 统一降采样处理：确保音频长度能被降采样因子整除
    if len(_audio_arr_filtered) % _dsFactor != 0:
        _audio_arr_filtered = _audio_arr_filtered[:-(len(_audio_arr_filtered) % _dsFactor)]

    _audio_arr_ds = _audio_arr_filtered.reshape((len(_audio_arr_filtered) // _dsFactor, _dsFactor))
    _audio_arr_ds = np.max(_audio_arr_ds, axis=1)  # 用max方法降采样

    _points_array = np.array([
        [_audio_arr_ds[i] for i in range(len(_audio_arr_ds) - 1)],
        [_audio_arr_ds[i + 1] for i in range(len(_audio_arr_ds) - 1)]
    ]).T

    _eps = params["eps_ratio"] * float(np.max(np.sort(_audio_arr_ds)[:int(.8 * len(_audio_arr_ds))]))  # 找到合适的radius，防止异常值
    

    del _audio_arr_ds
    gc.collect()

    _min_samples = math.ceil(0.3/_dsFactor * _audio_obj.frame_rate)
    try:
        _cluster = DBSCAN(eps=_eps, min_samples=_min_samples, metric="manhattan").fit(_points_array)
    except MemoryError:
        print("[SOT] Not enough memory")
        return []

    # To look for the label with which the coordinate is closet to the zero point
    # xy值加起来最小值 -> 最接近零点
    noise_label = 0
    for i in range(0, len(set(_cluster.labels_))-1):
        if np.min(np.sum(_points_array[_cluster.labels_ == i], axis=1)) < np.min(np.sum(_points_array[_cluster.labels_ == noise_label], axis=1)):
            noise_label = i
    _points_confirmed = _points_array[_cluster.labels_ == noise_label]

    # 把最小cluster以下的所有点都囊括进来
    _points_compensation = np.array(range(len(_points_array)))[np.sum(np.square(_points_array), axis=1) <= np.mean(np.sum(np.square(_points_confirmed), axis=1))]

    _labels = _cluster.labels_
    for i in _points_compensation:
        _labels[int(i)] = noise_label

    _labels = [noise_label] * 3 + [i for i in _labels] + [noise_label] * 3
    _indices_confirmed = [i-3 for i in range(len(_labels)) if _labels[i] == noise_label]

    # gather sampled area | target area
    _indices_completed = []
    for i in _indices_confirmed:
        for j in range(3):  # 原来是4，改成了3，只加上012
            if (i + j) not in _indices_completed:
                _indices_completed.append(i + j)

    _onsets = []
    _offsets = []
    for i in range(min(_indices_completed), max(_indices_completed) + 2):
        if i in _indices_completed and (i - 1) not in _indices_completed:
            _onsets.append(i)
        elif i not in _indices_completed and (i - 1) in _indices_completed:
            _offsets.append(i - 1)

    # 筛除掉长度不够的噪声片段
    while True:
        _bad_onoffsets = []
        for i in range(len(_offsets)-1):
            if (_onsets[i+1] - _offsets[i]) * _dsFactor / _audio_samplerate < .1:
                _bad_onoffsets.append(_onsets[i+1])
                _bad_onoffsets.append(_offsets[i])
        if len(_bad_onoffsets) == 0:
            break
        _onsets = [i for i in _onsets if i not in _bad_onoffsets]
        _offsets = [i for i in _offsets if i not in _bad_onoffsets]
    _onoffsets = [(_onsets[i], _offsets[i]) for i in range(len(_onsets))]


    for i, (__offset, __onset) in enumerate(_onoffsets):
        print(f"[SOT] {(i+1)/len(_onoffsets)*100:.1f}%")

        # 检查是否需要停止
        if stop_flag:
            return []

        # 强制跳过条件
        if __onset <= 0 - 3:
            continue
        if __offset >= len(_cluster.labels_) + 3:
            continue

        __offset = 0 if __offset <= 0 else __offset
        
        try:
            __candidate_y1_area = abs(np.array(
                _audio_arr_filtered[__offset * _dsFactor+1:__onset * _dsFactor] -
                _audio_arr_filtered[__offset * _dsFactor:__onset * _dsFactor-1]
            ))
        except ValueError:
            continue  # hit the bottom with no more frames

        __sample_startpoint = int(np.argmin(__candidate_y1_area) + __offset * _dsFactor)
        __sample_endpoint = __sample_startpoint - params["ref_len"]
        if __sample_endpoint < 0:
            __sample_endpoint = 0

        try:
            __candidate_y1_area = abs(np.array(
                _audio_arr_filtered[__sample_endpoint+1:__sample_startpoint] -
                _audio_arr_filtered[__sample_endpoint:__sample_startpoint - 1]
            ))
        except ValueError:
            __sample_startpoint = __sample_endpoint + params["ref_len"]
            __candidate_y1_area = abs(np.array(
                _audio_arr_filtered[__sample_endpoint+1:__sample_startpoint] -
                _audio_arr_filtered[__sample_endpoint:__sample_startpoint - 1]
            ))

        __candidate_y1_area = np.sort(__candidate_y1_area)[:int(len(__candidate_y1_area) * params["ratio"])]
        __y1_threshold = float(np.sum(__candidate_y1_area) / (__sample_startpoint - __sample_endpoint) * params["amp"])
        __ref_midpoint = int(__offset*_dsFactor + (__onset-__offset) * _dsFactor * 0.8)  # 3/4偏移量

        if i < len(_onoffsets) - 1:
            __ref_midpoint_next = int(_onoffsets[i+1][0]*_dsFactor + (_onoffsets[i+1][1]-_onoffsets[i+1][0]) * _dsFactor * 0.8)
        else:
            __ref_midpoint_next = len(_audio_arr_filtered)  # 设置为音频最后一帧的位置

        if __ref_midpoint < __sample_startpoint:
            __ref_midpoint = __sample_startpoint

        __countValidPiece = 0
        __countBadPiece = 0
        __countDSTime = -1

        while __ref_midpoint + __countDSTime < __ref_midpoint_next:

                
            __countDSTime += 1

            __left_boundary = __ref_midpoint + __countDSTime - params["win_size"]
            __right_boundary = __ref_midpoint + __countDSTime

            try:
                __raw_value = abs(_audio_arr_filtered[__left_boundary:__right_boundary] - _audio_arr_filtered[__left_boundary-1:__right_boundary-1])
            except ValueError:
                break
            __raw_value.sort()
            __raw_value = __raw_value[:int(len(__raw_value) * params["ratio"])]

            __y1_value = sum(__raw_value)/len(__raw_value)

            if __y1_value > __y1_threshold:
                __countValidPiece += 1
            else:
                __countBadPiece += 1

            if __countValidPiece - __countBadPiece * params["penalty"]  <= 0:
                __countValidPiece = 0
                __countBadPiece = 0
            elif __countValidPiece - __countBadPiece >= params["numValid"]:
                _final_answer = __ref_midpoint + __countDSTime - __countValidPiece - __countBadPiece

                if which_set == "offset":
                    _final_answer = len(_audio_arr_filtered) - (_final_answer +  len(_audio_arr_filtered) % _dsFactor)
                _answer_frames.append(_final_answer)
                break
    
    # 处理时间范围偏移
    _answer = [frm/_audio_samplerate for frm in list(set(_answer_frames))]
    # print(_answer)
    
    # VAD模式下排序结果
    if mode == "vad":
        _answer = sorted(_answer)
    
    # 添加时间偏移
    if etime != -1:
        _answer = [tp + stime for tp in _answer if 5 < tp < (_answer[-1] - 5) if _answer]
    
    # print(_answer)
    return _answer


def create_textgrid_with_time_point(audio_file_path, is_vad_mode:bool, onsets=[], offsets=[]):
    # 获取音频文件的目录和文件名（不包括扩展名）
    audio_dir = os.path.dirname(os.path.abspath(audio_file_path))
    audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
    audio_extension = os.path.splitext(os.path.basename(audio_file_path))[1]
    audio_obj = ReadSound(os.path.join(audio_dir, audio_filename+audio_extension))
    audio_duration = audio_obj.duration_seconds
    audio_samplerate = audio_obj.frame_rate


    if is_vad_mode:

        # 检测 onsets 和 offsets 的数量是否一致
        if len(onsets) != len(offsets):
            raise ValueError(f"The number of onsets ({len(onsets)}) and offsets ({len(offsets)}) does not match. ")

        # 检测并删除包含 None 的对应元素
        indices_to_remove = [i for i in range(len(onsets)) if onsets[i] is None or offsets[i] is None]
        for idx in sorted(indices_to_remove, reverse=True):
            del onsets[idx]
            del offsets[idx]


        # 获取音频文件的目录和文件名（不包括扩展名）
        audio_dir = os.path.dirname(os.path.abspath(audio_file_path))
        audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
        audio_extension = os.path.splitext(os.path.basename(audio_file_path))[1]
        audio_obj = ReadSound(os.path.join(audio_dir, audio_filename+audio_extension))


        tg_filename = os.path.join(audio_dir, audio_filename + "_vad.TextGrid")
        tg = TextGrid()

        interval_tier = IntervalTier(name="interval", minTime=0., maxTime=audio_obj.duration_seconds)

        for i in range(len(onsets)):
            try:
                interval_tier.addInterval(Interval(onsets[i], offsets[i], "sound"))
            except ValueError:
                continue
        tg.append(interval_tier)

    else:
        # 创建一个新的TextGrid对象
        tg_filename = os.path.join(audio_dir, audio_filename + ".TextGrid")
        tg = TextGrid()

        # 时间
        # time_points = [frm/audio_samplerate for frm in frame_points]

        for set_mode in ["onset", "offset"]:
            point_tier = PointTier(name=set_mode, minTime=0., maxTime=audio_duration)

            if set_mode == "onset":
                xsets = onsets
            elif set_mode == "offset":
                xsets = offsets
                # print(xsets)
            for time_point in xsets:
                try:
                    point_tier.addPoint(Point(time_point, set_mode))
                except ValueError:
                    continue

            tg.append(point_tier)



    tg.write(tg_filename)  # 将TextGrid对象写入文件

    # print(f"{audio_filename}\t|\t{get_current_time()}\t|\tTextGrid created at: {tg_filename}")
    print(f"[SOT] TextGrid created at: {tg_filename}")
    
    # 生成CSV文件
    textgrid_to_csv(tg_filename)


def textgrid_to_csv(textgrid_file_path):
    """将TextGrid文件转换为CSV文件"""
    # 获取TextGrid文件的目录和文件名（不包括扩展名）
    tg_dir = os.path.dirname(os.path.abspath(textgrid_file_path))
    tg_filename = os.path.splitext(os.path.basename(textgrid_file_path))[0]
    
    # 构建CSV文件名
    csv_filename = os.path.join(tg_dir, tg_filename + ".csv")
    
    # 获取原始音频文件名（移除_vad后缀，如果有）
    original_filename = tg_filename.replace("_vad", "")
    
    # 读取TextGrid文件
    tg = TextGrid(textgrid_file_path)
    tg.read(textgrid_file_path)
    
    # 根据TextGrid类型（点或区间）进行不同处理
    if tg.tiers[0].__class__.__name__ == "PointTier":
        # 点模式：onset和offset作为两列
        data = {"onset": [], "offset": []}
        
        # 提取每个tier的数据
        for tier in tg.tiers:
            data[tier.name] = [p.time for p in tier]
        
        # 确定最大长度，用于对齐数据
        max_len = max(len(data["onset"]), len(data["offset"]))
        
        # 写入CSV文件
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # 写入表头
            writer.writerow(["filename", "onset", "offset"])
            # 写入数据
            for i in range(max_len):
                onset = data["onset"][i] if i < len(data["onset"]) else ""
                offset = data["offset"][i] if i < len(data["offset"]) else ""
                writer.writerow([original_filename, onset, offset])
    
    elif tg.tiers[0].__class__.__name__ == "IntervalTier":
        # 区间模式：minTime, maxTime, mark作为列
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # 写入表头
            writer.writerow(["filename", "minTime", "maxTime", "mark"])
            # 写入数据，只保存mark为"sound"的区间
            for interval in tg.tiers[0]:
                if interval.mark == "sound":
                    writer.writerow([original_filename, interval.minTime, interval.maxTime, interval.mark])
    
    # print(f"{tg_filename}\t|\t{get_current_time()}\t|\tCSV created at: {csv_filename}")
    print(f"[SOT] CSV created at: {csv_filename}")
    return csv_filename
