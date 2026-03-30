"""
Сборка в .app:
  pip3 install py2app
  python3 setup_app.py py2app
"""
from setuptools import setup

APP = ['whisper_menubar.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'LSUIElement': True,  # нет иконки в доке
        'CFBundleName': 'WhisperBar',
        'CFBundleDisplayName': 'WhisperBar',
        'NSMicrophoneUsageDescription': 'WhisperBar needs microphone for voice transcription.',
        'NSAccessibilityUsageDescription': 'WhisperBar needs accessibility to paste text.',
    },
    'packages': ['whisper', 'rumps', 'sounddevice', 'pynput'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
