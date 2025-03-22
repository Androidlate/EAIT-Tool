@echo off
title EAIT-Tool Build
echo Building EAIT-Tool .exe...

REM Clean old build/dist folders
rmdir /s /q build
rmdir /s /q dist

REM Build EXE mit allen Ressourcen aus dem "data" Ordner
pyinstaller --onefile --noconsole --icon "data\icon.ico" ^
--add-data "data\icon.ico;data" ^
--add-data "data\ProtonVPN.zip;data" ^
--add-data "data\jetbrains_toolbox.zip;data" ^
--add-data "data\ublock.xpi;data" ^
--add-data "data\brave.zip;data" ^
--add-data "data\brave_32x32.png;data" ^
--add-data "data\adobe_normal.cur;data" ^
--add-data "data\adobe_click.cur;data" ^
EAIT-Tool.py

echo.
echo ✅ Build finished!
pause
