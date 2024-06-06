import math
import os
import platform
from concurrent.futures import ProcessPoolExecutor

import cupy as cp
from matplotlib import pyplot as plt
from pydub import AudioSegment
from sklearn.cluster import DBSCAN
from textgrid import TextGrid, PointTier, Point

from Praditor_tool import isAudioFile, lowpass_filter, bandpass_filter, get_current_time

plat = platform.system().lower()

if plat == 'windows':
    AudioSegment.converter = f".\\ffmpeg\\{plat}\\ffmpeg.exe"
    AudioSegment.ffmpeg = f".\\ffmpeg\\{plat}\\ffmpeg.exe"
elif plat == "darwin":  # macOS
    AudioSegment.converter = f".\\ffmpeg\\{plat}\\ffmpeg"
    AudioSegment.ffmpeg = f".\\ffmpeg\\{plat}\\ffmpeg"
elif plat == 'linux':
    pass
else:
    pass


def create_textgrid_with_time_point(audio_file_path, time_points):
    # 获取音频文件的目录和文件名（不包括扩展名）
    audio_dir = os.path.dirname(os.path.abspath(audio_file_path))
    audio_filename = os.path.splitext(os.path.basename(audio_file_path))[0]
    audio_extension = os.path.splitext(os.path.basename(audio_file_path))[1]

    audio_duration = AudioSegment.from_file(os.path.join(audio_dir, audio_filename+audio_extension)).duration_seconds

    tg_filename = os.path.join(audio_dir, audio_filename + ".TextGrid")

    # 创建一个新的TextGrid对象
    tg = TextGrid()
    for set_mode in time_points:
        point_tier = PointTier(name=set_mode, minTime=0., maxTime=audio_duration)

        for time_point in time_points[set_mode]:
            try:
                point_tier.addPoint(Point(time_point, set_mode))
            except ValueError:
                continue

        tg.append(point_tier)

    # 将TextGrid对象写入文件
    tg.write(tg_filename)

    print(f"{audio_filename}\t|\t{get_current_time()}\t|\tTextGrid created at: {tg_filename}")


def process_item(params_procitem, audio_file, reverse):

    try:
        amp, low_cutoff, high_cutoff, numValid, window_size, ratio, penalty, ref_length, eps_radius_ratio = params_procitem
    except ValueError:
        amp, low_cutoff, high_cutoff, numValid, window_size, ratio, penalty, ref_length = params_procitem
        eps_radius_ratio = 0.015

    low_cutoff = int(low_cutoff)
    high_cutoff = int(high_cutoff)
    numValid = int(numValid)
    window_size = int(window_size)
    ratio = float(ratio)
    penalty = int(penalty)
    ref_length = int(ref_length)
    eps_radius_ratio = float(eps_radius_ratio)


    time_points = []

    target_audio_obj = AudioSegment.from_file(audio_file).split_to_mono()[0]  # from_file函数在没有指定后缀的时候会尝试获取后缀
    target_audio_samplerate = target_audio_obj.frame_rate  # 获取文件的采样率（比如44100）
    audio_file = os.path.splitext(os.path.basename(audio_file))[0]


    if high_cutoff >= target_audio_samplerate / 2:
        low_cutoff = 1
        high_cutoff = int(target_audio_samplerate * .5) - 1


    if low_cutoff == 0:
        target_audio_arr_filtered_ = lowpass_filter(
            target_audio_obj.get_array_of_samples(),
            high_cutoff,
            target_audio_samplerate
        )
    else:
        target_audio_arr_filtered_ = bandpass_filter(
            target_audio_obj.get_array_of_samples(),
            low_cutoff,
            high_cutoff,
            target_audio_samplerate
        )

    if reverse:
        target_audio_arr_filtered_ = cp.flip(target_audio_arr_filtered_)

    accFactor = int(target_audio_samplerate / (40. * target_audio_samplerate/44100))  # 默认值为20.
    print(f"{audio_file}\t|\t{get_current_time()}\t|\t"
          f"{len(target_audio_arr_filtered_)} Frm with {target_audio_samplerate}({accFactor}) Hz"
          f" is {round(len(target_audio_arr_filtered_) / target_audio_samplerate, 3)} Sec")

    target_audio_arr_ds = target_audio_arr_filtered_

    # 用取余容易得到[:-0]，返回一个空list
    # 用整除解决这个问题
    if len(target_audio_arr_ds) % accFactor == 0:
        target_audio_arr_ds = target_audio_arr_ds[:]
    else:
        target_audio_arr_ds = target_audio_arr_ds[:-(len(target_audio_arr_ds) % accFactor)]

    max_frm_num = len(target_audio_arr_filtered_)

    target_audio_arr_ds = target_audio_arr_ds.reshape((len(target_audio_arr_ds) // accFactor, accFactor))
    target_audio_arr_ds = cp.max(target_audio_arr_ds, axis=1)  # 用max方法降采样

    points_array = cp.array([
        [target_audio_arr_ds[i] for i in range(len(target_audio_arr_ds)-1)],
        [target_audio_arr_ds[i+1] for i in range(len(target_audio_arr_ds)-1)]
    ]).T
    # 0.015
    eps = eps_radius_ratio * float(cp.max(cp.sort(target_audio_arr_ds)[:int(.8 * len(target_audio_arr_ds))]))  # 防止异常值

    min_samples = math.ceil(0.3/accFactor*target_audio_samplerate) #math.ceil(2 / (target_audio_samplerate/44100) / (interval*2/4281))

    cluster = DBSCAN(eps=eps, min_samples=min_samples, metric="manhattan").fit(points_array.get())
    labels = cluster.labels_

    # To look for the label with which the coordinate is closet to the zero point
    target_label = 0
    for i in range(0, len(set(labels))-1):
        if cp.min(cp.sum(points_array[cluster.labels_ == i], axis=1)) < cp.min(cp.sum(points_array[cluster.labels_ == target_label], axis=1)):
            target_label = i

    points_confirmed = points_array[cluster.labels_ == target_label]
    points_compensation = cp.array(range(len(points_array)))[cp.sum(cp.square(points_array), axis=1) <= cp.mean(cp.sum(cp.square(points_confirmed), axis=1))]
    for i in points_compensation:
        labels[int(i)] = target_label


    labels = [target_label] * 3 + [i for i in labels] + [target_label] * 3

    indexes_confirmed = [i-3 for i in range(len(labels)) if labels[i] == target_label]  # or labels[i] == -1]

    # gather sampled area | target area

    indexes_completed = []
    for i in indexes_confirmed:
        for j in range(3):  # 原来是4，改成了3，只加上012
            if (i + j) not in indexes_completed:
                indexes_completed.append(i + j)

    onsets = []
    offsets = []
    for i in range(min(indexes_completed), max(indexes_completed) + 2):  # +2取不到 +1必定不存在
        if i in indexes_completed and (i - 1) not in indexes_completed:
            onsets.append(i)
        elif i not in indexes_completed and (i - 1) in indexes_completed:
            offsets.append(i - 1)

    # print(f" > Silence/Noise Onsets: {onsets}")  # 打印所有无声范围的onset
    # print(f" > Silence/Noise Offsets: {offsets}")  # 打印所有无声范围的offset

    # onset和offset的数量一定一样
    # 把它俩成对组合后，筛除掉其中长度不够的（noise too short）

    while True:
        bad_onoffsets = []
        for i in range(len(offsets)-1):
            if (onsets[i+1] - offsets[i]) * accFactor /target_audio_samplerate < .1:
                bad_onoffsets.append(onsets[i+1])
                bad_onoffsets.append(offsets[i])
                # print(onsets[i+1], offsets[i])
        if len(bad_onoffsets) == 0:
            break

        onsets = [i for i in onsets if i not in bad_onoffsets]
        offsets = [i for i in offsets if i not in bad_onoffsets]
    onoffsets = [(onsets[i], offsets[i]) for i in range(len(onsets))]
    # print(onoffsets)

    # now offset means sound offset (not silence offset)
    # onset means sound onset (not silence onset)
    # with ProcessPoolExecutor(max_workers=threads) as executor:
    #     results = list(executor.map(process_items_with_params, *parameters, chunksize=threads))
    # print(cp.cuda.get_device_id())
    # cp.cuda.device = 1
    print("---↘")
    for offset, onset in onoffsets:

        # -------------------------------------------------
        # 强制跳过条件 Skip Condition

        if onset <= 0 - 3:
            continue

        if onset >= len(cluster.labels_) + 3:
            continue

        # -----------------------------------------------

        if offset <= 0:
            offset = 0

        candidate_y1_area = abs(cp.array(
            target_audio_arr_filtered_[offset * accFactor+1:onset * accFactor] -
            target_audio_arr_filtered_[offset * accFactor:onset * accFactor-1]
        ))

        sample_startpoint = int(cp.argmin(candidate_y1_area) + offset * accFactor)
        sample_endpoint = sample_startpoint - ref_length
        if sample_endpoint < 0:
            sample_endpoint = 0
        # print(sample_endpoint, sample_startpoint)
        try:
            candidate_y1_area = abs(cp.array(
                target_audio_arr_filtered_[sample_endpoint+1:sample_startpoint] -
                target_audio_arr_filtered_[sample_endpoint:sample_startpoint-1]
            ))
        except ValueError:
            sample_startpoint = sample_endpoint + ref_length
            candidate_y1_area = abs(cp.array(
                target_audio_arr_filtered_[sample_endpoint+1:sample_startpoint] -
                target_audio_arr_filtered_[sample_endpoint:sample_startpoint-1]
            ))

        candidate_y1_area = cp.sort(candidate_y1_area)[:int(len(candidate_y1_area) * ratio)]

        y1_threshold = float(cp.sum(candidate_y1_area)/(sample_startpoint-sample_endpoint) * amp)
        ref_midpoint = int(offset*accFactor + (onset-offset) * accFactor * 0.8)  # 3/4偏移量
        if ref_midpoint < sample_startpoint:
            ref_midpoint = sample_startpoint
        # print(cp.argmin(candidate_y1_area), ref_midpoint)

        # ----------------- Processing onset area --------------
        print(f"\r{audio_file}\t|\t{get_current_time()}\t|\tProcessing >> onset {onset} + offset {offset}", end="")


        # print(y1_threshold)

        countValidPiece = 0
        countBadPiece = 0
        countDSTime = -1

        while True:
            countDSTime += 1

            left_boundary = ref_midpoint + countDSTime - window_size
            right_boundary = ref_midpoint + countDSTime

            try:
                raw_value = abs(target_audio_arr_filtered_[left_boundary:right_boundary] - target_audio_arr_filtered_[left_boundary-1:right_boundary-1])
            except ValueError:
                break
            raw_value.sort()
            raw_value = raw_value[:int(len(raw_value) * ratio)]

            y1_value = sum(raw_value)/len(raw_value)

            if y1_value > y1_threshold:
                countValidPiece += 1
            else:
                countBadPiece += penalty

            countTotalPiece = countValidPiece - countBadPiece
            if countTotalPiece <= 0:
                countValidPiece = 0
                countBadPiece = 0

            if countTotalPiece >= numValid:
                final_answer = ref_midpoint + countDSTime - countValidPiece - countBadPiece
                if reverse:
                    final_answer = max_frm_num - final_answer
                time_points.append(round(final_answer / target_audio_samplerate, 6))

                # 打印答案时间
                # print(round(final_answer / target_audio_samplerate, 6))

                if 1 == 2 and not reverse:
                    plt.figure(figsize=(9, 6))
                    if low_cutoff != 0:
                        target_audio_arr_filtered_y1 = abs(bandpass_filter(
                                target_audio_obj.get_array_of_samples(),
                                low_cutoff,
                                high_cutoff,
                                target_audio_samplerate
                            )[1:] -
                            bandpass_filter(
                                target_audio_obj.get_array_of_samples(),
                                low_cutoff,
                                high_cutoff,
                                target_audio_samplerate
                            )[:-1])
                    else:
                        target_audio_arr_filtered_y1 = abs(lowpass_filter(
                                target_audio_obj.get_array_of_samples(),
                                high_cutoff,
                                target_audio_samplerate
                            )[1:] -
                            lowpass_filter(
                                target_audio_obj.get_array_of_samples(),
                                high_cutoff,
                                target_audio_samplerate
                            )[:-1])

                    plt.scatter(range(len(target_audio_arr_filtered_y1)), target_audio_arr_filtered_y1, s=1)

                    if not reverse:
                        plt.axvspan(ref_midpoint, final_answer, color="g", alpha=0.3)
                        plt.axvspan(sample_startpoint-ref_length, sample_startpoint, color="violet", alpha=0.3)
                    else:
                        print(final_answer, max_frm_num-ref_midpoint)
                        plt.axvspan(final_answer, max_frm_num-ref_midpoint, color="g", alpha=0.3)
                        plt.axvspan(max_frm_num-(sample_startpoint-ref_length), max_frm_num-sample_startpoint, color="violet", alpha=0.3)

                    plt.show()
                break
    print("\rComplete", end="\n")  # 刷新为空
    print("---↗")


    return list(set(time_points))


def process_items_with_params(params_procitems, audio_file) -> dict:

    time_points = {
        "onset": process_item(params_procitems["onset"], audio_file, reverse=False),
        "offset": process_item(params_procitems["offset"], audio_file, reverse=True)
    }
    print(time_points)
    # Generate TEXTGRID
    create_textgrid_with_time_point(
        time_points=time_points,
        audio_file_path=audio_file
    )

    return time_points




if __name__ == "__main__":

    # print(cp.cuda.runtime.getDeviceCount())
    # cp.cuda.Device(0).use()

    audio_path = r"D:\Corpus\Project_Praditor\praditor - batch"
    file_proc_list = [os.path.join(audio_path, f) for f in os.listdir(audio_path) if isAudioFile(f) and "" in f]

    # random.shuffle(file_proc_list)
    # amp, low_cutoff, high_cutoff, numValid, window_size, ratio, penalty, ref_length
    params = {
        "onset": [1.5, 220, 10800, 2400, 150, .87, 10, 1000, 0.01],
        "offset": [1.2, 200, 10000, 5000, 100, .9, 20, 1000, 0.3]
    }
    # 使用zip函数和列表推导式来转置列表
    parameters = [
        [params] * len(file_proc_list),
        file_proc_list
    ]

    threads = 4  # 四进程基本拉满效率了

    # 使用for循环
    # for file in file_proc_list:
    #     process_items_with_params(params, file)

    # 使用 ThreadPoolExecutor
    # with ThreadPoolExecutor(max_workers=12) as executor:
    #     # 使用 map 方法并行执行 process_item 函数
    #     executor.map(process_items_with_params, *params)

    # 使用 ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(process_items_with_params, *parameters, chunksize=threads))


