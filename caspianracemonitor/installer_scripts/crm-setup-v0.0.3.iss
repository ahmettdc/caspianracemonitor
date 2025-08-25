[Setup]
AppName=Caspian Race Monitor
AppVersion=0.0.3
AppId={{C9F7B0C2-5E62-4D15-9BBA-CRM-0.0.3}}
DefaultDirName={commonpf}\CaspianRaceMonitor-v0.0.3
DefaultGroupName=CaspianRaceMonitor
OutputDir=dist-installer
OutputBaseFilename=crm-setup-v0.0.3
SetupIconFile=crm_icon.ico
Compression=lzma
SolidCompression=yes
[Files]
Source: "..\dist\crm-v0.0.3\crm-v0.0.3.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\CaspianRaceMonitor"; Filename: "{app}\crm-v0.0.3.exe"
Name: "{commondesktop}\CaspianRaceMonitor"; Filename: "{app}\crm-v0.0.3.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Masaüstü simgesi oluştur"; GroupDescription: "Ek görevler:"
