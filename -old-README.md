<h1 align="center">🦉 Keylogger Tool V12</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-22223B?style=plastic&logo=python&logoColor=FFD343" height="22">
  <img src="https://img.shields.io/badge/Windows-Full-0078D6?style=plastic&logo=windows&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Linux-Partial-22223B?style=plastic&logo=linux&logoColor=FCC624" height="22">
  <img src="https://img.shields.io/badge/MacOS-Partial-000000?style=plastic&logo=apple&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Stealth-F12_-6e40c9?style=plastic&logo=ghost&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Clipboard-Logger-44C767?style=plastic&logo=clipboard&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Screenshots-Manual /Auto-3B8EEA?style=plastic&logo=image&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Mouse-Clicks/Scrolls-27ae60?style=plastic&logo=mouse&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/AI_Summaries--00B2FF?style=plastic&logo=openai&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Logs-Encrypted-8d71e3?style=plastic&logo=lock&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/GUI-Tkinter+Icons-5E81AC?style=plastic&logo=windowsterminal&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Themes-7%2B_-1eaaae?style=plastic&logo=artstation&logoColor=white" height="22">
  <img src="https://img.shields.io/badge/Offline-100%25-lightgray?style=plastic&logo=cloud&logoColor=gray" height="22">
  <img src="https://visitor-badge.laobi.icu/badge?page_id=shubham-shipt.keylog-v6&left_color=gray&right_color=1eaaae&style=plastic" alt="Repo Visitors" height="22">
</p>

---

<details>
<summary>⚡ <b>Quick Install</b> <i>(click)</i></summary>

```bash
git clone https://github.com/shubham-shipt/keylog-v6.git
cd keylog-v6
```
```
# Install all required libraries
pip install pynput pillow cryptography pygame pyperclip tk
```
```
# (Or, for all dependencies at once)
pip install -r requirements.txt
```
```
# Run the script
python keylogger_v12.py
```
</details>
<details>
<summary>🔎 <b>Info & Usage</b> <i>(click)</i></summary>

- **Category:** <span style="color:#FF5E57"><b>Advanced Monitoring Tool</b></span>
- **WhatsApp/Facebook/Discord/Telegram Chat Logging**
- **Password & Credential Capture** (browsers, terminals, editors, etc.)
- **Clipboard Espionage** (text/images, passwords or secrets)
- **Platforms:** Windows (full), Linux/Mac (partial)
- **No cloud, no email alerts, 100% offline, encrypted logs**

</details>



<details>
<summary>🛡️ <b>How to Decrypt Fernet Encrypted </b> <i>(click)</i></summary>

```python
from cryptography.fernet import Fernet

# Replace with your key and token
key = b'YOUR_KEY_HERE'
token = b'YOUR_ENCRYPTED_STRING_HERE'

fernet = Fernet(key)
decrypted = fernet.decrypt(token)
print(decrypted.decode())
```

**How it works:**  
- Install the cryptography library:  
  `pip install cryptography`
- Paste your key and token into the script above.
- Run the script.  
- **The output will be printed in your terminal as plain text after decryption.**

</details>

<details>
<summary>📝 <b>Example Keylogger Output Summary</b> <i>(click to expand)</i></summary>

```text
───────────── KEYLOGGER SUMMARY ─────────────
Session Start: 2025-07-30 09:12:01
Session End  : 2025-07-30 14:45:17
Total Duration: 5 hours 33 mins

[🟢 WhatsApp]
 - 09:14:20 → 09:16:05
 - Typed: "Hey, are we meeting at 5pm? 👍"
 - Copied: "Location: Cafe Coffee Day"

[🔵 Telegram]
 - 09:20:40 → 09:23:12
 - Typed: "Sending the project files now."
 - Screenshot taken at 09:21:18

[🌐 Chrome]
 - 10:05:10 → 11:27:58
 - Typed: "github copilot documentation"
 - Copied: "https://github.com/features/copilot"
 - Mouse: 14 clicks, 6 scrolls
 - Screenshot taken at 10:10:44

[📝 Notepad]
 - 12:00:33 → 12:25:01
 - Typed: 
    "Todo:
    - Finish report
    - Email John
    - Backup files"
 - Clipboard: "Confidential: Salary.xlsx"

[🗂️ Explorer]
 - 13:55:09 → 14:07:44
 - Actions: 4 files renamed, 2 files deleted
 - Screenshot taken at 14:00:00

───────────── END OF SUMMARY ─────────────
```

</details>

---

## 🧩 Feature Grid

<div align="center" style="font-size:1.1em">

<b>🕵️ Stealth</b> <sub>Instant hide/show (F12)</sub>  
⬇️  
<img src="https://img.icons8.com/fluency/48/clipboard.png" width="32" style="vertical-align:middle;"/> <b>Clipboard</b> <sub>Logs text & images</sub>  
⬇️  
<img src="https://img.icons8.com/fluency/48/screenshot.png" width="32" style="vertical-align:middle;"/> <b>Screenshots</b> <sub>Manual capture</sub>  
⬇️  
<img src="https://img.icons8.com/fluency/48/mouse.png" width="32" style="vertical-align:middle;"/> <b>Mouse</b> <sub>Click & scroll tracking</sub>  
⬇️  
<img src="https://img.icons8.com/fluency/48/lock.png" width="32" style="vertical-align:middle;"/> <b>Encrypted</b> <sub>Fernet encryption</sub>  
⬇️  
<img src="https://img.icons8.com/fluency/48/art-prices.png" width="32" style="vertical-align:middle;"/> <b>Themes</b> <sub>7+ dark/hacker themes</sub>  
⬇️  
<img src="https://img.icons8.com/color/48/artificial-intelligence.png" width="32" style="vertical-align:middle;"/> <b>AI Logs</b> <sub>Smart summaries</sub>  

</div>

---

## 🌌 Visual Gallery

<table align="center">
  <tr>
    <p align="center">
  <img src="Images/7.png" alt="Keylogger Main UI" width="480" style="border-radius:12px;box-shadow:0 4px 24px #0002"/>
</p>
    <td align="center"><img src="Images/2.png" alt="Screenshot 1" width="220"/><br><b> </b></td>
    <td align="center"><img src="Images/3.png" alt="Screenshot 2" width="220"/><br><b>  </b></td>
    <td align="center"><img src="Images/4.png" alt="Screenshot 3" width="220"/><br><b> </b></td>
  </tr>
  <tr>
    <td align="center"><img src="Images/5.png" alt="Screenshot 4" width="220"/><br><b> </b></td>
    <td align="center"><img src="Images/6.png" alt="Screenshot 5" width="220"/><br><b> </b></td>
    <td align="center"><img src="Images/1.png" alt="Screenshot 6" width="220"/><br><b></b></td>
  </tr>
</table>

---

## 📦 Tech Stack

<div align="center">
  
  <img src="https://img.icons8.com/color/48/python.png" width="36" alt="Python"/>
  <img src="https://img.icons8.com/fluency/48/code.png" width="36" alt="Code"/>
  <img src="https://img.icons8.com/color/48/windows-10.png" width="36" alt="Windows"/>
  <img src="https://img.icons8.com/color/48/linux.png" width="36" alt="Linux"/>
  <img src="https://img.icons8.com/color/48/mac-logo.png" width="36" alt="Mac"/>
</div>

**Core Language:**  
&nbsp;&nbsp;• Python 3.8+  

**Key Libraries:**  
- `pynput` <sub><i>(Keyboard/Mouse listening)</i></sub>
- `pillow` <sub><i>(Screenshots, image handling)</i></sub>
- `cryptography` <sub><i>(Fernet log encryption)</i></sub>
- `pygame` <sub><i>(Audio/notification features)</i></sub>
- `pyperclip` <sub><i>(Clipboard access)</i></sub>
- `tkinter` <sub><i>(Modern GUI frontend)</i></sub>

**Cross-Platform:**  
- 🟦 Windows <b>(full support)</b>  
- 🐧 Linux / 🍏 Mac <b>(partial support)</b>

---
> 🟢 **Manual Run:** Open the script, understand the code, and execute it as per your custom needs.

---

> ⚠️ **Legal Notice:**  
> This tool is for **educational purposes** only. Unauthorized use may be illegal or unethical.

---

<p align="center">
  <a href="https://github.com/shubham-shipt/keylog-v6">
    <img src="https://img.shields.io/badge/GitHub-View%20Source-181717?style=plastic&logo=github&logoColor=white" alt="View Source on GitHub" height="26">
  </a>
</p>
