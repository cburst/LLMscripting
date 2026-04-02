# ============================================================
# REQUIRE ADMIN
# ============================================================
if (-not ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Start-Process powershell.exe `
        "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" `
        -Verb RunAs
    exit
}

$ErrorActionPreference = "Stop"

# ============================================================
# MAIN (LOGGED)
# ============================================================
try {

    # ------------------------------------------------------------
    # LOGGING
    # ------------------------------------------------------------
    $LOG = "$env:TEMP\gptmulti_install.log"

    if (Test-Path $LOG) {
        Remove-Item $LOG
    }

    Start-Transcript -Path $LOG -Append
    $ProgressPreference = "SilentlyContinue"

    # ------------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------------
    $TARGET_DIR = "C:\LLMscripting-main"
    $REPO_ZIP = "https://github.com/cburst/LLMscripting/archive/refs/heads/main.zip"

    # ============================================================
    # 1. INSTALL PYTHON
    # ============================================================
    Write-Output "Installing Python..."

    $pythonInstaller = "$env:TEMP\python.exe"
    Invoke-WebRequest `
        "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" `
        -OutFile $pythonInstaller

    Start-Process $pythonInstaller `
        -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" `
        -WindowStyle Hidden -Wait

    Start-Sleep -Seconds 2

    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine")

    # ============================================================
    # 2. DOWNLOAD + EXTRACT REPO
    # ============================================================
    Write-Output "Downloading LLM Scripting..."

    $zipPath = "$env:TEMP\llm.zip"
    $tempDir = "$env:TEMP\llm-temp"

    Invoke-WebRequest $REPO_ZIP -OutFile $zipPath

    if (Test-Path $tempDir) {
        Remove-Item -Recurse -Force $tempDir
    }

    Expand-Archive $zipPath -DestinationPath $tempDir -Force

    # ============================================================
    # OVERWRITE INSTALL
    # ============================================================
    if (-not (Test-Path $TARGET_DIR)) {
        New-Item -ItemType Directory -Path $TARGET_DIR | Out-Null
        Write-Output "Creating new installation directory..."
    } else {
        Write-Output "Updating existing installation..."
    }

    $extracted = Get-ChildItem $tempDir | Select-Object -First 1

    Copy-Item "$($extracted.FullName)\*" `
        -Destination $TARGET_DIR `
        -Recurse `
        -Force

    Remove-Item -Recurse -Force $tempDir

    # ============================================================
    # 3. INSTALL DEPENDENCIES
    # ============================================================
    Write-Output "Installing dependencies..."

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue

    if (-not $pythonCmd) {
        Write-Output "Python not found in PATH, using fallback..."
        $pythonCmd = "C:\Program Files\Python311\python.exe"
    } else {
        $pythonCmd = $pythonCmd.Source
    }

    Write-Output "Using Python: $pythonCmd"

    # Upgrade pip
    & $pythonCmd -m pip install --upgrade pip

    # Install requirements (both files preserved from original)
    & $pythonCmd -m pip install -r "$TARGET_DIR\folders\gpt-cli\requirements.txt"

    # Ensure GPT CLI exists in SAME environment
    & $pythonCmd -m pip install gpt-command-line

    # ------------------------------------------------------------
    # ADD USER PYTHON SCRIPTS TO PATH
    # ------------------------------------------------------------
    Write-Output "Adding Python Scripts directory to PATH..."

    try {

        # detect Python version dynamically (e.g., Python311)
        $pythonVersion = & $pythonCmd -c "import sys; print(f'Python{sys.version_info.major}{sys.version_info.minor}')"
        $scriptPath = "$env:APPDATA\Python\$pythonVersion\Scripts"

        if (Test-Path $scriptPath) {

            $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")

            if ($userPath -notlike "*$scriptPath*") {

                [Environment]::SetEnvironmentVariable(
                    "PATH",
                    "$userPath;$scriptPath",
                    "User"
                )

                Write-Output "Added to PATH: $scriptPath"

            } else {

                Write-Output "Scripts path already in PATH."

            }

        } else {

            Write-Output "⚠️ Scripts directory not found: $scriptPath"

        }

        # refresh PATH for current session
        $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "User")

    } catch {

        Write-Output "⚠️ Failed to update PATH: $($_.Exception.Message)"

    }

    # ============================================================
    # 3.5 COPY GPT CONFIG (CRITICAL)
    # ============================================================
    Write-Output "Setting up gpt-cli config..."

    try {

        $configDir = "$env:USERPROFILE\.config\gpt-cli"
        $configFile = "$configDir\gpt.yml"
        $sourceConfig = "$TARGET_DIR\folders\gpt-cli\gpt.yml"

        # Create config directory if it doesn't exist
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
            Write-Output "Created config directory: $configDir"
        }

        # Copy gpt.yml (overwrite to ensure consistency)
        if (Test-Path $sourceConfig) {

            Copy-Item $sourceConfig $configFile -Force
            Write-Output "Copied gpt.yml → $configFile"

        } else {

            Write-Output "⚠️ gpt.yml not found at: $sourceConfig"

        }

    } catch {

        Write-Output "⚠️ Failed to set up gpt-cli config: $($_.Exception.Message)"

    }

    # ============================================================
    # 4. CREATE DESKTOP SHORTCUT
    # ============================================================
    Write-Output "Creating desktop shortcut..."

    $desktop = [Environment]::GetFolderPath("Desktop")

    $WshShell = New-Object -ComObject WScript.Shell
    $shortcut = $WshShell.CreateShortcut("$desktop\Grammar Pipeline.lnk")

    $shortcut.TargetPath = "$pythonCmd"
    $shortcut.Arguments = "`"$TARGET_DIR\run_gui.py`""
    $shortcut.WorkingDirectory = $TARGET_DIR
    $shortcut.IconLocation = "$TARGET_DIR\app\data\icon.ico"

    $shortcut.Save()

    # ============================================================
    # DONE
    # ============================================================
    Write-Output ""
    Write-Output "========================================"
    Write-Output "✅ Grammar Pipeline installation complete!"
    Write-Output "========================================"

}
finally {
    try { Stop-Transcript } catch {}
}