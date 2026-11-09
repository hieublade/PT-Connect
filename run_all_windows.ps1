# =====================================================================
# PT-Connect Launcher (PowerShell Windows)
# =====================================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "         KHỞI ĐỘNG HỆ THỐNG PT-CONNECT TRÊN WINDOWS (POWERSHELL)     " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Chọn chế độ chạy: [1] Docker Compose (Mặc định) | [2] Python Trực Tiếp"
if ($choice -ne "2") {
    Write-Host "`n[*] Đang khởi động qua Docker Compose..." -ForegroundColor Green
    docker compose -f docker-compose.python.yml up --build
} else {
    Write-Host "`n[*] Đang bật Backend FastAPI (Port 8080)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend-py; if (Test-Path .venv/Scripts/Activate.ps1) { . .venv/Scripts/Activate.ps1 } elseif (Test-Path venv/Scripts/Activate.ps1) { . venv/Scripts/Activate.ps1 }; uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"

    Start-Sleep -Seconds 3

    Write-Host "[*] Đang bật Frontend Streamlit (Port 8501)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; if (Test-Path .venv/Scripts/Activate.ps1) { . .venv/Scripts/Activate.ps1 } elseif (Test-Path venv/Scripts/Activate.ps1) { . venv/Scripts/Activate.ps1 }; `$env:BACKEND_URL='http://localhost:8080'; streamlit run app.py --server.port 8501"

    Write-Host "`n=====================================================================" -ForegroundColor Green
    Write-Host " HỆ THỐNG ĐÃ ĐƯỢC BẬT THÀNH CÔNG!" -ForegroundColor Green
    Write-Host " - Frontend Web: http://localhost:8501" -ForegroundColor Cyan
    Write-Host " - Backend Docs: http://localhost:8080/docs" -ForegroundColor Cyan
    Write-Host "=====================================================================`n" -ForegroundColor Green
}
