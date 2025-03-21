import gc
import math
import os

import numpy as np
from pydub import AudioSegment
from sklearn.cluster import DBSCAN
from textgrid import TextGrid, PointTier, Point
from tool import bandpass_filter, get_current_time, resource_path


plat = os.name.lower()
# check if ffmpeg exists in the system path or the pydub package can find it
os.environ["PATH"] += os.pathsep + resource_path(f".\\ffmpeg\\{plat}")
print(resource_path(f".\\ffmpeg\\{plat}"))


def runPraditorWithTimeRange(params, audio_obj, which_set, stime=0, etime=-1):
    if etime == -1:
        ans_tps = runPraditor(params, audio_obj, which_set)

    else:
        ans_tps = runPraditor(params, audio_obj[stime*1000:etime*1000], which_set)
        ans_tps = [tp + stime for tp in ans_tps if 5 < tp <ans_tps[-1] - 5]
    return ans_tps


def runPraditor(params, audio_obj, which_set):
    # 导入数据，并且遵循一定之格式
    for xset in params:
        for item in params[xset]:
            params[xset][item] = eval(params[xset][item])

    params = params[which_set]  # 选择是onset还是offset
    # print(params)
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

    # Audio已经准备好
    # 接下来就是第一步：DBSCAN聚类找噪声片段


    # 1.1. 降采样
    # 把一秒钟的音频分成n=40份

    _dsFactor = _audio_obj.frame_rate // 40
    # _audio_arr_ds = _audio_arr_filtered

    # 用取余容易得到[:-0]，返回一个空list
    # 用整除解决这个问题
    if len(_audio_arr_filtered) % _dsFactor == 0:
        _audio_arr_ds = _audio_arr_filtered[:]
    else:
        _audio_arr_ds = _audio_arr_filtered[:-(len(_audio_arr_filtered) % _dsFactor)]

    # max_frm_num = len(_audio_arr_filtered)

    _audio_arr_ds = _audio_arr_ds.reshape((len(_audio_arr_ds) // _dsFactor, _dsFactor))
    _audio_arr_ds = np.max(_audio_arr_ds, axis=1)  # 用max方法降采样

    # print(_audio_arr_ds[10:1000])

    _points_array = np.array([
        [_audio_arr_ds[i] for i in range(len(_audio_arr_ds) - 1)],
        [_audio_arr_ds[i + 1] for i in range(len(_audio_arr_ds) - 1)]
    ]).T




    _eps = params["eps_ratio"] * float(np.max(np.sort(_audio_arr_ds)[:int(.8 * len(_audio_arr_ds))]))  # 找到合适的radius，防止异常值


    del _audio_arr_ds
    gc.collect()

    _min_samples = math.ceil(0.3/_dsFactor * _audio_obj.frame_rate) #math.ceil(2 / (target_audio_samplerate/44100) / (interval*2/4281))
    try:
        _cluster = DBSCAN(eps=_eps, min_samples=_min_samples, metric="manhattan").fit(_points_array)

    except MemoryError:
        print("not enough memory")
        return []
    _labels = _cluster.labels_



    # To look for the label with which the coordinate is closet to the zero point
    # xy值加起来最小值 -> 最接近零点
    noise_label = 0
    for i in range(0, len(set(_labels))-1):
        if np.min(np.sum(_points_array[_labels == i], axis=1)) < np.min(np.sum(_points_array[_labels == noise_label], axis=1)):
            noise_label = i
    _points_confirmed = _points_array[_labels == noise_label]
    # print(_labels, noise_label)

    # 把最小cluster以下的所有点都囊括进来
    _points_compensation = np.array(range(len(_points_array)))[np.sum(np.square(_points_array), axis=1) <= np.mean(np.sum(np.square(_points_confirmed), axis=1))]
    # print(_points_confirmed)

    for i in _points_compensation:
        _labels[int(i)] = noise_label

    _labels = [noise_label] * 3 + [i for i in _labels] + [noise_label] * 3  # 这句干啥用的？？？
    _indices_confirmed = [i-3 for i in range(len(_labels)) if _labels[i] == noise_label]  # or labels[i] == -1]

    # print(_indices_confirmed)


    # gather sampled area | target area

    _indices_completed = []
    for i in _indices_confirmed:
        for j in range(3):  # 原来是4，改成了3，只加上012
            if (i + j) not in _indices_completed:
                _indices_completed.append(i + j)

    # print(_indices_completed)

    _onsets = []
    _offsets = []
    for i in range(min(_indices_completed), max(_indices_completed) + 2):  # +2取不到 +1必定不存在
        if i in _indices_completed and (i - 1) not in _indices_completed:
            _onsets.append(i)
        elif i not in _indices_completed and (i - 1) in _indices_completed:
            _offsets.append(i - 1)

    # print(f" > Silence/Noise Onsets: {onsets}")  # 打印所有无声范围的onset
    # print(f" > Silence/Noise Offsets: {offsets}")  # 打印所有无声范围的offset

    # onset和offset的数量一定一样(? not really)
    # 把它俩成对组合后，筛除掉其中长度不够的（noise too short）


    while True:
        _bad_onoffsets = []
        for i in range(len(_offsets)-1):
            if (_onsets[i+1] - _offsets[i]) * _dsFactor /_audio_samplerate < .1:
                _bad_onoffsets.append(_onsets[i+1])
                _bad_onoffsets.append(_offsets[i])
        if len(_bad_onoffsets) == 0:
            break

        _onsets = [i for i in _onsets if i not in _bad_onoffsets]
        _offsets = [i for i in _offsets if i not in _bad_onoffsets]
    _onoffsets = [(_onsets[i], _offsets[i]) for i in range(len(_onsets))]

    # print(_onoffsets)

    # now offset means sound offset (not silence offset)
    # onset means sound onset (not silence onset)
    # with ProcessPoolExecutor(max_workers=threads) as executor:
    #     results = list(executor.map(process_items_with_params, *parameters, chunksize=threads))
    # print(np.cuda.get_device_id())
    # np.cuda.device = 1
    # print("---↘")
    for __offset, __onset in _onoffsets:

        # -------------------------------------------------
        # 强制跳过条件 Skip Condition

        if __onset <= 0 - 3:
            continue

        if __offset >= len(_cluster.labels_) + 3:
            continue

        # -----------------------------------------------

        __offset = 0 if __offset <= 0 else __offset
        # print(__offset * _dsFactor+1, __onset * _dsFactor, __offset * _dsFactor, __onset * _dsFactor-1)
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
        if __ref_midpoint < __sample_startpoint:
            __ref_midpoint = __sample_startpoint
        # print(np.argmin(candidate_y1_area), ref_midpoint)

        # ----------------- Processing onset area --------------
        # print(f"\r{audio_file}\t|\t{get_current_time()}\t|\tProcessing >> onset {onset} + offset {offset}", end="")


        # print(y1_threshold)

        __countValidPiece = 0
        __countBadPiece = 0
        __countDSTime = -1


        while True:
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
                __countBadPiece += params["penalty"]

            if __countValidPiece - __countBadPiece  <= 0:
                __countValidPiece = 0
                __countBadPiece = 0

            elif __countValidPiece - __countBadPiece >= params["numValid"]:
                _final_answer = __ref_midpoint + __countDSTime - __countValidPiece - __countBadPiece

                if which_set == "offset":
                    _final_answer = len(_audio_arr_filtered) - _final_answer
                _answer_frames.append(_final_answer)
                break
    return [frm/_audio_samplerate for frm in list(set(_answer_frames))]


def get_frm_points_from_textgrid(audio_file_path):

    audio_dir = os.path.dirname(os.path.abspath(audio_file_path))
    audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
    tg_file_path = os.path.join(audio_dir, audio_filename + ".TextGrid")
    if not os.path.exists(tg_file_path):
        return {"onset":[], "offset": []}
    tg = TextGrid(tg_file_path)
    tg.read(tg_file_path)
    dict_tg_time = {}
    for tier in tg.tiers:
        dict_tg_time[tier.name] = [p.time for p in tier]
    return dict_tg_time


def create_textgrid_with_time_point(audio_file_path, onsets=[], offsets=[]):
    # 获取音频文件的目录和文件名（不包括扩展名）
    audio_dir = os.path.dirname(os.path.abspath(audio_file_path))
    audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
    audio_extension = os.path.splitext(os.path.basename(audio_file_path))[1]
    audio_obj = AudioSegment.from_file(os.path.join(audio_dir, audio_filename+audio_extension))
    audio_duration = audio_obj.duration_seconds
    audio_samplerate = audio_obj.frame_rate

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

    print(f"{audio_filename}\t|\t{get_current_time()}\t|\tTextGrid created at: {tg_filename}")






