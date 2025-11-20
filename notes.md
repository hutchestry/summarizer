# Notes

# ✅ **Ad-hoc Run Command**

After installation:

`summarizer`

This triggers the full daily+weekly generation immediately.

You can also call the Python module directly:

`python3 -m summarizer.main`

---

# ✅ **summarizer-uninstall.sh (Uninstaller)**

Save this as `summarizer-uninstall.sh`:

`#!/bin/bash  set -e  PLIST_PATH=~/Library/LaunchAgents/com.summarizer.agent.plist  echo "🗑 Removing LaunchAgent..."  launchctl unload "$PLIST_PATH" 2>/dev/null || true  rm -f "$PLIST_PATH"  echo "✅ Summarizer LaunchAgent removed." echo "✅ Daily automation is now disabled."`

---

# ✅ Usage

### Install:

`chmod +x summarizer-install.sh ./summarizer-install.sh`

### Uninstall:

`chmod +x summarizer-uninstall.sh ./summarizer-uninstall.sh`

Below is a **self-contained CLI extension** for your Python package that provides:

✅ `summarizer service install`  
✅ `summarizer service remove`  
✅ Auto-detects Python & executable path  
✅ Manages LaunchAgent plist cleanly  
✅ Fully embedded inside your Python package

This turns your Summarizer into a real macOS-native service manager.

---

# ✅ Add this file: `summarizer/service.py`

### ✅ Run Summarizer ad-hoc:

`summarizer run`

—or simply—

`summarizer`

### ✅ Install the daily 3AM service:

`summarizer service-install`

### ✅ Remove the LaunchAgent:

`summarizer service-remove`