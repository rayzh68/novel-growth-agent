# Run this from the folder that contains novel-growth-agent.
$Source = Join-Path (Get-Location) "novel-growth-agent"
$Target = "D:\novel-growth-agent"

if (Test-Path $Target) {
  Write-Host "Removing old folder: $Target"
  Remove-Item $Target -Recurse -Force
}

Copy-Item $Source $Target -Recurse -Force
Write-Host "Copied to $Target"
Write-Host "Next:"
Write-Host "cd D:\novel-growth-agent"
Write-Host ".\setup_windows.ps1"
