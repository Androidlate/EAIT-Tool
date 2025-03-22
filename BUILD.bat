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
  --add-data "data\icon.ico;data" ^
  --add-data "data\ProtonVPN.zip;data" ^
  --add-data "data\jetbrains_toolbox.zip;data" ^
  --add-data "data\brave.zip;data" ^
  --add-data "data\brave_32x32.png;data" ^
  --add-data "data\adobe_normal.cur;data" ^
  --add-data "data\adobe_click.cur;data" ^
  --add-data "data\ublock.xpi;data" ^
  EAIT-Tool.py

echo.
echo [✓] Build finished!
pause
