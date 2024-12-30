from pydub import AudioSegment
import numpy as np
import scipy.io.wavfile as wavfile

# 音频文件路径
audio_file_path = r'C:\Users\18357\Desktop\Praditor\test_audio.wav'

# 使用pydub读取音频文件
audio_segment = AudioSegment.from_file(audio_file_path)
# 将音频数据转换为NumPy数组
# 注意：pydub的get_array_of_samples()返回的是int16的样本值，需要归一化到-1.0到1.0的范围
pydub_samples = audio_segment.get_array_of_samples()
pydub_channels = audio_segment.channels
pydub_sample_width = audio_segment.sample_width
pydub_frame_rate = audio_segment.frame_rate
pydub_array = np.array(pydub_samples) #/ (2**(pydub_sample_width * 8 - 1))

# 使用scipy读取音频文件
scipy_sample_rate, scipy_data = wavfile.read(audio_file_path)
# scipy读取的数据已经是NumPy数组，需要归一化到-1.0到1.0的范围
scipy_array = scipy_data #/ (2**15)





# 打印结果
print("Pydub:")
print("Sample Rate:", pydub_frame_rate)
print("Channels:", pydub_channels)
print("Sample Width:", pydub_sample_width)
print("Array Shape:", pydub_array.shape)
print("Array Sample:", pydub_array[:5])

print("\nSciPy:")
print("Sample Rate:", scipy_sample_rate)
print("Array Shape:", scipy_array.shape)
print("Array Sample:", scipy_array[:5])