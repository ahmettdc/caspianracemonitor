[Setup]
AppName=Caspian Race Monitor
AppVersion=0.0.2
DefaultDirName={pf}\CaspianRaceMonitor-v0.0.2
DefaultGroupName=CaspianRaceMonitor
OutputDir=installer_scripts\dist-installer
OutputBaseFilename=crm-setup-v0.0.2
SetupIconFile=installer_scripts\crm_icon.ico
Compression=lzma
SolidCompression=yes
[Files]
Source: "dist\crm-v0.0.2\crm-v0.0.2.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\CaspianRaceMonitor"; Filename: "{app}\crm-v0.0.2.exe"
Name: "{commondesktop}\CaspianRaceMonitor"; Filename: "{app}\crm-v0.0.2.exe"
[Tasks]
Name: "desktopicon"; Description: "Masaüstü simgesi oluştur"; GroupDescription: "Ek görevler:"
