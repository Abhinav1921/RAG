# PowerShell script to run the Document Analysis app
Write-Host "🚀 Starting Document Analysis MCP Server..." -ForegroundColor Green

# Check if MongoDB is running
Write-Host "🔍 Checking MongoDB connection..." -ForegroundColor Yellow
$mongoRunning = netstat -an | findstr :27017
if (-not $mongoRunning) {
    Write-Host "❌ MongoDB is not running on port 27017!" -ForegroundColor Red
    Write-Host "Please start MongoDB using MongoDB Compass or mongod command" -ForegroundColor Yellow
    Write-Host "Press any key to continue anyway..."
    Read-Host
} else {
    Write-Host "✅ MongoDB is running" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🐍 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file based on .env.example" -ForegroundColor Yellow
    Write-Host "You need to set up your Google AI API key" -ForegroundColor Yellow
    exit 1
}

# Check Google AI API key
Write-Host "🔑 Checking Google AI API key..." -ForegroundColor Yellow
$envContent = Get-Content .env
$apiKeyLine = $envContent | Where-Object { $_ -like "GOOGLE_API_KEY=*" }
if ($apiKeyLine -and $apiKeyLine -notlike "*your_google_ai_api_key_here*") {
    Write-Host "✅ Google AI API key configured" -ForegroundColor Green
} else {
    Write-Host "⚠️  Google AI API key not set - some features may not work" -ForegroundColor Yellow
    Write-Host "Please set your API key in the .env file" -ForegroundColor Yellow
    Write-Host "Get one at: https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
}

# Run the Streamlit app
Write-Host "🌐 Starting Streamlit app..." -ForegroundColor Green
Write-Host "The app will open in your browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
streamlit run document_streamlit_app.py
