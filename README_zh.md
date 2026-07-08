[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](./LICENSE)
![GitHub Release](https://img.shields.io/github/v/release/Paradeluxe/Praditor)
![Downloads](https://img.shields.io/github/downloads/Paradeluxe/Praditor/total)


<h3>
    <br/>
    <br/>
</h3>


<h3 align="center">


<p align="center">
  <a href="https://github.com/Paradeluxe/Praditor">
    <img align="center" src="resources/icons/icon.png" alt="Praditor_icon" width="100" height="100">
  </a>
</p>

<p align="center">
Praditor
</p>
</h3>

<p align="center">
基于 DBSCAN 的语音起始时间自动检测工具
</p>


  <p align="center">
    <a href="https://github.com/Paradeluxe/Praditor/releases"><strong>下载 Praditor</strong></a>
     | 
    <a href="https://github.com/Paradeluxe/Praditor/blob/master/README.md"><strong>English</strong></a>
     · 
    <a href="https://github.com/Paradeluxe/Praditor/blob/master/README_zh.md"><strong>中文</strong></a>
     | 
    <a href="https://doi.org/10.3758/s13428-025-02776-2"><strong>论文</strong></a>
  </p>


<br/>


# 功能

Praditor 是一款**语音起始时间（Onset）检测器**，能自动标定语音信号的 onset 和 offset，支持两种检测模式，输出 `.TextGrid` 文件，可直接在 Praat 中使用。

> [!TIP]
> 需要**自动**标注时间和内容？试试 **[Praasper](https://github.com/Paradeluxe/Praasper)** — **一个面向心理语言学研究的 VAD 增强自动语音标注流水线**。

- **起始/结束检测（默认模式）** — 利用 DBSCAN 聚类和一阶导数阈值法检测语音事件边界，输出 `PointTier` 格式的 onset（蓝色）和 offset（绿色）标注。
- **语音活动检测（VAD 模式）** — 检测有声片段，输出 `IntervalTier` 格式的 "sound" 区间。VAD 模式固定部分参数，以 15 秒分段智能处理。
- **批量处理** — `Run All` 一键处理当前文件夹内所有音频，自动生成 `.TextGrid` 和 CSV 汇总。
- **三级参数存储** — 支持 Default（默认）/ Folder（文件夹）/ File（文件）三级参数保存，按 File → Folder → Default 优先级自动加载。VAD 模式参数独立存储（`_vad` 后缀）。
- **参数历史** — 通过 `Backward` / `Forward` 按钮在最多 10 组历史参数间切换。
- **CSV 导出** — 自动生成文件夹级别的 CSV 汇总，包含所有处理文件的检测时间戳。
- **实时预览** — `Test` 按钮可预览当前参数下的 onset/offset 数量，不修改 `.TextGrid` 结果。

> 可尝试使用 [test_audio.wav](https://github.com/Paradeluxe/Praditor/raw/master/resources/test_audio/test_audio.wav) 或 [test_audio_mp3.mp3](https://github.com/Paradeluxe/Praditor/raw/master/resources/test_audio/test_audio_mp3.mp3) 体验 **Praditor**。
> `test_audio_mp3.mp3` 来源于[在线资源](https://accent.gmu.edu/browse_language.php?function=detail&speakerid=462)，`test_audio.wav` 和 `test_large_audio.wav` 来自我们的实验数据。


# GUI 界面说明

![audio2textgrid.png](instructions/audio2textgrid.png)

## 标题栏

| 按钮 | 功能 |
|------|------|
| `File` | 导入音频文件（支持 `.mp3`, `.wav`, `.ogg`, `.aac`, `.flac`, `.amr`, `.wma`, `.aiff`） |
| `?` (帮助) | 打开使用文档 |
| `Run` | 对当前文件运行检测 |
| `Run All` | 批量处理当前文件夹内所有音频 |
| `Test` | 预览当前参数下能检测到的 onset/offset 数量（不修改 `.TextGrid`） |
| `Stop` | 停止正在运行的检测 |
| `Trash` | 清除显示标注（不修改 `.TextGrid`） |
| `Read` | 从 `.TextGrid` 重新加载标注 |
| `Onset` | 切换蓝色 onset 标注显示 |
| `Offset` | 切换绿色 offset 标注显示 |
| `◀` / `▶` | 切换上一首 / 下一首音频 |

## 音频查看器

显示波形、onset/offset 标记和时间标签。支持鼠标、键盘和触控板缩放/滚动。

### 鼠标与键盘
- `滚轮 ↑↓` — 缩放振幅
- `Ctrl` + `滚轮 ↑↓` — 缩放时间轴
- `Shift` + `滚轮 ↑↓` — 滚动时间轴
- `F5` — 播放 / 暂停音频；任意键停止

### 触控板
- 纵向滑动 — 缩放振幅
- 横向滑动 — 缩放时间轴
- 横向滑扫 — 滚动时间轴

> macOS 触控板时间轴缩放可能无效，可使用 `Command + I` / `Command + O` 替代。

## 参数滑块

onset（蓝色）和 offset（绿色）各有 9 个独立可调参数：

| 参数 | 说明 |
|------|------|
| `Threshold` | 决定实际阈值的系数（基线 × 系数 = 实际阈值） |
| `NetActive` | 触发检测所需的累计有效帧数 |
| `Penalty` | 低于阈值帧的惩罚系数 |
| `RefLen` | 用于生成基线的参考段长度 |
| `KernelFrm%` | 核内保留的帧比例 |
| `KernelSize` | 核大小（单位：帧） |
| `EPS%` | DBSCAN 聚类的邻域半径 |
| `LowPass` | 带通滤波器的低频截止频率 |
| `HighPass` | 带通滤波器的高频截止频率 |

VAD 模式下，offset 滑块隐藏，`Penalty`、`RefLen`、`KernelFrm%`、`KernelSize` 固定为 VAD 优化默认值。

## 工具栏

| 按钮 | 功能 |
|------|------|
| `Default` | 使用应用级默认参数 |
| `Folder` | 使用当前文件夹的 `params.txt` / `params_vad.txt` |
| `File` | 使用与音频同名的 `.txt` 参数文件 |
| `Save` | 保存当前参数到选中模式 |
| `Reset` | 从选中模式的文件重新加载参数 |
| `Backward` / `Forward` | 浏览参数历史（每种模式最多 10 组） |
| `VAD` | 切换 VAD 模式 |
| `1/10` | 当前参数索引 / 总组数 |

**优先级**: File > Folder > Default。多模式同时选中时，`Save` 写入所有选中位置；`Reset` 从存在且最高优先级的位置加载。


# 算法简述

## 1. 算法流程

1. **带通滤波** — 设定低频 cutoff 和高频 cutoff，滤除不感兴趣的频率。
2. **最大池化降采样（Max-pooling Downsampling）** — 将原信号采样率降至 40Hz，即每秒 N 帧 → 将 N 帧每 40 帧为一组取最大值，得到 40 个值/秒的信号。降采样极大地减小了后面聚类和检测的运算量。
3. **DBSCAN 聚类** — 为了找到"接近基线"的数据点（即"静音"段中的点）：
   - Step 1: 将当前帧值（x）与下一帧值（y）构成二维点 (x, y)。第一帧和最后一帧例外（可使用 padding）。
   - Step 2: 对形成的二维点执行 DBSCAN 聚类。距离度量为 Manhattan distance。
   - Step 3: 聚类后，取中心点距离零点最近的簇（即所谓的"最佳基线簇"），该簇中的点为"准基线点"。
   - **dBSCAN 聚类图解**：

     <p align="center"><img width="70%" src="instructions/dbscan.png"></p>

4. **一阶导数阈值法（First-derivative Thresholding）** — 对每个 onset 候选区间，采用自适应阈值 + 滑动核算法，找到一阶导数跃变点：
   - Step 1: 在候选区间内向内缩进（onset 缩进 80%，offset 缩进 20%），设定为参考中点。
   - Step 2: 从参考中点向 reference 段取一个长度为 ref_len 的窗口，计算窗口内一阶导数的 top ratio% → cumsum → sup_threshold。
   - Step 3: 从参考中点向检测方向，以一个滑动窗口逐个采样点移动。在每个采样点计算窗口内一阶导数的 top ratio%（见上面参数说明），若其 sum 超过 sup_threshold，则计为 countValid。
   - Step 4: 无效点积攒 penalty 倍容忍度。countValid = countValid - countBad * penalty。
   - Step 5: countValid 达到 numValid 时认定为 onset/offset。

## 2. 检测对象

Praditor 可检测两种目标：

### a. 句子 / 短语起始（称为 onset 和 offset）

默认模式（Default mode）针对的是句子 / 短语边界的起始和结束时间。onset 和 offset 检测逻辑相同，区别在于 offset 检测时信号反向处理（flip + detect onset + flip back），基本原理一致。

### b. 任意有声事件（Voice Activity Detection, VAD）

VAD 模式检测任意有声片段，作为 onset/offset 的初级筛选。VAD 模式下 offset 参数由 onset 参数强制复制，kenerl 参数（KernelFrm%, KernelSize, RefLen, Penalty）固定不变。

## 3. 核（Kernel）

Kernel 即经过比例筛选后的滑动窗口，由 KernelFrm% 和 KernelSize 两个参数共同决定。

假设 KernelSize = 50 帧，KernelFrm% = 80%。算法运行时，取一个 50 帧长的窗口 → 其中 80% 的帧（即 40 帧）保留作为核 → 用核内信号的一阶导数值与阈值比较。

## 4. 时间复杂度特征

以下因素影响检测速度（按影响程度排序）：

- 音频时长
- `RefLen`（参考段长度 — 越长，每个候选区间计算量越大）
- `KernelSize`（核大小 — 越大，滑动窗口越慢）
- onset/offset 候选区间数量

总时间复杂度约为 O(audio_length × ref_len × kernel_size × n_candidates)。


# 视频教程

<div align="center">

<div style="display: flex; justify-content: space-between; align-items: center;">
  <a href="https://www.bilibili.com/video/BV1UnKWzmEBz/"><img src="./instructions/bilibili.PNG" width="30%" /></a>
  <a href="https://youtu.be/68bqwj3q-Ag?si=yAwNLceIqdiQuNFE"><img src="./instructions/youtube.PNG" width="30%" /></a>
</div>

</div>


# 微调（Fine-tuning）指导

> 懂基础会用即可。懂算法更好调参。

- **基础学习**: 阅读 [**快速修复**](markdown/quick_fix.md) 第一部分。
- **进阶学习**: 阅读 [**快速修复**](markdown/quick_fix.md#detailed-introduction) 第二部分。
- **专家学习**: 阅读 [**参数详解**](./markdown/params.md)。


# 数据与材料

如需获取开发 **Praditor** 所用的数据集，请访问 [我们的 OSF 存储](https://osf.io/9se8r/)。


# 引用

如在研究中使用 **Praditor**，请引用以下论文：

```
Liu, Z., Yu, X., Hu, W.C. et al. Praditor: A DBSCAN-based automation for speech onset detection. Behav Res 57, 247 (2025). https://doi.org/10.3758/s13428-025-02776-2
```

或从论文页面的 [**About this article**](https://link.springer.com/article/10.3758/s13428-025-02776-2#article-info) 下载 `.ris` 引用文件。


# 致谢

感谢以下各位的卓越贡献！

- 感谢 **YU Xinqi（余新奇）**、**马蕴潇博士**、**ZHANG Sifan（张思凡）** 在验证 **Praditor** 算法有效性中的工作。
- 感谢 **HU Wing Chung（胡颖聪）** 为 macOS（arm64 和 universal2）打包 **Praditor**。
- 感谢澳门大学 **张浩云教授** 和华南师范大学 **王瑞明教授** 的指导和支持。

同时感谢以下资助：

- 国家自然科学基金（32200845），澳门特别行政区科学技术发展基金（FDCT, 0153/2022/A），澳门大学多年研究基金（MYRG2022-00148-ICI）。


# 许可协议

Praditor 采用 **AGPL v3 + 商业许可** 双许可模式（[LICENSE](./LICENSE)）：

- **AGPL v3**（默认）：开源、免费。学术 / 个人 / 非营利 / 小团队均可直接使用。
  唯一要求：如果你将 Praditor 作为网络服务提供，必须公开源码。
- **商业许可**：如果不接受 AGPL 的 copyleft 要求（例如商业产品集成、SaaS 服务、
  大公司内部使用），可购买商业许可来免除 AGPL 义务。

详见 [COMMERCIAL-LICENSE.md](./COMMERCIAL-LICENSE.md)。


# 作者

**Praditor** 由澳门大学认知与脑科学研究中心 **刘正远** 编写和维护。

如有关于 **Praditor** 使用、算法细节的疑问，或需要定制脚本（音频导出、Excel 表格等），欢迎通过 `zhengyuan.liu@connect.um.edu.mo` 或 `paradeluxe3726@gmail.com` 与我联系。
