@echo off
title Khoi tao CSDL MySQL ptconnect
echo =======================================================
echo    Dang nap CSDL ptconnect tu init.sql va seed_demo.sql...
echo =======================================================

set MYSQL_BIN=mysql
if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" (
    set "MYSQL_BIN=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
)

echo 1. Tao Database ptconnect...
"%MYSQL_BIN%" -u root -p123 -e "CREATE DATABASE IF NOT EXISTS ptconnect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo 2. Khoi tao bang (init.sql)...
"%MYSQL_BIN%" -u root -p123 ptconnect < "%~dp0database\init.sql"

echo 3. Nap du lieu mau (seed_demo.sql)...
"%MYSQL_BIN%" -u root -p123 ptconnect < "%~dp0database\seed_demo.sql"

echo.
echo =======================================================
echo   DA KHOI TAO CSDL PTCONNECT VA NAP DU LIEU MAU XONG!
echo =======================================================
pause
