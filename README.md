# whisper-hotkey

Local voice-to-text using [OpenAI Whisper](https://github.com/openai/whisper) — no API key, no cloud, completely free.

Hold a hotkey → speak → release → text is pasted wherever your cursor is.

---

## Requirements

- macOS (uses `pbcopy` + `osascript` for paste)
- Python 3.8+
- [ffmpeg](https://ffmpeg.org/)

## Installation

**1. Install ffmpeg**
```bash
brew install ffmpeg
```

**2. Clone the repo**
```bash
git clone https://github.com/mokyio8/whisper-hotkey.git
cd whisper-hotkey
```

**3. Install Python dependencies**
```bash
pip3 install -r requirements.txt
```

> First run will download the Whisper model (~145MB for `base`).

## Usage

```bash
python3 whisper_hotkey.py
```

- **Hold F5** → speak → **release** → text is pasted into the active window
- **Esc** → quit

Works in terminal, browser, any text field.

## Configuration

Edit the top of `whisper_hotkey.py`:

```python
HOTKEY = keyboard.Key.f5   # change to any key
LANGUAGE = "ru"             # "ru" / "en" / None (auto-detect)
MODEL_SIZE = "base"         # tiny (fast) / base / small / medium / large
```

## Model sizes

| Model  | Size   | Speed  | Accuracy |
|--------|--------|--------|----------|
| tiny   | ~75MB  | fast   | ok       |
| base   | ~145MB | fast   | good     |
| small  | ~465MB | medium | better   |
| medium | ~1.5GB | slow   | great    |
| large  | ~3GB   | slow   | best     |

For everyday use, `base` or `small` is recommended.

## Permissions

On first run, macOS will ask for **Accessibility** permission (needed to simulate Cmd+V).

Go to: **System Settings → Privacy & Security → Accessibility** → enable Terminal (or your Python).

## Auto-start on login

Run once to make WhisperBar launch automatically at startup:

```bash
PLIST="$HOME/Library/LaunchAgents/com.whisperbar.launch.plist"
cat > "$PLIST" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.whisperbar.launch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/YOUR_USERNAME/Desktop/whisper_app/whisper_app/WhisperBar.command</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF
launchctl load "$PLIST"
```

> Replace `YOUR_USERNAME` with your macOS username (run `whoami` to check).

To disable autostart:
```bash
launchctl unload ~/Library/LaunchAgents/com.whisperbar.launch.plist
```

## License

MIT
