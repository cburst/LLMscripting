!include "MUI2.nsh"
!include "FileFunc.nsh"

Name "LLM Scripting"
OutFile "LLMscripting-Installer.exe"
InstallDir "C:\LLMscripting-main"
InstallDirRegKey HKLM "Software\LLMscripting" "InstallDir"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show
BrandingText "LLM Scripting Installer"

!define MUI_ABORTWARNING
!define MUI_ICON "app\data\icon.ico"
!define MUI_UNICON "app\data\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Var StartMenuFolder

Section "Install" SEC01
    SetShellVarContext all
    SetOutPath "$INSTDIR"

    DetailPrint "Preparing installer files..."
    File "LLMscripting.ps1"

    DetailPrint "Running PowerShell installer..."
    DetailPrint "This may take several minutes."

    nsExec::ExecToLog '"$WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\LLMscripting.ps1"'
    Pop $0

    ${If} $0 != 0
        MessageBox MB_ICONSTOP "LLM Scripting installation failed. PowerShell exit code: $0"
        Abort
    ${EndIf}

    DetailPrint "Writing uninstaller..."
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Registry: install location
    WriteRegStr HKLM "Software\LLMscripting" "InstallDir" "$INSTDIR"

    ; Registry: Add/Remove Programs entry
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting" "DisplayName" "LLM Scripting"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting" "DisplayIcon" "$INSTDIR\app\data\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting" "Publisher" "Richard Rose"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting" "NoRepair" 1

    ; Start Menu folder
    StrCpy $StartMenuFolder "$SMPROGRAMS\LLM Scripting"
    CreateDirectory "$StartMenuFolder"

    ; Main shortcut (GUI launcher created by your PS script)
    ${If} ${FileExists} "$INSTDIR\Grammar Pipeline.lnk"
        CreateShortCut "$StartMenuFolder\Grammar Pipeline.lnk" "$INSTDIR\Grammar Pipeline.lnk"
    ${Else}
        CreateShortCut "$StartMenuFolder\Grammar Pipeline.lnk" "$INSTDIR\run_gui.py" "" "$INSTDIR\app\data\icon.ico"
    ${EndIf}

    CreateShortCut "$StartMenuFolder\Uninstall LLM Scripting.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\app\data\icon.ico"

    DetailPrint "Installation completed successfully."
SectionEnd

Section "Uninstall"
    SetShellVarContext all

    DetailPrint "Removing shortcuts..."
    Delete "$DESKTOP\Grammar Pipeline.lnk"
    Delete "$SMPROGRAMS\LLM Scripting\Grammar Pipeline.lnk"
    Delete "$SMPROGRAMS\LLM Scripting\Uninstall LLM Scripting.lnk"
    RMDir "$SMPROGRAMS\LLM Scripting"

    DetailPrint "Removing registry entries..."
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LLMscripting"
    DeleteRegKey HKLM "Software\LLMscripting"

    DetailPrint "Removing files..."
    RMDir /r "$INSTDIR"

    DetailPrint "Python was left installed."

    DetailPrint "Uninstall complete."
SectionEnd