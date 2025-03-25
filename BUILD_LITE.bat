@echo off
title Building EAIT-Tool Lite

echo Entferne alte BUILD-Ordner ...
rmdir /s /q build
del EAIT-Tool.spec >nul 2>&1

echo Starte PyInstaller-Build ...

pyinstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --icon="%cd%\data\icon.ico" ^
  --add-data "data\\casino_logo.gif;data" ^
  --add-data "data\\casino_background.png;data" ^
  --add-data "data\\adobe_normal.cur;data" ^
  --add-data "data\\adobe_click.cur;data" ^
  --add-data "data\\7z.exe;data" ^
  EAIT-Tool_LITE.py

echo.
echo [✓] Build finished!
pause
