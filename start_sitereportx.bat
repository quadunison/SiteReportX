@echo off
chcp 65001 > nul
title SiteReportX - 배관 검사 보고서 자동화 웹앱
echo ========================================================
echo   SiteReportX 웹 플랫폼을 시작합니다...
echo ========================================================
cd /d "%~dp0"
python run_server.py
pause
