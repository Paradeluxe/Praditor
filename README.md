
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
> [mp3_test_audio.mp3](https://github.com/Paradeluxe/Praditor/raw/master/test_audio/mp3_test_audio.mp3)
> on _**Praditor**_.

# Video instruction (bilibili)
<div align="center">
  <a href="https://www.bilibili.com/video/BV1i3QPYkEzP/?share_source=copy_web&vd_source=04f6059f57092624c36ac4e9fc1efe10">
    <img src="instructions/Praditor_intro_cover.png" alt="Praditor_intro_cover" style="width:80%;">
  </a>
</div>

# Basic Operation

Although I have prepared various buttons in this GUI, you do not have to use them all.

The simplest and easiest procedure is (1) import audio files, (2) hit the `extract` button,
(3) [optional] you are not happy about the results, fine-tune the parameters and hit the `extract` button again. 
**Until you are happy about the results, repeat step (2) and (3).**

## General

### 🗃️ import audio file(s)

`File` -> `Read files...` -> Select your target audio file

_Note_. All the other audio files will also be added to the list.


### ▶️ run algorithm and extract onsets

Hit `Extract`. Wait for a while until the results come out. Onsets are in blue, offsets are in green.


### 🔊 play and stop

Press <kbd>F5</kbd> to play the audio signal that is currently presented in the window. 

Press <kbd>any key</kbd> to stop playing.

### ⏮️⏭️ next/previous audio file

Hit `Next`/`Prev`.

## .TextGrid related

### 🧹 I wanna temporarily clear the annotations

Hit `Clear`. This does not delete/change the .TextGrid file. It's safe.

### ✍️ Oh no, I want the cleared annotations back

Hit `Read`. _Praditor_ will go back to the .TextGrid and present whatever is in it.

### 👀 Hide/Show annotations

Press `Onset`/`Offset` (sometimes they are the number of Onsets/Offsets). 

## 📊 Parameters 

`Current/Default` Display default parameters or parameters for the current file

`Save` Save the displayed parameters as Current/Default

`Reset` Reset the displayed parameters to the last time you saved it.


## Audio signal

### 🖱️⌨️ Mouse & Keyboard
<kbd>Wheel ↑</kbd>/<kbd>Wheel ↓</kbd> to zoom-in/out at **amplitude**

<kbd>Ctrl/Command</kbd>+<kbd>Wheel ↑</kbd>/<kbd>Wheel ↓</kbd> to zoom-in/out at **timeline**

<kbd>Shift</kbd>+<kbd>Wheel ↓</kbd>/<kbd>Wheel ↑</kbd> to move forward/backward in **timeline** 

### 💻 Touchpad
`↑✌↑`/`↓✌↓` to zoom-in/out at **amplitude**

`←✌→`/`→✌←` to zoom-in/out at **timeline**

`←←✌`/`✌→→` to move forward/backward in **timeline** 


## Fine-tuning guidance

> Basic understanding is enough. Understanding the algorithm is better.

- **Basic knowledge**: Go to the first section of [**Quick Fix**](markdown/quick_fix.md).
- **Advanced knowledge**: Go to the second section of [**Quick Fix** (Detailed Introduction)](markdown/quick_fix.md/#detailed-introduction).
- **Expert knowledge**: Go to [**Parameter**](./markdown/params.md).



# Data and Materials

If you would like to download the datasets that were used in developing Praditor, please refer to [our OSF storage](https://osf.io/9se8r/).


# Contact us
_**Praditor**_ is written and maintained by **Tony, Liu Zhengyuan** from Centre for Cognitive and Brain Sciences, University of Macau.

If you have any questions in terms of how to use _Praditor_ or its algorithm details, or you want me to help you write some additional
scripts like **export audio files**, **export Excel tables**,
feel free to contact me at `zhengyuan.liu@connect.um.edu.mo` or `paradeluxe3726@gmail.com`.


## 🙌 Acknowledgments
This project thrives thanks to these remarkable contributors:
- Thank **Yu Xinqi**, **Dr. Ma Yunxiao**, **Zhang Sifan** for their work in validating the effectiveness of _Praditor_'s algorithm.
- Thank **Hu Wing Chung** for her work in packaging _Praditor_ for macOS (arm64 and universal2)
- Thank **Prof. Zhang Haoyun** (University of Macau) and **Prof. Wang Ruiming** (South China Normal University) for their guidance and support for this project
