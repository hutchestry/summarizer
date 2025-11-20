#!/bin/bash

set -e

echo "🔍 Detecting Python path..."
PYTHON_PATH=$(which python3)
echo "   → Using: $PYTHON_PATH"

echo "🔍 Detecting 'summarizer' entry point..."
SUMMARIZER_PATH=$(which summarizer)

if [ -z "$SUMMARIZER_PATH" ]; then
    echo "❌ Could not find 'summarizer' on PATH."
    echo "Make sure you installed the package: pip install -e ."
    exit 1
fi

echo "   → Found summarizer at: $SUMMARIZER_PATH"

PLIST_PATH=~/Library/LaunchAgents/com.summarizer.agent.plist

echo "📝 Generating LaunchAgent plist at:"
echo "   $PLIST_PATH"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.summarizer.agent</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SUMMARIZER_PATH</string>
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
EOF

echo "✅ LaunchAgent plist created."

echo "🔄 Reloading LaunchAgent..."
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "✅ Summarizer is now scheduled to run daily at 3AM."
echo "✅ You can check logs:"
echo "   tail -f /tmp/summarizer.out"
echo "   tail -f /tmp/summarizer.err"

echo "✅ To run Summarizer ad-hoc:"
echo "   summarizer"
