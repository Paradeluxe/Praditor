# Praditor: A DBSCAN-Based Automation for Speech Onset Detection

## Download

### 1. What to download:

Refer to **[Release](https://github.com/Paradeluxe/Praditor/releases)** section for the latsest update, or, **[dist](https://github.com/Paradeluxe/Praditor/tree/master/dist) -> [Praditor_GUI.exe](https://github.com/Paradeluxe/Praditor/raw/master/dist/Praditor_GUI.exe?download=)**, this .exe should work on its own and bring you the GUI version Praditor.

If you want to modify these .py files, kindly refer to **2. Deploy Yourself**

### 2. Deploy Yourself:

Only **Praditor_GUI.py**, **Praditor.py**, **clustering_DBSCAN_quick.py** are necessary, and maybe **parameters.txt**. Put them in the same folder and they should work.
- If you want to use GUI, run **Praditor_GUI.py**
- If you want to use process a lot of files automatically, run **clustering_DBSCAN_quick.py**


### 3. In case you want to try GPU acceleration

Implement the correct versions of **CuPy**, and replace the corresponding files with the ones in the **cupy_version** folder

#### How to pip CuPy in your os
- For Nvidia user, kindly refer to [Installing CuPy](https://docs.cupy.dev/en/stable/install.html#installing-cupy)
- For AMD user, kindly refer to [Using CuPy on AMD GPU (experimental)](https://docs.cupy.dev/en/stable/install.html#using-cupy-on-amd-gpu-experimental)

## Annotation

As designed and tested, there are two ways of fine-tuning Praditor:

> For the record, I intend to provide a general idea of how you should turn up/down certain parameter(s).

- 

> PS: I'm new to GitHub and still learning how to use it. Please forgive me if there is something I missed. Thx XD
