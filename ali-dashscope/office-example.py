import os
from dashscope import Generation

# 初始化请求参数
messages = [{"role": "user", "content": "你是谁？"}]

completion = Generation.call(
    # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
    api_key="sk-xxx",
    # 此处以 deepseek-v3.2-exp 为例，可按需更换模型名称为 deepseek-v3.1、deepseek-v3 或 deepseek-r1
    model="deepseek-v3.2-exp",
    messages=messages,
    session_id="",
    result_format="message",  # 设置结果格式为 message
    enable_thinking=False,     # 开启思考模式，该参数仅对 deepseek-v3.2-exp 和 deepseek-v3.1 有效。deepseek-v3 和 deepseek-r1 设定不会报错
    stream=True,              # 开启流式输出
    incremental_output=True,  # 开启增量输出
)

reasoning_content = ""  # 完整思考过程
answer_content = ""     # 完整回复
is_answering = False    # 是否进入回复阶段

print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

for chunk in completion:
    message = chunk.output.choices[0].message
    # 只收集思考内容
    if "reasoning_content" in message:
        if not is_answering:
            print(message.reasoning_content, end="", flush=True)
        reasoning_content += message.reasoning_content

    # 收到 content，开始进行回复
    if message.content:
        if not is_answering:
            print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
            is_answering = True
        print(message.content, end="", flush=True)
        answer_content += message.content

print("\n" + "=" * 20 + "Token 消耗" + "=" * 20 + "\n")
print(chunk.usage)