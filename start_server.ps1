# Career Companion - Start Server Script
Write-Host "🚀 Starting Career Companion Server..." -ForegroundColor Cyan

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Set Python path
$env:PYTHONPATH = "c:\Users\ganes\OneDrive\Desktop\AI botPlacemnt"

# Start the server
Write-Host "📍 Server will run on: http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Docs at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

python backend\main.py
