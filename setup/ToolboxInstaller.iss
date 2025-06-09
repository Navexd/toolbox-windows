; Script Inno Setup pour Toolbox
[Setup]
AppName=Toolbox
AppVersion=0.8
DefaultDirName={pf}\Toolbox
DefaultGroupName=Toolbox
OutputBaseFilename=ToolboxInstaller
Compression=lzma
SolidCompression=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
Source: "\toolbox\toolbox\dist\Toolbox\Toolbox.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "\toolbox\toolbox\dist\Toolbox\_internal\styles.qss"; DestDir: "{app}"; Flags: ignoreversion
Source: "\toolbox\toolbox\dist\Toolbox\_internal\pick\*"; DestDir: "{app}\pick"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "\toolbox\toolbox\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{group}\Toolbox"; Filename: "{app}\Toolbox.exe"
Name: "{group}\{cm:UninstallProgram,Toolbox}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Toolbox.exe"; Description: "{cm:LaunchProgram,Toolbox}"; Flags: nowait postinstall skipifsilent
