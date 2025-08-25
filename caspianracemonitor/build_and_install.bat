@echo off
set /p ver="Yeni versiyonu girin (örn: 0.0.3): "

:: Temizlik
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

:: 1. EXE oluştur
echo 🔧 EXE derleniyor...
pyinstaller --noconsole ^
 --name crm-v%ver% ^
 --icon=crm_icon.ico ^
 --add-data "ui;ui" ^
 --add-data "assets;assets" ^
 --add-data "data;data" ^
 main.py

:: EXE üretildi mi kontrol et
if not exist "dist\crm-v%ver%\crm-v%ver%.exe" (
    echo ❌ HATA: EXE dosyası oluşmadı!
    pause
    exit /b
)

:: 2. ISS dosyası oluştur
echo 🔨 ISS oluşturuluyor...
set "ISS_PATH=installer_scripts\crm-setup-v%ver%.iss"

(
echo [Setup]
echo AppName=Caspian Race Monitor
echo AppVersion=%ver%
echo AppId={{C9F7B0C2-5E62-4D15-9BBA-CRM-%ver%}}
echo DefaultDirName={commonpf}\CaspianRaceMonitor-v%ver%
echo DefaultGroupName=CaspianRaceMonitor
echo OutputDir=dist-installer
echo OutputBaseFilename=crm-setup-v%ver%
echo SetupIconFile=crm_icon.ico
echo Compression=lzma
echo SolidCompression=yes

echo [Files]
echo Source: "..\dist\crm-v%ver%\crm-v%ver%.exe"; DestDir: "{app}"; Flags: ignoreversion

echo [Icons]
echo Name: "{group}\CaspianRaceMonitor"; Filename: "{app}\crm-v%ver%.exe"
echo Name: "{commondesktop}\CaspianRaceMonitor"; Filename: "{app}\crm-v%ver%.exe"; Tasks: desktopicon

echo [Tasks]
echo Name: "desktopicon"; Description: "Masaüstü simgesi oluştur"; GroupDescription: "Ek görevler:"
) > "%ISS_PATH%"

:: 3. ISCC derleme
echo 📦 Installer derleniyor...
set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "%ISCC_PATH%" (
    "%ISCC_PATH%" "%ISS_PATH%"
    echo ✅ Tamamlandı: dist-installer\crm-setup-v%ver%.exe
) else (
    echo ❌ HATA: ISCC.exe bulunamadı!
)

pause
