@echo off
set /p ver="Yeni versiyonu girin (örn: 0.0.3): "

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

pyinstaller --noconsole ^
 --name crm-v%ver% ^
 --icon=crm_icon.ico ^
 --add-data "ui;ui" ^
 --add-data "assets;assets" ^
 --add-data "data;data" ^
 main.py

echo.
echo ✅ EXE üretimi tamamlandı: dist\crm-v%ver%\crm-v%ver%.exe
pause
