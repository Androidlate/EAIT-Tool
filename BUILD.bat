@echo off
title Building EAIT-Tool

echo Entferne alte BUILD-Ordner ...
rmdir /s /q build

echo Starte PyInstaller-Build ...

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --icon "data\icon.ico" ^
  --add-data "data;data" ^
  EAIT-Tool.py

echo.
echo [✓] Build finished!
pause
