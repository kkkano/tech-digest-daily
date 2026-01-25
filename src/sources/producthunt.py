"""
Product Hunt 数据源
爬取 Product Hunt 获取每日新品
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem, SourceType, SourceResult
from sources.base import BaseSource
from translator import translate_to_chinese


class ProductHuntSource(BaseSource):
    """Product Hunt 数据源"""

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
            html = self._fetch_page()
            items = self._parse_items(html, limit)
            return self._create_success_result(items)
        except Exception as e:
            return self._create_error_result(str(e))

    def _fetch_page(self) -> str:
        """获取页面 HTML"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = requests.get(self.BASE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text

    def _parse_items(self, html: str, limit: int) -> list[NewsItem]:
        """解析 HTML 提取产品信息"""
        soup = BeautifulSoup(html, "html.parser")
        items = []

        # Product Hunt 的页面结构可能会变化，这里尝试多种选择器
        # 方式1: 查找产品卡片
        product_cards = soup.select('[data-test="post-item"]')

        if not product_cards:
            # 方式2: 尝试其他选择器
            product_cards = soup.select('div[class*="styles_item"]')

        if not product_cards:
            # 方式3: 查找所有链接到 /posts/ 的元素
            product_cards = soup.select('a[href^="/posts/"]')

        for rank, card in enumerate(product_cards[:limit], 1):
            try:
                item = self._parse_product(card, rank)
                if item:
                    items.append(item)
            except Exception as e:
                print(f"解析产品 {rank} 失败: {e}")
                continue

        return items

    def _parse_product(self, element, rank: int) -> Optional[NewsItem]:
        """解析单个产品"""
        # 尝试提取产品名称
        name_elem = element.select_one('h3') or element.select_one('[class*="title"]')
        if not name_elem:
            # 如果元素本身是链接，尝试从链接文本获取
            if element.name == 'a':
                name = element.get_text(strip=True)
                href = element.get('href', '')
            else:
                return None
        else:
            name = name_elem.get_text(strip=True)
            href = ""

        if not name:
            return None

        # 获取链接
        if not href:
            link_elem = element.select_one('a[href^="/posts/"]') or element
            href = link_elem.get('href', '') if hasattr(link_elem, 'get') else ''

        if href and not href.startswith('http'):
            url = f"{self.BASE_URL}{href}"
        else:
            url = href or f"{self.BASE_URL}/posts/{name.lower().replace(' ', '-')}"

        # 获取描述
        desc_elem = element.select_one('p') or element.select_one('[class*="tagline"]')
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        # 翻译描述
        description_cn = translate_to_chinese(description) if description else translate_to_chinese(name)

        # 获取投票数
        vote_elem = element.select_one('[class*="vote"]') or element.select_one('button')
        votes = 0
        if vote_elem:
            vote_text = vote_elem.get_text(strip=True)
            vote_match = re.search(r'\d+', vote_text.replace(',', ''))
            if vote_match:
                votes = int(vote_match.group())

        # 获取评论数
        comments = 0
        comment_elem = element.select_one('[class*="comment"]')
        if comment_elem:
            comment_text = comment_elem.get_text(strip=True)
            comment_match = re.search(r'\d+', comment_text)
            if comment_match:
                comments = int(comment_match.group())

        # 获取缩略图
        img_elem = element.select_one('img')
        image_url = img_elem.get('src', '') if img_elem else ""

        return NewsItem(
            source=self.source_type,
            title=name,
            url=url,
            description=description or name,
            description_cn=description_cn,
            image_url=image_url,
            score=votes,
            comments=comments,
            rank=rank,
            extra={}
        )


if __name__ == "__main__":
    # 测试
    source = ProductHuntSource()
    result = source.fetch(limit=5)

    if result.success:
        print(f"获取到 {result.count} 个产品")
        for item in result.items:
            print(f"#{item.rank} {item.title}")
            print(f"  描述: {item.description_cn}")
            print(f"  投票: {item.score} | 评论: {item.comments}")
            print(f"  链接: {item.url}")
            print()
    else:
        print(f"获取失败: {result.error_message}")
