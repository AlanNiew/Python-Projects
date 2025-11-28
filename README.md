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
# 方式1：从 config.ini 读取配置（推荐）
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

### 03：variable-translator
智能中文变量名翻译器，支持本地词典和在线翻译双模式，快速生成符合规范的英文变量名。基于PyQt5构建，提供简洁美观的GUI界面。

**核心功能：**
- 🎯 智能分词与翻译，支持词组识别
- 📖 双词典系统：默认词典（62个常用术语）+ 用户自定义词典
- 🌐 在线翻译支持（百度翻译API）
- 🔧 5种命名风格：camelCase / PascalCase / snake_case / UPPER_CASE / kebab-case
- ⚡ 实时翻译，即输即出
- 💾 自动缓存翻译结果到本地词典
- 📋 一键复制翻译结果
- 🎨 简洁白底黑字界面设计

**使用方式：**
```bash
# 启动GUI界面
python gui.py
```

**配置文件 (config.ini)：**
```ini
appid=你的百度翻译APPID
key=你的百度翻译密钥
```

**词典文件说明：**
- `default.txt`: 系统默认术语词典（62个常用编程术语）
- `user.txt`: 用户自定义词典，支持手动添加和在线翻译自动缓存
- 格式：`中文词=英文词`（每行一个词对）

**功能特色：**
1. **智能词组识别**：优先匹配词典中的多字词组，提高翻译准确性
2. **混合翻译模式**：本地词典翻译 + 在线API翻译无缝结合
3. **自动学习机制**：在线翻译结果自动保存至user.txt，避免重复调用API
4. **多风格支持**：一键切换5种主流命名风格，适配不同编程规范
5. **实时加载动画**：在线翻译过程中显示加载状态，提升用户体验