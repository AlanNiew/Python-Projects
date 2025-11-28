import hashlib
import os
import random
import re
from typing import Optional

from ChineseVariableTranslator import ChineseVariableTranslator


class AdvancedTranslator(ChineseVariableTranslator):
    """高级翻译器（支持在线翻译）"""

    def __init__(self, appid: str = None, key: str = None):
        super().__init__()
        self.appid = appid or self._load_config('appid')
        self.key = key or self._load_config('key')

    @staticmethod
    def _load_config(param: str) -> Optional[str]:
        """从配置文件读取参数"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        if not os.path.exists(config_path):
            return None
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith(f'{param}='):
                        return line.split('=', 1)[1].strip()
        except Exception as e:
            print(f'读取配置失败: {e}')
        return None

    def online_translate(self, text: str, from_lang: str = 'zh', to_lang: str = 'en') -> Optional[str]:
        """使用百度翻译API进行在线翻译"""
        if not self.appid or not self.key:
            return None
        try:
            import requests
            salt = random.randint(32768, 65536)
            sign = self.appid + text + str(salt) + self.key
            sign = hashlib.md5(sign.encode('utf-8')).hexdigest()
            url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
            params = {
                'q': text, 'from': from_lang, 'to': to_lang,
                'appid': self.appid, 'salt': salt, 'sign': sign
            }
            response = requests.get(url, params=params, timeout=5)
            result = response.json()
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
        except Exception as e:
            print(f'翻译失败: {e}')
        return None

    def translate_phrase_advanced(self, phrase: str, style: str = 'camelCase', use_online: bool = False) -> str:
        """高级翻译（支持在线翻译）"""
        if not phrase:
            return ''
        words = self.split_chinese_phrase(phrase.strip())
        english_words = []
        # 第一遍：使用本地词典翻译，收集未匹配的中文词
        untranslated_words = []
        word_indices = {}  # 记录未翻译词在结果列表中的位置
        
        for i, word in enumerate(words):
            if re.match(r'[\u4e00-\u9fa5]', word):
                translated = self.translate_term(word)
                if translated == word and use_online:
                    # 词典中未找到，需要在线翻译
                    untranslated_words.append(word)
                    word_indices[len(untranslated_words) - 1] = i
                    english_words.append(None)  # 占位符
                else:
                    english_words.append(translated)
            else:
                english_words.append(word.lower())
        
        # 第二遍：逐个在线翻译所有未匹配的词
        if untranslated_words and use_online:
            # 用于保存新翻译的词对
            new_terms = {}
            # 逐个翻译每个未匹配的词
            for idx, word_idx in word_indices.items():
                word = untranslated_words[idx]
                result = self.online_translate(word)
                if result:
                    # 清理翻译结果，只取第一个单词
                    cleaned_result = re.sub(r'[^a-zA-Z0-9\s]', '', result).strip().lower()
                    # 如果翻译结果包含多个词，只取第一个
                    translated_word = cleaned_result.split()[0] if cleaned_result.split() else word
                    english_words[word_idx] = translated_word
                    # 记录成功翻译的词对
                    new_terms[word] = translated_word
                else:
                    # 翻译失败，使用原词
                    english_words[word_idx] = word
            # 保存新翻译的词到user.txt
            if new_terms:
                self.add_custom_terms(new_terms)
        
        # 过滤掉None值（理论上不应该存在）
        english_words = [w for w in english_words if w is not None]
        
        if style in self.NAMING_STYLES:
            method_name = self.NAMING_STYLES[style]
            return getattr(self, method_name)(english_words)
        return self._to_camel_case(english_words)

if __name__ == '__main__':
    translator = AdvancedTranslator()
    print(translator.online_translate('中文翻译测试', 'zh', 'en'))