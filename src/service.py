import os
import subprocess
from pathlib import Path
import shutil
import sys


PLIST_PATH = Path.home() / "Library/LaunchAgents/com.summarizer.agent.plist"


def detect_python():
    """Return the path of the active Python interpreter."""
    return sys.executable


def detect_summarizer_entrypoint():
    """Return path to the installed summarizer CLI script."""
    from shutil import which
    exe = which("summarizer")
    if not exe:
        raise RuntimeError("Could not find 'summarizer' on PATH.")
    return exe


def generate_plist(python_path, summarizer_path):
    """Return plist XML as a string."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.summarizer.agent</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{summarizer_path}</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>3</integer>
        <key>Minute</key><integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/summarizer.out</string>

    <key>StandardErrorPath</key>
    <string>/tmp/summarizer.err</string>

    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""


def service_install():
    """Install and load LaunchAgent."""
    python_path = detect_python()
    summarizer_path = detect_summarizer_entrypoint()

    print(f"🔍 Using python: {python_path}")
    print(f"🔍 Using summarizer: {summarizer_path}")
    print(f"📝 Writing plist: {PLIST_PATH}")

    plist_content = generate_plist(python_path, summarizer_path)
    PLIST_PATH.write_text(plist_content)

    print("🔄 Reloading LaunchAgent...")
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["launchctl", "load", str(PLIST_PATH)])

    print("✅ Summarizer scheduled daily at 3AM.")
    print("✅ Logs: /tmp/summarizer.out /tmp/summarizer.err")


def service_remove():
    """Unload and remove LaunchAgent."""
    print(f"🗑 Removing LaunchAgent: {PLIST_PATH}")

    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()

    print("✅ Summarizer LaunchAgent removed.")
    print("✅ Automation disabled.")
