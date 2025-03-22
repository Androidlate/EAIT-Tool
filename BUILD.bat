@echo off
title Building EAIT-Tool

echo Entferne alte Build-Ordner ...
rmdir /s /q build
rmdir /s /q dist

echo Starte PyInstaller-Build ...
pyinstaller ^
  --onefile ^
  --noconsole ^
  --icon "data\icon.ico" ^
  --add-data "data;data" ^
  EAIT-Tool.py

echo.
echo [✓] Build finished!
pause
