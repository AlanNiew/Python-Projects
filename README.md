# Python Projects
Hi,欢迎来到我的 Python 项目集合！

## 项目列表

### 01：必应壁纸助手
这个项目可以自动下载并设置必应每日壁纸作为你的桌面背景。
资源API: https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&country=CN&locale=zh-CN
![程序预览](/bing/resource/preview.png)
![壁纸预览](/bing/resource/wallpaper_1755010258.jpg)

### 02：ali-dashscope
AI聊天小程序，基于阿里云百炼API，支持两种智能对话模式。提供流式输出、会话管理和实时交互体验。

**两种工作模式：**
- **Application 模式**：调用预配置的应用实例，开箱即用
- **Generation 模式**：调用通用大语言模型，支持模型选择和思考模式

**核心功能：**
- ✨ 多轮对话，自动维持会话上下文
- 🔄 流式输出和增量输出
- ⏳ 实时加载动画
- 🧠 思考模式（仅 Generation 模式，部分模型支持）
- 💾 会话ID管理
- ⚙️ 灵活的配置管理（INI 格式）
- 🖥️ 支持命令行参数覆盖配置

**使用方式：**
```bash
# 方式1：从 config.txt 读取配置（推荐）
python chat.py

# 方式2：Application 模式 + 命令行参数
python chat.py <API_KEY> <APP_ID>

# 方式3：Generation 模式 + 思考模式
python chat.py <API_KEY> "" generation deepseek-v3.2-exp true

# Windows 批处理脚本
run.bat <API_KEY> <APP_ID>

# Linux/MacOS 脚本
./run.sh <API_KEY> <APP_ID>
```

**配置文件示例 (config.txt)：**
```ini
[API]
api_key = sk-xxx
app_id = 519c7167d9084c1cbe9127cdea27c892

[MODE]
# application 或 generation
mode = application

[MODEL]
# deepseek-v3.2-exp, deepseek-v3.1, deepseek-v3, deepseek-r1
model = deepseek-v3.2-exp

[THINKING]
# 是否启用思考模式
enable_thinking = false
```

**命令行参数说明：**
| 参数 | 说明 | 必需 |
|------|------|------|
| API_KEY | 阿里云百炼API密钥 | 是 |
| APP_ID | 应用ID (application模式) | 仅Application模式 |
| MODE | 运行模式 (application/generation) | 否 |
| MODEL | LLM模型名称 | 否 |
| ENABLE_THINKING | 启用思考模式 (true/false) | 否 |