
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![GitHub Release](https://img.shields.io/github/v/release/Paradeluxe/Praditor)
![Downloads](https://img.shields.io/github/downloads/Paradeluxe/Praditor/total)


<h3>
    <br/>
    <br/>
</h3>


<h3 align="center">


<p align="center">
  <a href="https://github.com/Paradeluxe/Praditor">
    <img align="center" src="icon.png" alt="Praditor_icon" width="100" height="100">
  </a>
</p>

<p align="center">
Praditor
</p>
</h3>

<p align="center">
A DBSCAN-Based Automation for Speech Onset Detection
</p>


  <p align="center">
    <a href="https://github.com/Paradeluxe/Praditor/releases"><strong>Download Praditor</strong></a>
     | 
    <a href="https://github.com/Paradeluxe/Praditor/blob/master/README.md"><strong>English</strong></a>
     · 
    <a href="https://github.com/Paradeluxe/Praditor/blob/master/README_zh.md"><strong>中文</strong></a>
     | 
    <a href="https://doi.org/10.3758/s13428-025-02776-2"><strong>Our Paper</strong></a>
  </p>

<br/>


# Features
Praditor is a **speech onset detector** that helps you find out boundaries between silence and sound **automatically**.

![audio2textgrid.png](instructions/audio2textgrid.png)

Praditor works for both **single-onset** and **multi-onset** audio files **without any language limitation**. 
It generates output as PointTiers in .TextGrid format. 

 - Onset/Offset Detection
 - Silence Detection

Praditor also allows users to adjust parameters in the Dashboard to get a better performance.

> You can try [test_audio.wav](https://github.com/Paradeluxe/Praditor/raw/master/test_audio/test_audio.wav) and 
> [test_audio_mp3.mp3](https://github.com/Paradeluxe/Praditor/raw/master/test_audio/test_audio_mp3.mp3) on _**Praditor**_.

# Video instruction
<div align="center">

<div style="display: flex; justify-content: space-between; align-items: center;">
  <a href="https://www.bilibili.com/video/BV1UnKWzmEBz/"><img src=".\instructions\bilibili.PNG" width="30%" /></a>
  <a href="https://youtu.be/68bqwj3q-Ag?si=yAwNLceIqdiQuNFE"><img src=".\instructions\youtube.PNG" width="30%" /></a>
</div>


</div>


# 📚 Fine-tuning guidance

> Basic understanding is enough. Understanding the algorithm is better.

- **Basic knowledge**: Go to the first section of [**Quick Fix**](markdown/quick_fix.md).
- **Advanced knowledge**: Go to the second section of [**Quick Fix** (i.e., Detailed Introduction)](markdown/quick_fix.md#detailed-introduction).
- **Expert knowledge**: Go to [**Parameter**](./markdown/params.md).


# 🙌 Play with GUI

Although I have prepared various buttons in this GUI, you do not have to use them all.

The simplest and easiest procedure is (1) import audio files, (2) hit the `extract` button,
(3) [optional] you are not happy about the results, fine-tune the parameters and hit the `extract` button again. 
**Until you are happy about the results, repeat step (2) and (3).**

## General

`File` -> `Read files...` -> Import your target audio file (**Recommend**: >= 44.1 kHz; **Accept**: >= 8 kHz)

`Run` Run algorithm and extract onsets. Wait for a while until the results come out. Onsets are in blue, offsets are in green.

`Test` Test how many onsets/offsets may be found using the presented parameters. This function does not affect .TextGrid.
> If the number meets the expectation, hit `Run` to get the final annotation.

<kbd>F5</kbd> to play the audio signal that is currently presented in the window, and <kbd>Any Key</kbd> to stop playing.

`Next`/`Prev` Move to the next/previous audio file

## .TextGrid related

`Clear` If you want to temporarily clear the annotations, this does not delete/change the .TextGrid file. It's safe.

`Show` If you want the cleared annotations back. _Praditor_ will go back to the .TextGrid and present whatever is in it.

`Onset`/`Offset` to hide/show annotations on the screen (also does not change the .TextGrid). 
> _Note_: **Onsets** and **offsets** are controlled by two DIFFERENT sets of parameters, 
> which means there is **no strict guarantee on 1-to-1 correspondence**.
> Offset annotation is the onset annotation on the reversed audio.

## Parameters 

`Current/Default` Display default parameters or parameters for the current file

`Save` Save the displayed parameters as Current/Default

`Reset` Reset the displayed parameters to the last time you saved it

`Last` Go back to the last set parameters you have run


## Audio signal

### Mouse & Keyboard 🖱️⌨️ 
<kbd>Wheel ↑</kbd>/<kbd>Wheel ↓</kbd> to zoom-in/out at **amplitude**

<kbd>Ctrl/Command</kbd>+<kbd>Wheel ↑</kbd>/<kbd>Wheel ↓</kbd> to zoom-in/out at **timeline** (<kbd>Ctrl/Command</kbd>+<kbd>I</kbd>/<kbd>O</kbd> also works)

<kbd>Shift</kbd>+<kbd>Wheel ↓</kbd>/<kbd>Wheel ↑</kbd> to move forward/backward in **timeline**


### Touchpad 💻
`↑✌↑`/`↓✌↓` to zoom-in/out at **amplitude**

`←✌→`/`→✌←` to zoom-in/out at **timeline**
> **Timeline zoom** might not work in macOS. Use `Command + I/O` instead.

`←←✌`/`✌→→` to move forward/backward in **timeline** 



# 🗃️ Data and Materials

If you would like to download the datasets that were used in developing _Praditor_, please refer to [our OSF storage](https://osf.io/9se8r/).


# 🙌 Acknowledgments
Shout out to these remarkable contributors!!
- Thank **YU Xinqi**, **Dr. MA Yunxiao**, **ZHANG Sifan** for their work in validating the effectiveness of _Praditor_'s algorithm.
- Thank **HU Wing Chung** for her work in packaging _Praditor_ for macOS (arm64 and universal2)
- Thank **Prof. ZHANG Haoyun** (University of Macau) and **Prof. WANG Ruiming** (South China Normal University) for their guidance and support for this project

Also, the funding:
- This project was funded by the National Natural Science Foundation of China (32200845),
the Science and Technology Development Fund, Macao S.A.R (FDCT, 0153/2022/A), and the Multi-Year Research Grant (MYRG2022-00148-ICI) from the University of Macau to Haoyun Zhang.

  
# 📨 Contact us
_**Praditor**_ is written and maintained by **Tony, Liu Zhengyuan** from Centre for Cognitive and Brain Sciences, University of Macau.

If you have any questions in terms of how to use _Praditor_ or its algorithm details, or you want me to help you write some additional
scripts like **export audio files**, **export Excel tables**,
feel free to contact me at `zhengyuan.liu@connect.um.edu.mo` or `paradeluxe3726@gmail.com`.

