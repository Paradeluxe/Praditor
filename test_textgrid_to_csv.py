import os
import sys
import tempfile

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.detection import create_textgrid_with_time_point

# 创建一个临时的WAV文件用于测试
temp_dir = tempfile.gettempdir()
test_audio_path = os.path.join(temp_dir, "test_audio.wav")

# 创建一个简单的WAV文件（使用pydub库）
from pydub import AudioSegment

# 创建一个1秒的静音WAV文件
silence = AudioSegment.silent(duration=1000)  # 1秒静音
silence.export(test_audio_path, format="wav")

print(f"创建了测试音频文件: {test_audio_path}")

# 示例数据
# 为VAD模式使用相同长度的onset和offset
vad_onsets = [0.2, 0.4, 0.6, 0.8]  # 4个onset
vad_offsets = [0.3, 0.5, 0.7, 0.9]  # 4个offset

# 为默认模式使用不同长度的onset和offset
default_onsets = [0.2, 0.4, 0.6, 0.8, 1.0]  # 5个onset
default_offsets = [0.3, 0.5, 0.7]  # 3个offset

# 测试VAD模式
print("\n测试VAD模式...")
create_textgrid_with_time_point(test_audio_path, is_vad_mode=True, onsets=vad_onsets, offsets=vad_offsets)

# 测试默认模式
print("\n测试默认模式...")
create_textgrid_with_time_point(test_audio_path, is_vad_mode=False, onsets=default_onsets, offsets=default_offsets)

# 检查生成的文件
print("\n检查生成的文件:")
test_filename = os.path.splitext(os.path.basename(test_audio_path))[0]

# 检查VAD模式生成的文件
vad_textgrid = os.path.join(temp_dir, f"{test_filename}_vad.TextGrid")
vad_csv = os.path.join(temp_dir, f"{test_filename}_vad.csv")

if os.path.exists(vad_textgrid):
    print(f"✓ VAD模式TextGrid文件已生成: {vad_textgrid}")
else:
    print(f"✗ VAD模式TextGrid文件未生成")

if os.path.exists(vad_csv):
    print(f"✓ VAD模式CSV文件已生成: {vad_csv}")
    # 显示CSV文件内容
    print("CSV文件内容:")
    with open(vad_csv, "r") as f:
        content = f.read()
        print(content)
        # 统计sound行数
        sound_count = content.count("sound")
        print(f"sound区间数量: {sound_count}")
else:
    print(f"✗ VAD模式CSV文件未生成")

# 检查默认模式生成的文件
default_textgrid = os.path.join(temp_dir, f"{test_filename}.TextGrid")
default_csv = os.path.join(temp_dir, f"{test_filename}.csv")

if os.path.exists(default_textgrid):
    print(f"\n✓ 默认模式TextGrid文件已生成: {default_textgrid}")
else:
    print(f"\n✗ 默认模式TextGrid文件未生成")

if os.path.exists(default_csv):
    print(f"✓ 默认模式CSV文件已生成: {default_csv}")
    # 显示CSV文件内容
    print("CSV文件内容:")
    with open(default_csv, "r") as f:
        print(f.read())
else:
    print(f"✗ 默认模式CSV文件未生成")

# 清理临时文件
os.remove(test_audio_path)
if os.path.exists(vad_textgrid):
    os.remove(vad_textgrid)
if os.path.exists(vad_csv):
    os.remove(vad_csv)
if os.path.exists(default_textgrid):
    os.remove(default_textgrid)
if os.path.exists(default_csv):
    os.remove(default_csv)

print("\n测试完成，临时文件已清理")
