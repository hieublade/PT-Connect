@echo off
title PTConnect Backend (Spring Boot :8080)
echo =======================================================
echo    Dang khoi dong PTConnect Backend (Spring Boot)...
echo =======================================================

if not defined JAVA_HOME (
    if exist "C:\jdk" (
        set "JAVA_HOME=C:\jdk"
        set "PATH=C:\jdk\bin;%PATH%"
    )
)

cd /d "%~dp0backend"
call mvnw.cmd spring-boot:run
pause
