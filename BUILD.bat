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
  --add-data "data\icon.ico;." ^
  --add-data "data\ProtonVPN.zip;." ^
  --add-data "data\jetbrains_toolbox.zip;." ^
  --add-data "data\brave.zip;." ^
  --add-data "data\brave_32x32.png;." ^
  --add-data "data\adobe_normal.cur;." ^
  --add-data "data\adobe_click.cur;." ^
  --add-data "data\ublock.xpi;." ^
  EAIT-Tool.py

echo.
echo [✓] Build finished!
pause
