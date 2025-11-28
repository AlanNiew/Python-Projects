import os
from http import HTTPStatus
from dashscope import Application, Generation
import sys
import threading
import time
import configparser

class AIChatBot:
    """AI聊天机器人，支持两种模式：Application（应用模式）和 Generation（通用模型模式）"""
    
    def __init__(self, api_key: str, app_id: str, mode: str = 'application', model: str = 'deepseek-v3.2-exp', enable_thinking: bool = False):
        """初始化聊天机器人
        
        Args:
            api_key: 阿里云百炼API Key
            app_id: 应用ID（在 application 模式下使用）
            mode: 运行模式，'application' 或 'generation'（默认 'application'）
            model: LLM 模型名称（在 generation 模式下使用，默认 'deepseek-v3.2-exp'）
            enable_thinking: 是否启用思考模式（仅 generation 模式，默认 False）
        """
        self.api_key = api_key
        self.app_id = app_id
        self.mode = mode.lower()
        self.model = model
        self.enable_thinking = enable_thinking
        self.session_id = ''
        self.messages = []  # 消息历史（generation 模式使用）
        self.loading = False
        self.loading_thread = None
    
    def _show_loading(self):
        """显示加载动画"""
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        index = 0
        while self.loading:
            sys.stdout.write(f'\r{spinner[index % len(spinner)]} 加载中...')
            sys.stdout.flush()
            index += 1
            time.sleep(0.1)
    
    def _start_loading(self):
        """启动加载动画"""
        self.loading = True
        self.loading_thread = threading.Thread(target=self._show_loading, daemon=True)
        self.loading_thread.start()
    
    def _stop_loading(self):
        """停止加载动画"""
        self.loading = False
        if self.loading_thread:
            self.loading_thread.join(timeout=0.5)
        sys.stdout.write('\r' + ' ' * 20 + '\r')
        sys.stdout.flush()
    
    def _should_output(self, buffer: str) -> bool:
        """判断是否应该输出缓冲区的内容
        
        Args:
            buffer: 暂存的文本
            
        Returns:
            是否应该输出
        """
        # 判断条件：1. 缓冲区长度>=50个字符  2. 以句号/问号/感叹号结尾
        sentence_endings = ('。', '？', '！', '.', '?', '!')
        return len(buffer) >= 50 or buffer.endswith(sentence_endings)
    
    def _chat_with_application(self, user_input: str) -> str:
        """使用 Application API 进行对话（应用模式）
        
        Args:
            user_input: 用户输入的问题
            
        Returns:
            AI的完整回复
        """
        full_response = ''
        buffer = ''
        first_response = True
        
        try:
            responses = Application.call(
                api_key=self.api_key,
                app_id=self.app_id,
                prompt=user_input,
                session_id=self.session_id,
                stream=True,  # 流式输出
                incremental_output=True  # 增量输出
            )
            
            for response in responses:
                if first_response:
                    self._stop_loading()
                    first_response = False
                
                if response.status_code != HTTPStatus.OK:
                    print(f'\n[错误] request_id={response.request_id}')
                    print(f'code={response.status_code}')
                    print(f'message={response.message}')
                    print(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')
                    return full_response
                else:
                    # 提取文本内容
                    if hasattr(response, 'output') and response.output:
                        text = response.output.text if hasattr(response.output, 'text') else ''
                        if text:
                            full_response += text
                            buffer += text
                            # 检查是否应该输出
                            if self._should_output(buffer):
                                sys.stdout.write(buffer)
                                sys.stdout.flush()
                                buffer = ''

                        # 更新session_id
                        if hasattr(response.output, 'session_id'):
                            self.session_id = response.output.session_id
            
            # 停止加载动画（如果还在运行）
            if self.loading:
                self._stop_loading()
            
            # 输出剩余的缓冲区内容
            if buffer:
                sys.stdout.write(buffer)
                sys.stdout.flush()
            
            print()  # 换行
            
        except Exception as _e:
            self._stop_loading()
            print(f'\n[异常] {str(_e)}')
        
        return full_response
    
    def _chat_with_generation(self, user_input: str) -> str:
        """使用 Generation API 进行对话（通用模型模式）
        
        Args:
            user_input: 用户输入的问题
            
        Returns:
            AI的完整回复
        """
        full_response = ''
        reasoning_content = ""
        answer_content = ""
        is_answering = False
        
        try:
            # 添加用户消息到历史
            self.messages.append({"role": "user", "content": user_input})
            
            # 调用 Generation API
            completion = Generation.call(
                api_key=self.api_key,
                model=self.model,
                messages=self.messages,
                result_format="message",
                enable_thinking=self.enable_thinking,
                stream=True,
                incremental_output=True
            )
            
            first_response = True
            last_chunk = None
            
            for chunk in completion:
                if first_response:
                    self._stop_loading()
                    if self.enable_thinking:
                        print("\n" + "="*20 + "思考过程" + "="*20 + "\n")
                    first_response = False
                
                last_chunk = chunk
                message = chunk.output.choices[0].message
                
                # 收集思考内容
                if self.enable_thinking and hasattr(message, 'reasoning_content') and message.reasoning_content:
                    if not is_answering:
                        print(message.reasoning_content, end="", flush=True)
                    reasoning_content += message.reasoning_content
                
                # 收集回复内容
                if hasattr(message, 'content') and message.content:
                    if not is_answering and self.enable_thinking:
                        print("\n" + "="*20 + "完整回复" + "="*20 + "\n")
                    if not is_answering:
                        is_answering = True
                    print(message.content, end="", flush=True)
                    answer_content += message.content
            
            # 输出 Token 消耗
            # if last_chunk and hasattr(last_chunk, 'usage'):
            #     print("\n" + "="*20 + "Token 消耗" + "="*20 + "\n")
            #     print(last_chunk.usage)
            
            # 添加助手回复到消息历史
            if answer_content:
                assistant_message = {"role": "assistant", "content": answer_content}
                if self.enable_thinking and reasoning_content:
                    assistant_message["reasoning_content"] = reasoning_content
                self.messages.append(assistant_message)
            
            full_response = answer_content
            print()  # 换行
            
        except Exception as _e:
            self._stop_loading()
            print(f'\n[异常] {str(_e)}')
        
        return full_response
    
    def chat(self, user_input: str) -> str:
        """与AI进行一轮对话
        
        Args:
            user_input: 用户输入的问题
            
        Returns:
            AI的完整回复
        """
        self._start_loading()
        
        if self.mode == 'generation':
            return self._chat_with_generation(user_input)
        else:
            return self._chat_with_application(user_input)
    
    def run(self):
        """启动交互式聊天"""
        print('='*50)
        print('AI聊天小程序')
        print(f'运行模式: {self.mode.upper()}')
        if self.mode == 'generation':
            print(f'模型: {self.model}')
            print(f'思考模式: {"启用" if self.enable_thinking else "禁用"}')
        print('='*50)
        print('提示：输入 "exit" 或 "quit" 退出')
        print('-'*50)
        
        while True:
            user_input = input('\n你: ').strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                print('\n再见！')
                break
            
            print('\nAI: ', end='')
            self.chat(user_input)


if __name__ == '__main__':
    api_key = None
    app_id = None
    mode = 'application'  # 默认模式
    model = 'deepseek-v3.2-exp'  # 默认模型
    enable_thinking = False  # 默认不启用思考模式

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

    if os.path.exists(config_path):
        try:
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            
            # 读取 API 配置
            if config.has_section('API'):
                api_key = config.get('API', 'api_key', fallback=None)
                app_id = config.get('API', 'app_id', fallback=None)
            
            # 读取模式配置
            if config.has_section('MODE'):
                mode = config.get('MODE', 'mode', fallback='application')
            
            # 读取模型配置
            if config.has_section('MODEL'):
                model = config.get('MODEL', 'model', fallback='deepseek-v3.2-exp')
            
            # 读取思考模式配置
            if config.has_section('THINKING'):
                enable_thinking = config.getboolean('THINKING', 'enable_thinking', fallback=False)
        
        except Exception as e:
            print(f'[错误] 读取config.txt失败: {str(e)}')
            sys.exit(1)

    if not api_key:
        if len(sys.argv) >= 2:
            api_key = sys.argv[1]
            if len(sys.argv) >= 3:
                app_id = sys.argv[2]
            if len(sys.argv) >= 4:
                mode = sys.argv[3]
            if len(sys.argv) >= 5:
                model = sys.argv[4]
            if len(sys.argv) >= 6:
                enable_thinking = sys.argv[5].lower() in ('true', '1', 'yes')
        else:
            print('用法1: python chat.py (自动从目录config.txt读取)')
            print('用法2: python chat.py <API_KEY> [APP_ID] [MODE] [MODEL] [ENABLE_THINKING]')
            print('\n参数说明:')
            print('  API_KEY: 阿里云百炼API Key (必需)')
            print('  APP_ID: 应用ID (application 模式需要，生成模式可选)')
            print('  MODE: 运行模式，"application" 或 "generation" (默认 "application")')
            print('  MODEL: LLM 模型名称，如 "deepseek-v3.2-exp" (默认 "deepseek-v3.2-exp")')
            print('  ENABLE_THINKING: 是否启用思考模式，"true" 或 "false" (默认 "false")')
            print('\n示例1: python chat.py sk-xxxx app-id-xxxx')
            print('示例2: python chat.py sk-xxxx "" generation deepseek-v3.2-exp true')
            sys.exit(1)

    chatbot = AIChatBot(api_key, app_id or '', mode=mode, model=model, enable_thinking=enable_thinking)
    chatbot.run()