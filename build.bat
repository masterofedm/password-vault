@echo off

echo Cleaning old build...

rmdir /s /q build
rmdir /s /q dist
del main.spec

echo Building executable...

pyinstaller --onefile --windowed --icon=vault_icon.ico --clean main.py

echo Build complete!

pause