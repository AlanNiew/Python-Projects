@echo off
chcp 65001
REM AI聊天小程序 - Windows 运行脚本

REM 支持三种运行方式：
REM 方式1: run.bat (自动从 config.ini 读取)
REM 方式2: run.bat <API_KEY> <APP_ID> [运行模式] [模型] [是否启用思考]
REM 方式3: run.bat <API_KEY> "" generation deepseek-v3.2-exp true

setlocal enabledelayedexpansion

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请确保已安装 Python 并添加到 PATH 环境变量
    pause
    exit /b 1
)

REM 检查是否提供了命令行参数
if "%1"=="" (
    REM 方式1: 从 config.ini 读取
    echo 从 config.ini 读取配置...
    python chat.py
) else (
    REM 方式2〗3: 使用提供的参数
    echo 使用提供的参数运行...
    if "%2"=="" (
        echo 错误: 须提供 APP_ID
        echo 用法1: run.bat (自动从 config.ini 读取)
        echo 用法2: run.bat ^<API_KEY^> ^<APP_ID^> [MODE] [MODEL] [ENABLE_THINKING]
        echo 用法3: run.bat ^<API_KEY^> "" generation deepseek-v3.2-exp true
        echo.
        echo 示例1: run.bat sk-xxxx app-id-xxxx
        echo 示例2: run.bat sk-xxxx "" generation deepseek-v3.2-exp true
        pause
        exit /b 1
    ) else (
        python chat.py %1 %2 %3 %4 %5
    )
)

pause
