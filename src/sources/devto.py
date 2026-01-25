"""
Dev.to 数据源
使用 Dev.to 公开 API 获取热门文章
"""

import requests
from typing import Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem, SourceType, SourceResult
from sources.base import BaseSource
from translator import translate_to_chinese


class DevToSource(BaseSource):
    """Dev.to 数据源"""

    BASE_URL = "https://dev.to/api/articles"

    @property
    def source_type(self) -> SourceType:
        return SourceType.DEVTO

    @property
    def display_name(self) -> str:
        return "Dev.to 热门文章"

    @property
    def icon(self) -> str:
        return "📝"

    @property
    def color(self) -> str:
        return "#0a0a0a"

    @property
    def gradient(self) -> str:
        return "linear-gradient(135deg, #0a0a0a 0%, #333333 100%)"

    def fetch(self, limit: int = 10, top: int = 1) -> SourceResult:
        """
        获取 Dev.to 热门文章

        Args:
            limit: 获取数量
            top: 时间范围（天数）
        """
        try:
            articles = self._fetch_articles(limit, top)
            items = [self._parse_article(article, rank) for rank, article in enumerate(articles, 1)]
            items = [item for item in items if item]  # 过滤 None
            return self._create_success_result(items)
        except Exception as e:
            return self._create_error_result(str(e))

    def _fetch_articles(self, limit: int, top: int) -> list[dict]:
        """获取文章列表"""
        params = {
            "per_page": limit,
            "top": top  # 过去 N 天最热门
        }

        headers = {
            "User-Agent": "TechDigest/1.0 (github.com/kkkano/github-trending-daily)"
        }

        response = requests.get(self.BASE_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def _parse_article(self, article: dict, rank: int) -> Optional[NewsItem]:
        """解析单篇文章"""
        try:
            title = article.get("title", "")
            url = article.get("url", "")
            description = article.get("description", "")

            if not title or not url:
                return None

            # 翻译标题和描述
            title_cn = translate_to_chinese(title)
            description_cn = translate_to_chinese(description) if description else title_cn

            # 作者
            user = article.get("user", {})
            author = user.get("name", "") or user.get("username", "")

            # 统计数据
            reactions = article.get("positive_reactions_count", 0)
            comments = article.get("comments_count", 0)

            # 封面图
            cover_image = article.get("cover_image", "") or article.get("social_image", "")

            # 发布时间
            published_at = article.get("published_at")
            created_at = None
            if published_at:
                try:
                    created_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except:
                    pass

            # 标签
            tags = article.get("tag_list", [])

            return NewsItem(
                source=self.source_type,
                title=title,
                url=url,
                description=description,
                description_cn=description_cn,
                image_url=cover_image,
                score=reactions,
                comments=comments,
                author=author,
                rank=rank,
                created_at=created_at,
                extra={
                    "title_cn": title_cn,
                    "tags": tags,
                    "reading_time": article.get("reading_time_minutes", 0)
                }
            )
        except Exception as e:
            print(f"解析文章失败: {e}")
            return None


if __name__ == "__main__":
    # 测试
    source = DevToSource()
    result = source.fetch(limit=5)

    if result.success:
        print(f"获取到 {result.count} 篇文章")
        for item in result.items:
            print(f"#{item.rank} {item.title}")
            print(f"   翻译: {item.extra.get('title_cn', '')}")
            print(f"   作者: {item.author}")
            print(f"   反应: {item.score} | 评论: {item.comments}")
            print(f"   标签: {', '.join(item.extra.get('tags', []))}")
            print(f"   链接: {item.url}")
            print()
    else:
        print(f"获取失败: {result.error_message}")
