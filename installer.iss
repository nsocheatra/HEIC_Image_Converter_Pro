; HEIC Image Converter Pro Installer
; Requires Inno Setup 6+ (https://jrsoftware.org/isdl.php)

#define AppName "HEIC Image Converter Pro"
#define AppVersion "1.0.0"
#define AppExe "HEIC_Image_Converter_Pro.exe"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=HEIC_Image_Converter_Pro_Setup
SetupIconFile=assets\logo.ico
WizardStyle=modern
PrivilegesRequired=admin

[Files]
Source: "dist\{#AppExe}"; DestDir: "{app}"

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: postinstall nowait skipifsilent
