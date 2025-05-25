#!/bin/bash

pyinstaller --clean --windowed --onefile --icon ico/heartonfireopenmoji.png --upx-dir=upx/upx-5.0.0-amd64_linux/ gui_qt6.py



# Windows build
# pyinstaller --clean --windowed --onefile --icon ico/heartonfireopenmoji.png --upx-dir=upx/upx-5.0.1-win64/ gui_qt6.py
