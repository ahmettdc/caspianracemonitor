[Setup]
AppName=Caspian Race Monitor
AppVersion=0.0.1
DefaultDirName={autopf}\CaspianRaceMonitor-v0.0.1
DefaultGroupName=CaspianRaceMonitor
OutputDir=dist-installer
OutputBaseFilename=crm-setup
SetupIconFile=crm_icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\crm-v0.0.1\crm-v0.0.1.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\crm-v0.0.1\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\CaspianRaceMonitor"; Filename: "{app}\crm-v0.0.1.exe"
Name: "{commondesktop}\CaspianRaceMonitor"; Filename: "{app}\crm-v0.0.1.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Masaüstü simgesi oluştur"; GroupDescription: "Ek görevler:"
