$ErrorActionPreference = "Stop"

# Locate NVGT binary via PATH
$nvgtCmd = Get-Command nvgt -ErrorAction SilentlyContinue

if (-not $nvgtCmd) {
  throw "nvgt not found in PATH"
}

# Get directory of nvgt.exe
$nvgtDir = Split-Path $nvgtCmd.Source

# Define download target
$file = "nvgtpm.exe"
$url = "https://github.com/harrymkt/nvgtpm/releases/latest/download/$file"

# Download
Write-Output "Downloading..."
$oldProgressPreference = $ProgressPreference
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $url -OutFile $file
$ProgressPreference = $oldProgressPreference

# Move into NVGT directory
Move-Item -Path $file -Destination (Join-Path $nvgtDir $file) -Force

Write-Output "NVGTPM installed to $nvgtDir"
