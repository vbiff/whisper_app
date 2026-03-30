#!/usr/bin/env python3
"""
Whisper Hotkey — локальная транскрипция голоса по хоткею.
Держи F5 → говори → отпусти → текст вставится в активное окно.

Установка зависимостей:
  pip3 install openai-whisper sounddevice scipy pynput

Запуск:
  python3 whisper_hotkey.py

Автозапуск (опционально):
  добавь в ~/.zshrc:
  alias wh='python3 ~/path/to/whisper_hotkey.py &'
"""

import sounddevice as sd
import scipy.io.wavfile as wav
import whisper
import tempfile
import subprocess
import numpy as np
import sys
from pynput import keyboard

SAMPLE_RATE = 16000
HOTKEY = keyboard.Key.f5   # Измени на нужный
LANGUAGE = "ru"             # "ru" / "en" / None (автодетект)
MODEL_SIZE = "base"         # tiny / base / small / medium / large

recording = []
is_recording = False

print(f"⚡ Loading Whisper model '{MODEL_SIZE}'...")
model = whisper.load_model(MODEL_SIZE)
print(f"✅ Ready! Hold {HOTKEY} to record, release to transcribe.")
print("   Ctrl+C to quit.\n")


def on_press(key):
    global is_recording, recording
    if key == HOTKEY and not is_recording:
        is_recording = True
        recording = []
        print("🎙  Recording...", end="", flush=True)


def on_release(key):
    global is_recording
    if key == HOTKEY and is_recording:
        is_recording = False
        transcribe()
    elif key == keyboard.Key.esc:
        print("\n👋 Bye!")
        sys.exit(0)


def audio_callback(indata, frames, time, status):
    if is_recording:
        recording.append(indata.copy())


def transcribe():
    if not recording:
        print(" (no audio captured — check microphone permissions)")
        return

    audio = np.concatenate(recording, axis=0).flatten()
    duration = len(audio) / SAMPLE_RATE
    print(f" ({duration:.1f}s captured)", end="", flush=True)

    if duration < 0.3:
        print(" (too short, skipped)")
        return

    if np.max(np.abs(audio)) < 0.001:
        print(" (silence — check microphone permissions in System Settings)")
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
        wav.write(f.name, SAMPLE_RATE, audio)
        result = model.transcribe(f.name, language=LANGUAGE)
        text = result["text"].strip()

    print(f"\n📝 {text}\n")

    # Копируем в буфер и вставляем Cmd+V в активное окно
    subprocess.run(["pbcopy"], input=text.encode())
    subprocess.run([
        "osascript", "-e",
        'tell application "System Events" to keystroke "v" using command down'
    ])


# Запуск
try:
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback):
        with keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
            listener.join()
except KeyboardInterrupt:
    print("\n👋 Bye!")
