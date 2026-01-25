"""
Product Hunt 数据源
使用 RSS Feed 获取每日新品（更稳定）
"""

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from typing import Optional
import sys
import os
import re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem, SourceType, SourceResult
from sources.base import BaseSource
from translator import translate_to_chinese


class ProductHuntSource(BaseSource):
    """Product Hunt 数据源 - 使用 RSS Feed"""

    RSS_URL = "https://www.producthunt.com/feed"
    BASE_URL = "https://www.producthunt.com"

    @property
    def source_type(self) -> SourceType:
        return SourceType.PRODUCTHUNT

    @property
    def display_name(self) -> str:
        return "Product Hunt 新品"

    @property
    def icon(self) -> str:
        return "🚀"

    @property
    def color(self) -> str:
        return "#da552f"

    @property
    def gradient(self) -> str:
        return "linear-gradient(135deg, #da552f 0%, #ff6154 100%)"

    def fetch(self, limit: int = 8) -> SourceResult:
        """获取 Product Hunt 热门产品"""
        try:
            entries = self._fetch_rss()
            items = self._parse_entries(entries, limit)
            return self._create_success_result(items)
        except Exception as e:
            print(f"  ⚠️ Product Hunt 获取失败: {e}")
            return self._create_error_result(str(e))

    def _fetch_rss(self) -> list:
        """获取 RSS Feed"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        response = requests.get(self.RSS_URL, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.text)

        # Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entries = root.findall('atom:entry', ns)
        return entries

    def _parse_entries(self, entries: list, limit: int) -> list[NewsItem]:
        """解析 RSS 条目"""
        items = []

        # Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        # 只获取最近 7 天的产品
        cutoff_date = datetime.now() - timedelta(days=7)

        for rank, entry in enumerate(entries, 1):
            if len(items) >= limit:
                break

            try:
                item = self._parse_entry(entry, ns, rank, cutoff_date)
                if item:
                    items.append(item)
            except Exception as e:
                print(f"  解析产品 {rank} 失败: {e}")
                continue

        return items

    def _parse_entry(self, entry, ns: dict, rank: int, cutoff_date: datetime) -> Optional[NewsItem]:
        """解析单个 RSS 条目"""
        # 获取标题
        title_elem = entry.find('atom:title', ns)
        if title_elem is None or not title_elem.text:
            return None
        title = title_elem.text.strip()

        # 获取链接
        link_elem = entry.find('atom:link', ns)
        url = link_elem.get('href', '') if link_elem is not None else ''
        if not url:
            return None

        # 获取发布时间
        published_elem = entry.find('atom:published', ns)
        if published_elem is not None and published_elem.text:
            try:
                # 解析时间格式: 2026-01-19T17:01:34-08:00
                pub_str = published_elem.text
                # 简单处理时区
                pub_date = datetime.fromisoformat(pub_str.replace('Z', '+00:00'))
                pub_date = pub_date.replace(tzinfo=None)

                # 跳过太旧的产品
                if pub_date < cutoff_date:
                    return None
            except:
                pass

        # 获取内容/描述
        content_elem = entry.find('atom:content', ns)
        description = ""
        if content_elem is not None and content_elem.text:
            # 解析 HTML 内容
            soup = BeautifulSoup(content_elem.text, 'html.parser')

            # 获取第一个 p 标签作为描述
            first_p = soup.find('p')
            if first_p:
                description = first_p.get_text(strip=True)

        # 如果没有描述，用标题
        if not description:
            description = title

        # 翻译描述
        description_cn = translate_to_chinese(description)

        # 获取图片
        image_url = ""
        if content_elem is not None and content_elem.text:
            soup = BeautifulSoup(content_elem.text, 'html.parser')
            img = soup.find('img')
            if img:
                image_url = img.get('src', '')

        return NewsItem(
            source=self.source_type,
            title=title,
            url=url,
            description=description,
            description_cn=description_cn,
            image_url=image_url,
            score=0,  # RSS 没有投票数
            comments=0,
            rank=rank,
            extra={
                "published": published_elem.text if published_elem is not None else ""
            }
        )


if __name__ == "__main__":
    # 测试
    source = ProductHuntSource()
    result = source.fetch(limit=8)

    if result.success:
        print(f"获取到 {result.count} 个产品")
        for item in result.items:
            print(f"#{item.rank} {item.title}")
            print(f"  描述: {item.description_cn}")
            print(f"  链接: {item.url}")
            print()
    else:
        print(f"获取失败: {result.error_message}")
