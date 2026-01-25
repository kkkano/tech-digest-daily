"""
翻译模块
使用 Google Translate 免费 API 将文本翻译为中文
"""

import requests
from typing import Optional
import time


def translate_to_chinese(text: str, max_retries: int = 3) -> str:
    """
    将文本翻译为中文

    Args:
        text: 要翻译的文本
        max_retries: 最大重试次数

    Returns:
        翻译后的中文文本，失败则返回原文
    """
    if not text or not text.strip():
        return text

    # 如果已经是中文，直接返回
    if _is_chinese(text):
        return text

    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "auto",  # 自动检测源语言
        "tl": "zh-CN",  # 目标语言：简体中文
        "dt": "t",
        "q": text
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                # 提取翻译结果
                if result and result[0]:
                    translated = "".join(
                        part[0] for part in result[0] if part[0]
                    )
                    return translated
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))  # 递增延迟
                continue
            print(f"翻译失败: {e}")

    return text  # 翻译失败返回原文


def _is_chinese(text: str) -> bool:
    """检查文本是否主要是中文"""
    if not text:
        return False

    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    return chinese_count > len(text) * 0.3


def batch_translate(texts: list[str], delay: float = 0.1) -> list[str]:
    """
    批量翻译文本

    Args:
        texts: 文本列表
        delay: 请求间隔（秒），避免触发频率限制

    Returns:
        翻译后的文本列表
    """
    results = []
    for text in texts:
        results.append(translate_to_chinese(text))
        if delay > 0:
            time.sleep(delay)
    return results


if __name__ == "__main__":
    # 测试
    test_texts = [
        "A lightweight but powerful source code editor",
        "Build software better, together",
        "这是中文文本"
    ]

    for text in test_texts:
        translated = translate_to_chinese(text)
        print(f"原文: {text}")
        print(f"翻译: {translated}")
        print("-" * 50)
