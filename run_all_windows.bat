@echo off
chcp 65001 >nul
title PT-Connect Launcher (Windows)

echo =====================================================================
echo          KHỞI ĐỘNG HỆ THỐNG PT-CONNECT TRÊN WINDOWS
echo =====================================================================
echo.

:: 1. Kiểm tra lựa chọn chế độ chạy
echo Bạn muốn chạy bằng cách nào?
echo   [1] Dùng Docker Compose (Khuyên dùng - Tự động build image và bật MySQL, Backend, Frontend)
echo   [2] Chạy trực tiếp bằng Python (Siêu nhẹ, không cần Docker, không tốn RAM máy)
echo.
set /p choice="Nhập lựa chọn của bạn (1 hoặc 2, mặc định 1): "

if "%choice%"=="2" goto RUN_PYTHON
goto RUN_DOCKER

:RUN_DOCKER
echo.
echo [*] Đang kiểm tra trạng thái Docker Desktop...
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CẢNH BÁO] Docker Desktop chưa được bật hoặc chưa cài đặt!
    echo - Vui lòng mở ứng dụng 'Docker Desktop' trên máy và đợi biểu tượng chuyển sang màu xanh.
    echo - Hoặc bạn có thể bấm phím bất kỳ để chuyển sang chạy Chế độ 2 (Python trực tiếp).
    echo.
    pause
    goto RUN_PYTHON
)

echo [*] Đang tự động BUILD IMAGE và khởi động 3 container (MySQL, Backend, Frontend)...
echo [*] (Lần đầu tiên chạy sẽ mất khoảng 2-3 phút để tải và build image, xin vui lòng đợi...)
echo.
docker compose -f docker-compose.python.yml up --build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [LỖI] Có lỗi xảy ra trong quá trình khởi động Docker.
    pause
)
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
