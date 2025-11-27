import os
from http import HTTPStatus
from dashscope import Application
import sys
import threading
import time

class AIChatBot:
    """AI聊天机器人"""
    
    def __init__(self, api_key: str, app_id: str):
        """初始化聊天机器人
        
        Args:
            api_key: 阿里云百炼API Key
            app_id: 应用ID
        """
        self.api_key = api_key
        self.app_id = app_id
        self.session_id = ''
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
    
    def chat(self, user_input: str) -> str:
        """与AI进行一轮对话
        
        Args:
            user_input: 用户输入的问题
            
        Returns:
            AI的完整回复
        """
        full_response = ''
        buffer = ''
        first_response = True
        
        self._start_loading()
        
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
            
        except Exception as e:
            self._stop_loading()
            print(f'\n[异常] {str(e)}')
        
        return full_response
    
    def run(self):
        """启动交互式聊天"""
        print('='*50)
        print('AI聊天小程序')
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

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('api-key'):
                        api_key = line.split('=', 1)[1].strip()
                    elif line.startswith('app-id'):
                        app_id = line.split('=', 1)[1].strip()
        except Exception as e:
            print(f'[错误] 读取config.txt失败: {str(e)}')
            sys.exit(1)

    if not api_key or not app_id:
        if len(sys.argv) >= 3:
            api_key = sys.argv[1]
            app_id = sys.argv[2]
        else:
            print('用法1: python chat.py (自动从目录config.txt读取)')
            print('用法2: python chat.py <API_KEY> <APP_ID>')
            print('\n示例: python chat.py sk-xxxx app-id-xxxx')
            sys.exit(1)

    chatbot = AIChatBot(api_key, app_id)
    chatbot.run()