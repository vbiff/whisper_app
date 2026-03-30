# WhisperBar 🎤

Local voice-to-text that lives in your macOS menubar. No API key, no cloud, completely free.

Hold **Ctrl+Shift+R** → speak → release → text is pasted wherever your cursor is.

---

## Quick Install

### Step 1 — Install ffmpeg

```bash
brew install ffmpeg
```

> Don't have Homebrew? Install it first: https://brew.sh

### Step 2 — Clone the repo

```bash
git clone https://github.com/vbiff/whisper_app.git
cd whisper_app
```

### Step 3 — Install Python dependencies

```bash
pip3 install -r requirements.txt
```

> First run will download the Whisper model (~145MB). This takes a minute.

### Step 4 — Run

Double-click **`WhisperBar.command`** in Finder.

Or from terminal:
```bash
python3 whisper_menubar.py
```

A 🎤 icon will appear in your menubar (top-right corner).

---

## Usage

| Action | Result |
|--------|--------|
| Hold **Ctrl+Shift+R** | 🔴 starts recording |
| Release **Ctrl+Shift+R** | ⏳ transcribes → pastes text |
| Click 🎤 → Quit | stops the app |

Works in any app — terminal, browser, text editor, Slack, etc.

**Language:** auto-detected (Russian, English, or any language).

---

## Auto-start on Login

Run once to make WhisperBar launch automatically when you log in:

```bash
bash install_autostart.sh
```

That's it. WhisperBar will start silently in the background every time you turn on your Mac.

To disable:
```bash
launchctl unload ~/Library/LaunchAgents/com.whisperbar.launch.plist
```

---

## Permissions

On first run, macOS may ask for two permissions:

- **Microphone** — needed to record your voice
- **Accessibility** — needed to paste text (Cmd+V simulation)

Go to: **System Settings → Privacy & Security** and enable both for Terminal (or your Python).

---

## Model sizes

Edit `MODEL_SIZE` in `whisper_menubar.py` to trade speed for accuracy:

| Model  | Size   | Speed  | Accuracy |
|--------|--------|--------|----------|
| `tiny` | ~75MB  | fast   | ok       |
| `base` | ~145MB | fast   | good ✅  |
| `small`| ~465MB | medium | better   |
| `medium`| ~1.5GB| slow  | great    |
| `large`| ~3GB   | slow   | best     |

Default is `base` — good enough for most use cases.

---

## Requirements

- macOS
- Python 3.8+
- ffmpeg (`brew install ffmpeg`)

---

## License

MIT
