@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════╗
echo ║   厌氧反应器智能诊断系统          ║
echo ║   正在启动 Web 界面...            ║
echo ╚════════════════════════════════════╝
echo.
echo 浏览器即将自动打开 http://localhost:8501
echo 按 Ctrl+C 可停止服务
echo.

start "" http://localhost:8501

python -m streamlit run anaerobic_reactor_agent/web/app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false

pause
