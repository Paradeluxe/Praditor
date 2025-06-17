## What's New ✨
### Play Audio
- Now you can play the audio while double-checking annotation

### Zoom-in/out like Praat
- Now _Praditor_ allows users to zoom in/out at timeline by pressing `ctrl/command + I/O`



## Which Edition to Download 🛒
_**Praditor**_ has been tested on **Win11** and **macOS** (≥10.14.6). Win10 should work as well.
- `full` version = `sklearn` embedded
- `light` version = identical output with no `sklearn` embedded

They produces the same answers with slight difference in processing speed. And, `light` version is generally smaller in size.

| System | Format | Recommend | Compatible |
|:---:|:---:|:---:|:---:|
| **Windows** | .exe |**x64, AMD64** (**[full](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_win.exe)**) | x64, AMD64 ([full](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_win.exe), [light](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_win_light.exe)) |
| **macOS** (M-series, macOS ≥15) | .app |  **arm64** (**[full](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_mac_arm64.tar.gz)**) | arm64 ([full](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_mac_arm64.tar.gz), [light](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_mac_arm64_light.tar.gz)), universal2 ([light](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_mac_universal2_light.tar.gz))  |
| **macOS** (Intel, or M-series,  macOS ≤14) | .app | **universal2** (**[light](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_mac_universal2_light.tar.gz)**) | universal2 ([light](https://github.com/Paradeluxe/Praditor/releases/download/v1.3.0/Praditor_v1.3.0_mac_universal2_light.tar.gz))  |


## Installation Instructions (for macOS only)
When installing and launching **_Praditor_** on macOS, you may encounter a security warning due to Apple’s Gatekeeper system, which blocks software from unidentified developers or software that hasn’t been notarized.

### :warning: Common Warning: "Praditor" Can’t Be Opened – Malicious Software
If you see the message:

> [!CAUTION]
> **"Praditor can’t be opened because Apple cannot check it for malicious software."**

follow these steps to bypass this warning safely:

**1. Open System Settings ⚙️** Click the Apple `menu` in the top-left corner of your screen. Select `System Settings` (or `System Preferences` in older macOS versions).

**2. Navigate to Privacy & Security 🛠️** In the sidebar, click `Privacy & Security`.

**3. Locate the Security Section 🛡️** Scroll down to the section labeled `Security or General`.

**4. Allow _Praditor_ to Open 📁** You should see a message stating that 

> “Praditor was blocked from opening because it is not from an identified developer.”

Click the `Open Anyway` button next to this message. A confirmation dialog will appear. Click `Open` to launch the app.

### 🛡️ If the Above Does Not Work: Disable Gatekeeper (Advanced)

If the app still refuses to open, you may need to **temporarily disable Gatekeeper** (the macOS security feature that restricts apps from unidentified developers).

> [!WARNING]  
> Disabling Gatekeeper lowers your system security and should only be done temporarily for trusted software.

1.	Open `Terminal` (Applications > Utilities > Terminal).
2.	Enter the following command to disable Gatekeeper:
```bash
sudo spctl --master-disable
```
3.	Press <kbd>Enter</kbd> and enter your administrator password when prompted.
4.	Try opening _**Praditor**_ again.
5.	After successfully opening the app, it is **highly recommended to re-enable Gatekeeper** to maintain system security:
```bash
sudo spctl --master-enable
```
