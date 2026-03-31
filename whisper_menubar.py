#!/usr/bin/env python3
"""
Whisper Menubar — живёт в трее, глобальный хоткей F5.
Запуск: python3 whisper_menubar.py
Сборка в .app: pip3 install py2app && python3 setup_app.py py2app
"""

import rumps
import sounddevice as sd
import scipy.io.wavfile as wav
import whisper
import tempfile
import subprocess
import numpy as np
import threading

SAMPLE_RATE = 16000
LANGUAGE = None  # None = auto-detect (Russian, English, any language)
MODEL_SIZE = "medium"

recording = []
is_recording = False
model = None
_app_ref = None


def load_model():
    global model
    # Show loading indicator in menubar
    if _app_ref:
        _app_ref.title = "⬇️"
    model = whisper.load_model(MODEL_SIZE)
    if _app_ref:
        _app_ref.title = "🎤"


def transcribe():
    global recording
    if not recording:
        return

    audio = np.concatenate(recording, axis=0).flatten()
    if len(audio) / SAMPLE_RATE < 0.3:
        return
    if np.max(np.abs(audio)) < 0.001:
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
        wav.write(f.name, SAMPLE_RATE, audio)
        result = model.transcribe(f.name, language=LANGUAGE)
        text = result["text"].strip()

    if text:
        subprocess.run(["pbcopy"], input=text.encode())
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to keystroke "v" using command down'
        ])


def audio_callback(indata, frames, time, status):
    if is_recording:
        recording.append(indata.copy())


class WhisperApp(rumps.App):
    def __init__(self):
        super().__init__("🎤", quit_button="Quit")
        self.stream = None
        self.menu = [
            rumps.MenuItem("Hold Shift+Option to record", callback=None),
            None,  # separator
        ]

    def start_recording(self):
        global is_recording, recording
        if model is None:
            return  # model still loading, ignore
        # Close previous stream if exists
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        is_recording = True
        recording = []
        self.title = "🔴"
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, callback=audio_callback
        )
        self.stream.start()
        # Watchdog: auto-stop if recording hangs (e.g. key-up event was lost)
        self._watchdog = threading.Timer(30.0, self._watchdog_stop)
        self._watchdog.start()

    def _watchdog_stop(self):
        if is_recording:
            self.stop_recording()

    def stop_recording(self):
        global is_recording
        # Cancel watchdog if it's still running
        if hasattr(self, '_watchdog') and self._watchdog is not None:
            self._watchdog.cancel()
            self._watchdog = None
        is_recording = False
        # Stop stream immediately to free resources
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        self.title = "⏳"
        threading.Thread(target=self._do_transcribe, daemon=True).start()

    def _do_transcribe(self):
        transcribe()
        self.title = "🎤"


def run():
    global _app_ref
    app = WhisperApp()
    _app_ref = app

    # Load model in background (shows ⬇️ while downloading)
    threading.Thread(target=load_model, daemon=True).start()

    # Global hotkey: hold Ctrl+Shift+R to record, release to transcribe
    from pynput import keyboard

    pressed = set()
    COMBO = {keyboard.Key.shift, keyboard.Key.alt}

    def on_press(key):
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            key = keyboard.Key.shift
        if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
            key = keyboard.Key.alt
        pressed.add(key)
        if pressed >= COMBO and not is_recording:
            app.start_recording()

    def on_release(key):
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            key = keyboard.Key.shift
        if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
            key = keyboard.Key.alt
        pressed.discard(key)
        # Stop only on first key release (when combo breaks)
        if is_recording and not (pressed >= COMBO):
            app.stop_recording()

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release,
        suppress=False,
        on_activate=lambda: pressed.clear(),  # reset state on focus change
    )
    listener.start()

    app.run()


if __name__ == "__main__":
    run()
