[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![GitHub Release](https://img.shields.io/github/v/release/Paradeluxe/Praditor)
![Downloads](https://img.shields.io/github/downloads/Paradeluxe/Praditor/total)

<br/>
<br/>


<p align="center">
  <a href="https://github.com/Paradeluxe/Praditor">
    <img align="center" src="icon.png" alt="Praditor_icon" width="100" height="100">
  </a>
</p>



<h3 align="center">Praditor</h3>

<p align="center">
A DBSCAN-Based Automation for Speech Onset Detection
</p>


  <p align="center">
    <a href="https://github.com/Paradeluxe/Praditor/releases"><strong>Download Praditor</strong></a>
    <br/>

  </p>


## Features
Praditor is a **speech onset detector** that helps you find out all the possible boundaries between silence and sound sections **automatically**.

![audio2textgrid.png](instructions/audio2textgrid.png)

Praditor works for both single-onset and multi-onset audio files without any language limitation. 
It generates output as PointTiers in .TextGrid format. 

 - Onset/Offset Detection
 - Silence Detection

To get a better performance, Praditor can also allow users to adjust parameters in the Dashboard.

## From Authors
If you have any questions in terms of how to use Praditor or its algorithm details,
feel free to contact me at `zhengyuan.liu@connect.um.edu.mo` or `paradeluxe3726@gmail.com`.

I'm new to GitHub and still learning how to use it. Please forgive me if there is something I missed. Thx XD

## How to use Praditor?

### 1. Import your audio

`File` -> `Read files...` -> Select your target audio file

![import_audio.png](instructions/import_audio.png)

### 2. Play with Praditor

![displaySignalArray.png](instructions/displaySignalArray.png)

For onset/offset,
- `Run` Apply Praditor Algorithm on the current Audio
- `Prev` & `Next` Go to previous/next Audio
- `Read` Read time points from current Audio's .TextGrid results
- `Clear` Clear time points that are being displayed (but no change to .TextGrid)
- `Onset` & `Offset` Show/Hide Onsets/Offsets

For parameters,
- `Current/Default` Display default parameters or parameters for the current file
- `Save` Save the displayed parameters as Current/Default
- `Reset` Reset the displayed parameters to the last time you saved it.

On the menu...
- `File` > `Read files...` > Select an audio file
- `Help` > `Parameters` > Show quick instruction on how our parameters work

## How does Praditor's parameters work?
![import_audio.png](instructions/import_audio.png)

## Data and Materials

If you would like to download the datasets that were used in developing Praditor, please refer to [our OSF storage](https://osf.io/9se8r/)
.


