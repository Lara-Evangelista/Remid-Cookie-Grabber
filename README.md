# Remid Cookie Grabber
 
Automatically logs into your EA account and grabs your remid cookie.
 
---
 
## Using the Release
 
1. Download `Sims4RemidGrabber.exe` from the [Releases](../../releases) page
2. Double-click it to run, no installation needed
3. Enter your EA email and password
4. Click **Grab Remid Cookie**
5. A Chromium browser window will open and log in automatically
6. Once done, the remid value is **copied to your clipboard** and saved to "remid.txt" in the same directory as the ".exe"
7. (If using it to access online functionality in The Sims 4) Paste it into the Sims 4 popup when prompted
> The first launch may take a few seconds, this is normal.
> 
---
 
## Are my credentials safe?
 
Yes. Your email and password are **encrypted** using AES (Fernet) before being saved locally. They are stored at:
 
```
C:\Users\<you>\.remid_config.json
```
 
The encryption key is stored separately at:
 
```
C:\Users\<you>\.remid_key
```
 
**Neither file is included in the ".exe" or shared with anyone.** They live only on your machine. You can delete both at any time using the **Clear Saved** button in the app.
 
---
 
## Running the Code Directly 
 
### Requirements
 
- Python 3.10+
- Install dependencies:
```bash
pip install playwright cryptography pyperclip
playwright install chromium
```
 
### Run
 
```bash
python Remid_Cookie_Grabber_v1.0.0.py
```

---
 
## Troubleshooting
 
**The browser window opens but gets stuck**
> EA may have added a CAPTCHA or 2FA step. Complete it manually in the browser window and it will continue automatically.
 
**"Remid" not found**
> Make sure you're logging in with the correct email and password, and that your account doesn't have extra verification steps blocking it.
 
**Program won't open / crashes immediately**
> Make sure you're on Windows 10 or 11. The ".exe" is not compatible with older versions.
 
**Want to clear your saved credentials?**
> Click the **Clear Saved** button in the app, or manually delete `~/.remid_config.json` and `~/.remid_key`.
