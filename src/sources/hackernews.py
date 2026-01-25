"""
Hacker News 数据源
使用官方 Firebase API 获取热门文章
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem, SourceType, SourceResult
from sources.base import BaseSource
from translator import translate_to_chinese


class HackerNewsSource(BaseSource):
    """Hacker News 数据源"""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    @property
    def source_type(self) -> SourceType:
        return SourceType.HACKERNEWS

    @property
    def display_name(self) -> str:
        return "Hacker News 热门"

    @property
    def icon(self) -> str:
        return "🔶"

    @property
    def color(self) -> str:
        return "#ff6600"

    @property
    def gradient(self) -> str:
        return "linear-gradient(135deg, #ff6600 0%, #ff8533 100%)"

    def fetch(self, limit: int = 10) -> SourceResult:
        """获取 Hacker News 热门文章"""
        try:
            # 获取 Top Stories ID 列表
            story_ids = self._get_top_story_ids(limit * 2)  # 多获取一些，因为有些可能没有 URL

            # 并发获取文章详情
            items = self._fetch_stories(story_ids, limit)

            return self._create_success_result(items)
        except Exception as e:
            return self._create_error_result(str(e))

    def _get_top_story_ids(self, limit: int) -> list[int]:
        """获取热门文章 ID 列表"""
        url = f"{self.BASE_URL}/topstories.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()[:limit]

    def _fetch_stories(self, story_ids: list[int], limit: int) -> list[NewsItem]:
        """并发获取文章详情"""
        items = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(self._fetch_story, story_id): story_id
                for story_id in story_ids
            }

            for future in as_completed(futures):
                if len(items) >= limit:
                    break

                try:
                    item = future.result()
                    if item:
                        items.append(item)
                except Exception as e:
                    print(f"获取文章失败: {e}")
                    continue

        # 按分数排序并限制数量
        items.sort(key=lambda x: x.score or 0, reverse=True)
        return items[:limit]

    def _fetch_story(self, story_id: int) -> Optional[NewsItem]:
        """获取单篇文章详情"""
        url = f"{self.BASE_URL}/item/{story_id}.json"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            # 只处理有 URL 的 story 类型
            if data.get("type") != "story" or not data.get("url"):
                return None

            title = data.get("title", "")
            story_url = data.get("url", "")
            score = data.get("score", 0)
            comments = data.get("descendants", 0)
            author = data.get("by", "")

            # 翻译标题
            title_cn = translate_to_chinese(title)

            # HN 讨论链接
            hn_url = f"https://news.ycombinator.com/item?id={story_id}"

            return NewsItem(
                source=self.source_type,
                title=title,
                url=story_url,
                description=title,  # HN 没有描述，用标题代替
                description_cn=title_cn,
                score=score,
                comments=comments,
                author=author,
                extra={
                    "hn_id": story_id,
                    "hn_url": hn_url
                }
            )
        except Exception as e:
            print(f"获取文章 {story_id} 失败: {e}")
            return None


if __name__ == "__main__":
    # 测试
    source = HackerNewsSource()
    result = source.fetch(limit=5)

    if result.success:
        print(f"获取到 {result.count} 篇文章")
        for i, item in enumerate(result.items, 1):
            print(f"{i}. {item.title}")
            print(f"   翻译: {item.description_cn}")
            print(f"   分数: {item.score} | 评论: {item.comments}")
            print(f"   链接: {item.url}")
            print()
    else:
        print(f"获取失败: {result.error_message}")
