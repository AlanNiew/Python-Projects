import os
import re
from typing import List, Dict


class ChineseVariableTranslator:
    """中文变量名翻译器"""

    NAMING_STYLES = {
        'snake_case': '_to_snake_case',
        'camelCase': '_to_camel_case',
        'PascalCase': '_to_pascal_case',
        'UPPER_CASE': '_to_upper_case',
        'kebab-case': '_to_kebab_case'
    }

    def __init__(self):
        self.term_dict = {}
        self._load_term_dicts()

    def _load_term_dicts(self):
        """从default.txt和user.txt加载词典"""
        base_dir = os.path.dirname(__file__)
        # 加载默认词典
        default_path = os.path.join(base_dir, 'default.txt')
        if os.path.exists(default_path):
            terms = self._load_dict_file(default_path)
            self.term_dict.update(terms)
        # 加载用户词典（覆盖默认词典）
        user_path = os.path.join(base_dir, 'user.txt')
        if os.path.exists(user_path):
            terms = self._load_dict_file(user_path)
            self.term_dict.update(terms)

    def _load_dict_file(self,file_path: str) -> Dict[str, str]:
        """从文件加载词典"""
        terms = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line:
                        cn, en = line.split('=', 1)
                        terms[cn.strip()] = en.strip()
        except Exception as e:
            print(f'加载词典失败 {file_path}: {e}')
        return terms

    def translate_term(self, chinese_term: str) -> str:
        """翻译单个中文术语"""
        return self.term_dict.get(chinese_term, chinese_term)

    def _to_snake_case(self, words: List[str]) -> str:
        """转换为蛇形命名法"""
        return '_'.join(word.lower() for word in words if word)

    def _to_camel_case(self, words: List[str]) -> str:
        """转换为驼峰命名法"""
        if not words:
            return ''
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    def _to_pascal_case(self, words: List[str]) -> str:
        """转换为帕斯卡命名法"""
        return ''.join(word.capitalize() for word in words)

    def _to_upper_case(self, words: List[str]) -> str:
        """转换为大写命名法"""
        return '_'.join(word.upper() for word in words if word)

    def _to_kebab_case(self, words: List[str]) -> str:
        """转换为短横线命名法"""
        return '-'.join(word.lower() for word in words if word)

    def split_chinese_phrase(self, phrase: str) -> List[str]:
        """拆分中文短语为单词（支持词典优先匹配）"""
        if not phrase:
            return []

        # 移除特殊字符，只保留中文、英文、数字
        cleaned_phrase = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', phrase).strip()

        words = []
        i = 0

        while i < len(cleaned_phrase):
            # 跳过空格
            if cleaned_phrase[i] == ' ':
                i += 1
                continue

            # 优先尝试词典匹配（贪心：从长到短）
            matched = False
            for length in range(min(4, len(cleaned_phrase) - i), 0, -1):
                candidate = cleaned_phrase[i:i + length]
                # 检查候选词是否全为中文且在词典中
                if re.match(r'^[\u4e00-\u9fa5]+$', candidate) and candidate in self.term_dict:
                    words.append(candidate)
                    i += length
                    matched = True
                    break

            if not matched:
                # 如果词典中没有，则使用正则表达式逐个单位匹配
                # 优先匹配英文单词、数字，再匹配单个中文字符
                if re.match(r'[a-zA-Z]', cleaned_phrase[i]):
                    # 匹配连续英文
                    match = re.match(r'[a-zA-Z]+', cleaned_phrase[i:])
                    words.append(match.group())
                    i += len(match.group())
                elif re.match(r'\d', cleaned_phrase[i]):
                    # 匹配连续数字
                    match = re.match(r'\d+', cleaned_phrase[i:])
                    words.append(match.group())
                    i += len(match.group())
                elif re.match(r'[\u4e00-\u9fa5]', cleaned_phrase[i]):
                    # 对于词典中没有的中文，单字符处理
                    words.append(cleaned_phrase[i])
                    i += 1
                else:
                    i += 1

        return words

    def translate_phrase(self, chinese_phrase: str, style: str = 'camelCase') -> str:
        """翻译短语为变量名"""
        if not chinese_phrase or not chinese_phrase.strip():
            return ''
        words = self.split_chinese_phrase(chinese_phrase.strip())
        english_words = []
        for word in words:
            if re.match(r'[\u4e00-\u9fa5]', word):
                translated = self.translate_term(word)
                if translated != word:
                    english_words.append(translated)
                else:
                    english_words.append(word)
            else:
                english_words.append(word.lower())
        if style in self.NAMING_STYLES:
            method_name = self.NAMING_STYLES[style]
            return getattr(self, method_name)(english_words)
        return self._to_camel_case(english_words)

    def batch_translate(self, phrases: List[str], style: str = 'camelCase') -> Dict[str, str]:
        """批量翻译"""
        return {phrase: self.translate_phrase(phrase, style) for phrase in phrases}

    def add_custom_terms(self, custom_terms: Dict[str, str]):
        """添加自定义术语，並存储到user.txt"""
        self.term_dict.update(custom_terms)
        self._save_user_terms(custom_terms)

    def _save_user_terms(self, terms: Dict[str, str]):
        """与user.txt文件中的术语合并，保存到文件"""
        base_dir = os.path.dirname(__file__)
        user_path = os.path.join(base_dir, 'user.txt')
        try:
            # 读取现有的用户词典
            existing = {}
            if os.path.exists(user_path):
                with open(user_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line:
                            cn, en = line.split('=', 1)
                            existing[cn.strip()] = en.strip()
            # 合并新載辛
            existing.update(terms)
            # 写入文件
            with open(user_path, 'w', encoding='utf-8') as f:
                for cn, en in existing.items():
                    f.write(f'{cn}={en}\n')
        except Exception as e:
            print(f'保存自定义词典失败: {e}')
