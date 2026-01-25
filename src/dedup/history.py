"""
历史去重器
持久化存储已发送的内容，避免重复推送
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem


class HistoryDedup:
    """历史去重器（持久化）"""

    DEFAULT_RETENTION_DAYS = 30

    def __init__(self, history_file: Optional[str] = None, retention_days: int = DEFAULT_RETENTION_DAYS):
        """
        初始化历史去重器

        Args:
            history_file: 历史数据文件路径
            retention_days: 数据保留天数
        """
        if history_file:
            self.history_file = Path(history_file)
        else:
            # 默认路径：项目根目录/data/history.json
            project_root = Path(__file__).parent.parent.parent
            self.history_file = project_root / "data" / "history.json"

        self.retention_days = retention_days
        self._history = self._load_history()

    def _load_history(self) -> dict:
        """加载历史数据"""
        if not self.history_file.exists():
            return {
                "version": 1,
                "last_updated": None,
                "sent_items": {}
            }

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载历史数据失败: {e}")
            return {
                "version": 1,
                "last_updated": None,
                "sent_items": {}
            }

    def is_sent_before(self, item: NewsItem) -> bool:
        """
        检查是否已发送过

        Args:
            item: 要检查的新闻项

        Returns:
            True 如果已发送过
        """
        return item.unique_id in self._history["sent_items"]

    def mark_sent(self, items: list[NewsItem]):
        """
        标记为已发送

        Args:
            items: 已发送的新闻项列表
        """
        today = datetime.now().strftime("%Y-%m-%d")
        for item in items:
            self._history["sent_items"][item.unique_id] = {
                "date": today,
                "title": item.title[:100],  # 只保存标题前100字符
                "source": item.source.value
            }

    def filter_sent(self, items: list[NewsItem]) -> list[NewsItem]:
        """
        过滤已发送的项目

        Args:
            items: 原始列表

        Returns:
            过滤后的列表（只包含未发送过的）
        """
        return [item for item in items if not self.is_sent_before(item)]

    def cleanup_old(self):
        """清理过期数据"""
        cutoff_date = (datetime.now() - timedelta(days=self.retention_days)).strftime("%Y-%m-%d")

        old_count = len(self._history["sent_items"])

        self._history["sent_items"] = {
            k: v for k, v in self._history["sent_items"].items()
            if isinstance(v, dict) and v.get("date", "2000-01-01") >= cutoff_date
        }

        new_count = len(self._history["sent_items"])
        if old_count > new_count:
            print(f"清理了 {old_count - new_count} 条过期历史记录")

    def save(self):
        """保存到文件"""
        # 清理过期数据
        self.cleanup_old()

        # 确保目录存在
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # 更新时间戳
        self._history["last_updated"] = datetime.now().isoformat()

        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
            print(f"历史数据已保存: {len(self._history['sent_items'])} 条记录")
        except Exception as e:
            print(f"保存历史数据失败: {e}")

    @property
    def total_sent(self) -> int:
        """已发送的总数"""
        return len(self._history["sent_items"])

    def get_stats(self) -> dict:
        """获取统计信息"""
        items = self._history["sent_items"]

        # 按来源统计
        by_source = {}
        for item in items.values():
            if isinstance(item, dict):
                source = item.get("source", "unknown")
                by_source[source] = by_source.get(source, 0) + 1

        # 按日期统计（最近7天）
        by_date = {}
        for item in items.values():
            if isinstance(item, dict):
                date = item.get("date", "unknown")
                by_date[date] = by_date.get(date, 0) + 1

        return {
            "total": len(items),
            "by_source": by_source,
            "by_date": dict(sorted(by_date.items(), reverse=True)[:7])
        }


if __name__ == "__main__":
    # 测试
    dedup = HistoryDedup()
    print(f"历史记录数: {dedup.total_sent}")
    print(f"统计信息: {dedup.get_stats()}")
