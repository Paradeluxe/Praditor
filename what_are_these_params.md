
# Quick instruction

**Basically, all you need to know is here.**

_Praditor_ employs 9 parameters divided into two functional categories: (1) **Denoising** and (2) **Defining** parameters.
The latter establishes onset definitions, while the former eliminates noise that might compromise Praditor's algorithmic performance.


## Denoising Parameters
(LowPass, HighPass, KernelSize, KernelFrm%)

### 1. Bandpass Filtering (First Stage)
- _**LowPass**_ (int, Hz): High cutoff frequency
- _**HighPass**_ (int, Hz): Low cutoff frequency

All recordings contain inherent noise to some extent.
Our focus lies specifically on noise that impacts Praditor's performance.
You should prioritize frequency bands exhibiting higher energy/amplitude contrast near onsets.
Removing low-contrast frequency bands is supposed to enhance annotation accuracy and precision.

### 2. Kernel Smoothing (Second Stage, During Scanning)
- **_KernelFrm%_** (float): Percentage of frames retained in kernel window (e.g., 0.97 = discard top 3% frames by absolute value)
- **_KernelSize_** (int, frame): Kernel window size in frames (e.g., 100 = 100-frame window)

We need, and only need, the trend of the audio signal to tell where the onset is, instead of the spiky ups and downs (i.e., high frequency components).
What the kernel smoothing does here is to remove the spiky part and keep the trend of audio signal.

## Definition Parameters
(Threshold, CountValid, Penalty, RefLen, EPS%)

### 1. Number of onsets
- **_EPS%_** (float): Radius ratio calculated from the 80th percentile of absolute amplitudes

Praditor's unique multi-onset detection capability derives from DBSCAN clustering pre-thresholding.
This technique identifies potential onset regions through density-based separation:
(1) Background noise forms dense clusters near the coordinate origin;
(2) Speech signals create sparse clusters away from the origin.

The EPS% parameter optimizes boundary delineation between clusters.
Increased EPS% incorporates transitional data points (e.g., pauses during utterance), while decreased values exclude them from onset annotations.

### 2. Thresholding Parameters
* **_RefLen_** (int, frame): Reference signal length for baseline calculation
* **_Threshold_** (float, >1.0): Amplitude coefficient (baseline × coefficient = actual threshold)
* **_CountValid_** (int) Onset qualification standard (valid count = above-threshold frames - [below-threshold frames × penalty])
* **_Penalty_** (float, >1.0): Weight applied to below-threshold frames

With DBSCAN clustering, we are able to pinpoint all the silence segments. But it is the boundaries between silence and sound segments that we care about, right? So, what we do to search for each of these boundaries is:

(1) We can generate a baseline by determine a reference segment (with RefLen parameter) that is totally inside a silence segment, which follows a basic principle that “Background noise is baseline”.

(2) We time the baseline with a coefficient, Threshold parameter. It is mostly of time around 1.3, but has to be larger than 1.0 at least, because another principle we follow here is “Sound should be louder than the background noise/silence”.

(3) We set frames that come after the reference segment as onset candidate and check their validity by scanning frames after them. Above-threshold frames count as +1, and below-threshold frames count as -1 multiplied by Penalty parameter. The penalty parameter acts as a sensitivity control: higher values increase rejection of onset candidates containing silent intervals (e.g., inter-word pauses), while lower values permit greater tolerance. We add these values up one by one until one of the two situations is met. If the number hits CountValid parameter, then this onset candidate is determined as an actual onset; if it becomes less or equal to zero, we move on to the next onset candidate.



