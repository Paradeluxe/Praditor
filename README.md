# Praditor: A DBSCAN-Based Automation for Speech Onset Detection

## Download

### 1. What to download:

Refer to **[Release](https://github.com/Paradeluxe/Praditor/releases)** section for the latsest update, or, **[dist](https://github.com/Paradeluxe/Praditor/tree/master/dist) -> [Praditor_GUI.exe](https://github.com/Paradeluxe/Praditor/raw/master/dist/Praditor_GUI.exe?download=)**, this .exe should work on its own and bring you the GUI version Praditor.

If you want to modify these .py files, kindly refer to **2. Deploy Yourself**

### 2. Deploy Yourself:

Only **Praditor_GUI.py**, **Praditor_tool.py**, **Praditor_run.py**, **requirements.txt**, **parameters.txt** are necessary. 

Put them in the same folder and they should work.

First thing to do: `pip install -r requirements.txt` (For some, it's `python3 -m pip install -r requirements.txt`)

- If you want to use GUI, run **Praditor_GUI.py**
- If you want to use process a lot of files automatically, run **Praditor_run.py**


### 3. In case you want to try GPU acceleration

Implement the correct versions of **CuPy**, and replace the corresponding file(s) with the one(s) in the **cupy_version** folder

#### How to pip CuPy in your OS
- For Nvidia user, kindly refer to [Installing CuPy](https://docs.cupy.dev/en/stable/install.html#installing-cupy)
- For AMD user, kindly refer to [Using CuPy on AMD GPU (experimental)](https://docs.cupy.dev/en/stable/install.html#using-cupy-on-amd-gpu-experimental)

## Annotation

As designed and tested, there are two ways of fine-tuning Praditor:

> For the record, I only intend to provide a general idea of how you can turn up/down certain parameter(s).

### If you include inhale (breath) as part of speech
Praditor is originally designed this way, I believe it's better to consider the **inhale** that is seamlessly followed up by
 other parts of speech should also be considered **speech**. 

In other words, if noise signals (silence) were in between inhale and speech, Praditor shall be able to detect the silence
and reject it as part of speech.

To annotate in this way, I recommend that you start with the original parameters that is written in the Praditor, 
then adjust the parameters following the below guidance:

1. If Praditor annotates a little bit too earlier than the actual onset:
   - Turn up ***y1_amp_factor***
   - Turn up ***Num_ValidFrm***

2. If Praditor annotates a little bit too later than the actual onset:
   
   - Do the opposite as above.

3. If the noise intervals have many spikes:
   - Turn up ***Kernel Size*** (might work) 
   - Turn down ***Signal_Ratio*** (might work) - e.g., Signal_Ratio = 0.90 -> 10% of points in each window will be discarded

   > These two shall be a pair, you might want to tune them together to see what works best for the target audio.
   
4. Other parameters:
   - ***Penalty*** Most of the time changing it won't make any difference. Performance might be worse if it is turned down (smaller than 10).
   - ***Ref_Length*** Its getting smaller might help avoid unexpected spiky noise signals.
   - ***eps_Ratio*** Think of it as the water level - the smaller it gets, the more onsets you might get.
   - ***Filter_Cutoff*** For a typical 44100-Hz 16-bit .wav audio, I use 200-10800 as the starting point. You might want to test it out yourself.

### If you want to exclude inhale (breath)

These two below matter:

1. Select a tiny ***y1_amp_factor*** (like 1.05)
2. Select a large ***Num_ValidFrm***

### If you want to change the upper/lower limit of parameters in GUI

- Go to **Praditor_GUI.py**. 
- Repack using *pyinstaller* if you intend to use .exe version of Praditor.


## From Authors
I'm new to GitHub and still learning how to use it. Please forgive me if there is something I missed. Thx XD

Feel free to contact me at `paradeluxe3726@gmail.com` or `zhengyuan.liu@connect.um.edu.mo`.
