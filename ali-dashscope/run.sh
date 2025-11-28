#!/bin/bash

# AI聊天小程序 - Linux/MacOS 运行脚本
# 支持三种运行方式:
# 方式1: ./run.sh (自动从 config.ini 读取)
# 方式2: ./run.sh <API_KEY> <APP_ID> [运行模式] [模型] [是否启用思考]
# 方式3: ./run.sh <API_KEY> "" generation deepseek-v3.2-exp true

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请确保已安装 Python3"
    exit 1
fi

# 检查是否提供了命令行参数
if [ $# -eq 0 ]; then
    # 方式1: 从 config.ini 读取
    echo "从 config.ini 读取配置..."
    python3 chat.py
elif [ $# -ge 2 ]; then
    # 方式2〗3: 使用提供的参数
    echo "使用提供的参数运行..."
    python3 chat.py "$1" "$2" "$3" "$4" "$5"
else
    echo "错误: 参数数量不正确"
    echo "用法1: ./run.sh (自动从 config.ini 读取)"
    echo "用法2: ./run.sh <API_KEY> <APP_ID> [MODE] [MODEL] [ENABLE_THINKING]"
    echo "用法3: ./run.sh <API_KEY> \"\" generation deepseek-v3.2-exp true"
    echo ""
    echo "示例1: ./run.sh sk-xxxx app-id-xxxx"
    echo "示例2: ./run.sh sk-xxxx \"\" generation deepseek-v3.2-exp true"
    exit 1
fi
