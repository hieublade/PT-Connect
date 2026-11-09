@echo off
chcp 65001 >nul
title PT-Connect Launcher (Windows)

echo =====================================================================
echo          KHỞI ĐỘNG HỆ THỐNG PT-CONNECT TRÊN WINDOWS
echo =====================================================================
echo.

:: 1. Kiểm tra lựa chọn chế độ chạy
echo Bạn muốn chạy bằng cách nào?
echo   [1] Dùng Docker Compose (Khuyên dùng - Tự bật cả MySQL, Backend, Frontend)
echo   [2] Chạy trực tiếp bằng Python (Siêu nhẹ, không tốn RAM máy)
echo.
set /p choice="Nhập lựa chọn của bạn (1 hoặc 2, mặc định 1): "

if "%choice%"=="2" goto RUN_PYTHON
goto RUN_DOCKER

:RUN_DOCKER
echo.
echo [*] Đang khởi động 3 dịch vụ bằng Docker Compose...
docker compose -f docker-compose.python.yml up --build
goto END

:RUN_PYTHON
echo.
echo [*] Đang khởi động Backend FastAPI ở cửa sổ riêng...
start "PT-Connect Backend (FastAPI :8080)" cmd /k "cd backend-py && if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) else if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) && uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload"

timeout /t 3 /nobreak >nul

echo [*] Đang khởi động Frontend Streamlit ở cửa sổ riêng...
start "PT-Connect Frontend (Streamlit :8501)" cmd /k "cd frontend && if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) else if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) && set BACKEND_URL=http://localhost:8080 && streamlit run app.py --server.port 8501"

echo.
echo =====================================================================
echo  HỆ THỐNG ĐÃ ĐƯỢC BẬT THÀNH CÔNG!
echo  - Frontend Web: http://localhost:8501
echo  - Backend Docs: http://localhost:8080/docs
echo =====================================================================
echo  (Đừng tắt 2 cửa sổ màu đen vừa bật lên nhé)
echo.
pause

:END
