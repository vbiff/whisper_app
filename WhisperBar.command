#!/bin/bash
# Double-click to launch WhisperBar in background (no terminal window needed)
cd "$(dirname "$0")"
nohup python3 whisper_menubar.py > /tmp/whisperbar.log 2>&1 &
echo "WhisperBar started (PID $!)"
sleep 1
# Close this terminal window
osascript -e 'tell application "Terminal" to close first window' &
