@echo off
title Building EAIT-Tool

echo Entferne alte Build-Ordner ...
rmdir /s /q build
rmdir /s /q dist

echo Starte PyInstaller-Build ...

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --icon "data\icon.ico" ^
  --add-data "data;data" ^
  EAIT-Tool_SAFE.py

echo.
echo [✓] Build finished!
pause
