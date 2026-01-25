"""
内存去重器
用于同一封邮件内的去重
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem


class MemoryDedup:
    """内存去重器"""

    def __init__(self):
        self._seen_ids: set[str] = set()
        self._seen_urls: set[str] = set()
        self._seen_titles: set[str] = set()

    def is_duplicate(self, item: NewsItem) -> bool:
        """
        检查是否重复

        Args:
            item: 要检查的新闻项

        Returns:
            True 如果是重复的
        """
        # 精确匹配：URL hash
        if item.unique_id in self._seen_ids:
            return True

        # URL 匹配
        normalized_url = self._normalize_url(item.url)
        if normalized_url in self._seen_urls:
            return True

        # 标题模糊匹配
        normalized_title = self._normalize_title(item.title)
        if normalized_title and normalized_title in self._seen_titles:
            return True

        return False

    def mark_seen(self, item: NewsItem):
        """标记为已处理"""
        self._seen_ids.add(item.unique_id)
        self._seen_urls.add(self._normalize_url(item.url))

        normalized_title = self._normalize_title(item.title)
        if normalized_title:
            self._seen_titles.add(normalized_title)

    def filter_duplicates(self, items: list[NewsItem]) -> list[NewsItem]:
        """
        过滤重复项

        Args:
            items: 原始列表

        Returns:
            去重后的列表
        """
        unique_items = []
        for item in items:
            if not self.is_duplicate(item):
                self.mark_seen(item)
                unique_items.append(item)
        return unique_items

    def _normalize_url(self, url: str) -> str:
        """URL 标准化"""
        url = url.lower().strip()
        # 移除常见的追踪参数
        for suffix in ['?ref=', '?utm_', '&ref=', '&utm_']:
            if suffix in url:
                url = url.split(suffix)[0]
        # 移除末尾斜杠
        return url.rstrip('/')

    def _normalize_title(self, title: str) -> str:
        """标题标准化（用于模糊去重）"""
        if not title:
            return ""
        # 转小写，移除常见前缀后缀
        title = title.lower().strip()
        # 移除常见前缀
        for prefix in ['show hn:', 'ask hn:', 'tell hn:', '[p]', '[d]']:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        return title

    def reset(self):
        """重置状态"""
        self._seen_ids.clear()
        self._seen_urls.clear()
        self._seen_titles.clear()

    @property
    def seen_count(self) -> int:
        """已处理的数量"""
        return len(self._seen_ids)
