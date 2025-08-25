@echo off
set /p version="Yeni sürüm numarasını girin (örn: 0.0.3): "

:: .iss dosyasını installer_scripts klasörüne oluştur
set "ISS_PATH=installer_scripts\crm-setup-v%version%.iss"

(
echo [Setup]
echo AppName=Caspian Race Monitor
echo AppVersion=%version%
echo AppId={{C9F7B0C2-5E62-4D15-9BBA-CRM-%version%}}
echo DefaultDirName={pf}\CaspianRaceMonitor-v%version%
echo DefaultGroupName=CaspianRaceMonitor
echo OutputDir=installer_scripts\dist-installer
echo OutputBaseFilename=crm-setup-v%version%
echo SetupIconFile=installer_scripts\crm_icon.ico
echo Compression=lzma
echo SolidCompression=yes

echo [Files]
echo Source: "..\dist\crm-v%version%\crm-v%version%.exe"; DestDir: "{app}"; Flags: ignoreversion

echo [Icons]
echo Name: "{group}\CaspianRaceMonitor"; Filename: "{app}\crm-v%version%.exe"
echo Name: "{commondesktop}\CaspianRaceMonitor"; Filename: "{app}\crm-v%version%.exe"; Tasks: desktopicon

echo [Tasks]
echo Name: "desktopicon"; Description: "Masaüstü simgesi oluştur"; GroupDescription: "Ek görevler:"
) > "%ISS_PATH%"

echo.
echo ✅ ISS dosyası oluşturuldu: %ISS_PATH%

:: ISCC.exe ile derleme başlat
set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "%ISCC_PATH%" (
    echo ⏳ Inno Setup derlemesi başlatılıyor...
    "%ISCC_PATH%" "%ISS_PATH%"
    echo ✅ Installer başarıyla oluşturuldu!
) else (
    echo ❌ HATA: ISCC.exe bulunamadı!
    echo Kontrol et: "%ISCC_PATH%"
)

pause
