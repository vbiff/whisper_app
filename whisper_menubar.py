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
MODEL_SIZE = "small"

recording = []
is_recording = False
model = None


def load_model():
    global model
    model = whisper.load_model(MODEL_SIZE)


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
            rumps.MenuItem("Hold Ctrl+Shift+R to record", callback=None),
            None,  # separator
        ]

    def start_recording(self):
        global is_recording, recording
        is_recording = True
        recording = []
        self.title = "🔴"
        if self.stream is None or not self.stream.active:
            self.stream = sd.InputStream(
                samplerate=SAMPLE_RATE, channels=1, callback=audio_callback
            )
            self.stream.start()

    def stop_recording(self):
        global is_recording
        is_recording = False
        self.title = "⏳"
        threading.Thread(target=self._do_transcribe, daemon=True).start()

    def _do_transcribe(self):
        transcribe()
        self.title = "🎤"


def run():
    # Load model in background
    threading.Thread(target=load_model, daemon=True).start()

    app = WhisperApp()

    # Global hotkey: hold Ctrl+Shift+R to record, release to transcribe
    from pynput import keyboard

    pressed = set()
    COMBO = {keyboard.Key.ctrl, keyboard.Key.shift, keyboard.KeyCode.from_char('r')}

    def on_press(key):
        # Normalize ctrl_l/ctrl_r → ctrl
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            key = keyboard.Key.ctrl
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            key = keyboard.Key.shift
        pressed.add(key)
        if pressed >= COMBO and not is_recording:
            app.start_recording()

    def on_release(key):
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            key = keyboard.Key.ctrl
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            key = keyboard.Key.shift
        pressed.discard(key)
        if is_recording:
            app.stop_recording()

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release,
        suppress=False
    )
    listener.start()

    app.run()


if __name__ == "__main__":
    run()
