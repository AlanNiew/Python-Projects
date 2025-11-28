import os
import sys
import threading
import time

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QTextEdit,
    QDialog, QMessageBox, QTabWidget
)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer

sys.path.insert(0, os.path.dirname(__file__))
from AdvancedVariableTranslator import AdvancedTranslator

# 颜色主题定义
COLOR_SCHEME = {
    'bg_main': '#ffffff',
    'bg_light': '#ffffff',
    'primary': '#000000',
    'primary_hover': '#333333',
    'text_dark': '#000000',
    'text_light': '#666666',
    'border': '#d0d0d0',
}


class TranslateSignals(QObject):
    """翻译信号发射器"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


class TranslatorGUI(QMainWindow):
    """中文变量名翻译器 PyQt5 版本"""

    def __init__(self):
        super().__init__()
        self.translator = AdvancedTranslator()
        self.translate_signals = TranslateSignals()
        self.translate_signals.finished.connect(self.on_translate_finished)
        self.translate_signals.error.connect(self.on_translate_error)
        self.translate_thread = None
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self._update_loading_animation)
        self.loading_frame = 0
        self.init_ui()
        self.set_icon()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("中文变量名翻译器")

        # 窗口居中
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - 700) // 2
        y = (screen_geometry.height() - 500) // 2
        self.setGeometry(x, y, 700, 500)

        self.setStyleSheet(self.get_stylesheet())
        
        # 主窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("中文变量名翻译器")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 输入框区域
        input_label = QLabel("输入中文:")
        input_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(input_label)
        
        self.input_text = QLineEdit()
        self.input_text.setFont(QFont("Arial", 12))
        self.input_text.setMinimumHeight(35)
        self.input_text.setStyleSheet(
            "QLineEdit { border: 1px solid #d0d0d0; padding: 5px; }"
        )
        self.input_text.textChanged.connect(self.translate)
        layout.addWidget(self.input_text)
        
        # 选项框
        options_layout = QHBoxLayout()
        
        style_label = QLabel("命名风格:")
        style_label.setFont(QFont("Arial", 11, QFont.Bold))
        options_layout.addWidget(style_label)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["camelCase", "PascalCase", "snake_case", "UPPER_CASE", "kebab-case"])
        self.style_combo.setMinimumWidth(150)
        self.style_combo.setMinimumHeight(30)
        self.style_combo.currentTextChanged.connect(self.translate)
        options_layout.addWidget(self.style_combo)
        
        self.online_checkbox = QCheckBox("使用在线翻译")
        self.online_checkbox.setFont(QFont("Arial", 10))
        self.online_checkbox.stateChanged.connect(self.translate)
        options_layout.addWidget(self.online_checkbox)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # 输出框
        output_label = QLabel("翻译结果:")
        output_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Courier", 11))
        self.output_text.setMinimumHeight(80)
        self.output_text.setMaximumHeight(120)
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(
            "QTextEdit { border: 1px solid #d0d0d0; padding: 5px; }"
        )
        layout.addWidget(self.output_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        buttons_config = [
            ("📋 复制结果", self.copy_result),
            ("🗑️ 清空", self.clear),
            ("➕ 添加自定义词", self.add_custom_term),
            ("📖 查看词典", self.view_dictionary)
        ]
        
        for text, callback in buttons_config:
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 10))
            btn.setMinimumHeight(35)
            btn.setMinimumWidth(120)
            btn.clicked.connect(callback)
            btn.setStyleSheet(
                """QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid #d0d0d0;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }"""
            )
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def get_stylesheet(self):
        """获取样式表"""
        return """
        QMainWindow {
            background-color: white;
        }
        QLabel {
            color: black;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: white;
            color: black;
        }
        QCheckBox {
            color: black;
        }
        """

    def _start_loading(self):
        """显示加载动画"""
        self.loading_frame = 0
        self.output_text.setText("翻译中 .")
        self.loading_timer.start(500)  # 每500ms更新一次

    def _stop_loading(self):
        """停止加载动画"""
        self.loading_timer.stop()

    def _update_loading_animation(self):
        """更新加载动画（在主线程中执行）"""
        frames = ["翻译中 .", "翻译中 ..", "翻译中 ..."]
        self.loading_frame = (self.loading_frame + 1) % 3
        self.output_text.setText(frames[self.loading_frame])

    def translate(self):
        """翻译函数（异步）"""
        text = self.input_text.text().strip()
        if not text:
            self.output_text.clear()
            return
        
        style = self.style_combo.currentText()
        use_online = self.online_checkbox.isChecked()
        
        if not use_online:
            result = self.translator.translate_phrase_advanced(text, style, use_online)
            self.output_text.setText(result)
        else:
            if self.translate_thread and self.translate_thread.is_alive():
                return
            
            self._start_loading()
            
            def translate_task():
                try:
                    result = self.translator.translate_phrase_advanced(text, style, use_online)
                    self.translate_signals.finished.emit(result)
                except Exception as e:
                    self.translate_signals.error.emit(str(e))
            
            self.translate_thread = threading.Thread(target=translate_task, daemon=True)
            self.translate_thread.start()

    def on_translate_finished(self, result):
        """翻译完成回调"""
        self._stop_loading()
        self.output_text.setText(result)

    def on_translate_error(self, error):
        """翻译错误回调"""
        self._stop_loading()
        QMessageBox.critical(self, "错误", f"翻译失败: {error}")

    def copy_result(self):
        """复制结果到剪贴板"""
        result = self.output_text.toPlainText().strip()
        if result and not result.startswith("翻译中"):
            clipboard = QApplication.clipboard()
            clipboard.setText(result)
            QMessageBox.information(self, "成功", "已复制到剪贴板")

    def clear(self):
        """清空输入和输出"""
        self.input_text.clear()
        self.output_text.clear()

    def add_custom_term(self):
        """打开添加自定义术语对话框"""
        dialog = CustomTermDialog(self, self.translator)
        if dialog.exec_():
            self.translate()

    def view_dictionary(self):
        """打开查看词典对话框"""
        dialog = DictionaryDialog(self)
        dialog.exec_()

    def set_icon(self):
        """设置程序图标"""
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))


class CustomTermDialog(QDialog):
    """添加自定义术语对话框"""

    def __init__(self, parent, translator):
        super().__init__(parent)
        self.translator = translator
        self.init_ui()

    def init_ui(self):
        """初始化对话框"""
        self.setWindowTitle("添加自定义术语")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        width = 380
        height = 200
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(x, y, width, height)
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: white; }")
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 中文词
        cn_label = QLabel("中文词:")
        cn_label.setFont(QFont("Arial", 10))
        layout.addWidget(cn_label)
        
        self.cn_input = QLineEdit()
        self.cn_input.setFont(QFont("Arial", 11))
        self.cn_input.setMinimumHeight(30)
        self.cn_input.setStyleSheet("QLineEdit { border: 1px solid #d0d0d0; padding: 5px; }")
        layout.addWidget(self.cn_input)
        
        # 英文词
        en_label = QLabel("英文词:")
        en_label.setFont(QFont("Arial", 10))
        layout.addWidget(en_label)
        
        self.en_input = QLineEdit()
        self.en_input.setFont(QFont("Arial", 11))
        self.en_input.setMinimumHeight(30)
        self.en_input.setStyleSheet("QLineEdit { border: 1px solid #d0d0d0; padding: 5px; }")
        layout.addWidget(self.en_input)
        
        layout.addStretch()
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.setFont(QFont("Arial", 10))
        save_btn.setMinimumHeight(35)
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet(
            """QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #d0d0d0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #f0f0f0; }"""
        )
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFont(QFont("Arial", 10))
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(
            """QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #d0d0d0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #f0f0f0; }"""
        )
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def save(self):
        """保存自定义术语"""
        cn = self.cn_input.text().strip()
        en = self.en_input.text().strip()
        
        if not cn or not en:
            QMessageBox.warning(self, "警告", "请输入中英文词")
            return
        
        self.translator.add_custom_terms({cn: en})
        QMessageBox.information(self, "成功", "自定义术语已添加")
        self.accept()


class DictionaryDialog(QDialog):
    """词典查看对话框"""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化对话框"""
        self.setWindowTitle("词典查看")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        width = 600
        height = 450
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(x, y, width, height)
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: white; }")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title = QLabel("词典查看")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 标签页
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget { background-color: white; }")
        
        # 默认词典标签页
        default_text = QTextEdit()
        default_text.setFont(QFont("Courier", 10))
        default_text.setReadOnly(True)
        default_text.setStyleSheet("QTextEdit { border: 1px solid #d0d0d0; }")
        default_text.setText(self.load_file_content('default.txt'))
        tabs.addTab(default_text, "默认词典 (62个)")
        
        # 用户词典标签页
        user_text = QTextEdit()
        user_text.setFont(QFont("Courier", 10))
        user_text.setReadOnly(True)
        user_text.setStyleSheet("QTextEdit { border: 1px solid #d0d0d0; }")
        user_text.setText(self.load_file_content('user.txt'))
        tabs.addTab(user_text, "用户自定义")
        
        layout.addWidget(tabs)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFont(QFont("Arial", 10))
        close_btn.setMinimumHeight(35)
        close_btn.setMaximumWidth(100)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(
            """QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #d0d0d0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #f0f0f0; }"""
        )
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    @staticmethod
    def load_file_content(filename: str) -> str:
        """加载文件内容"""
        file_path = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content if content.strip() else "(空)"
        except Exception as e:
            return f"加载失败: {e}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = TranslatorGUI()
    gui.show()
    sys.exit(app.exec_())
