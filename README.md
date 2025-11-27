# Python Projects
Hi,欢迎来到我的 Python 项目集合！

## 项目列表

### 01：必应壁纸助手
这个项目可以自动下载并设置必应每日壁纸作为你的桌面背景。
资源API: https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&country=CN&locale=zh-CN
![程序预览](/bing/resource/preview.png)
![壁纸预览](/bing/resource/wallpaper_1755010258.jpg)

### 02：ali-dashscope
这是一个基于阿里云百炼API的交互式聊天机器人程序。支持流式对话、会话管理和实时加载动画。

**主要功能：**
- 与AI进行多轮对话
- 支持流式输出和增量输出
- 实时加载动画提示
- 会话ID管理维护上下文
- 支持命令行参数或配置文件传入API密钥

**使用方式：**
```bash
# 方式1：从 config.txt 读取配置
python chat.py

# 方式2：命令行传入参数
python chat.py <API_KEY> <APP_ID>
```

**配置文件示例 (config.txt)：**
```
api-key = sk-xxxx
app-id = xxxx
```