#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试翻译器功能"""

from AdvancedVariableTranslator import AdvancedTranslator
from ChineseVariableTranslator import ChineseVariableTranslator


def test_basic_translator():
    """测试基础翻译器"""
    print("=" * 50)
    print("测试基础翻译器")
    print("=" * 50)
    
    translator = ChineseVariableTranslator()
    
    # 测试从文件加载的词典
    print("\n1. 词典加载测试:")
    print(f"   词典大小: {len(translator.term_dict)}")
    print(f"   示例词汇: 用户 -> {translator.term_dict.get('用户')}")
    
    # 测试翻译
    print("\n2. 基础翻译测试:")
    test_cases = [
        ('用户信息', 'camelCase'),
        ('用户管理系统', 'snake_case'),
        ('产品分类', 'PascalCase'),
        ('商品列表', 'kebab-case'),
        ('查询结果', 'UPPER_CASE'),
    ]
    
    for text, style in test_cases:
        result = translator.translate_phrase(text, style)
        print(f"   {text:15} -> {style:15} = {result}")
    
    # 测试自定义词汇
    print("\n3. 自定义词汇测试:")
    translator.add_custom_terms({'系统': 'system', '管理': 'management'})
    print(f"   添加自定义词: 系统->system, 管理->management")
    result = translator.translate_phrase('用户管理系统', 'camelCase')
    print(f"   用户管理系统 -> camelCase = {result}")
    
    # 检查文件是否保存
    print("\n4. 文件保存验证:")
    with open('user.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"   user.txt 内容:\n   {content.replace(chr(10), chr(10) + '   ')}")


def test_advanced_translator():
    """测试高级翻译器"""
    print("\n" + "=" * 50)
    print("测试高级翻译器")
    print("=" * 50)
    
    translator = AdvancedTranslator()
    
    print("\n1. API配置加载:")
    print(f"   appid: {translator.appid[:10]}..." if translator.appid else "   appid: 未配置")
    print(f"   key: {translator.key[:10]}..." if translator.key else "   key: 未配置")
    
    print("\n2. 翻译测试:")
    result = translator.translate_phrase_advanced('用户账号', 'camelCase', use_online=False)
    print(f"   用户账号 -> {result}")


if __name__ == '__main__':
    test_basic_translator()
    test_advanced_translator()
    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50)
