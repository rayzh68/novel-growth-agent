param(
  [string]$ProjectDir = "D:\novel-growth-agent"
)

Write-Host "Setting up novel-growth-agent in $ProjectDir"

Set-Location $ProjectDir

if (-not (Test-Path ".venv")) {
  py -m venv .venv
}

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env" -Force
}

Write-Host "Running sample full workflow through unified controller..."
python main.py all --book book_001 --round round_001

Write-Host "Done."
Write-Host "From now on, use only: python main.py <command>"
Write-Host "Check output folder: $ProjectDir\output"
