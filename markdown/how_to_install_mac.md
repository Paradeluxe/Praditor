
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
