# Career Companion - Start CLI Chat
Write-Host "💬 Starting Career Companion CLI Chat..." -ForegroundColor Cyan
Write-Host "Make sure the server is running at http://localhost:8000`n" -ForegroundColor Yellow

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Start CLI chat
python frontend\cli_chat.py
