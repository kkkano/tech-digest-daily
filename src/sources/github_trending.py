"""
GitHub Trending 数据源
爬取 GitHub Trending 页面获取热门项目
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem, SourceType, SourceResult
from sources.base import BaseSource
from translator import translate_to_chinese


class GitHubTrendingSource(BaseSource):
    """GitHub Trending 数据源"""

    BASE_URL = "https://github.com/trending"

    @property
    def source_type(self) -> SourceType:
        return SourceType.GITHUB

    @property
    def display_name(self) -> str:
        return "GitHub Trending"

    @property
    def icon(self) -> str:
        return "📊"

    @property
    def color(self) -> str:
        return "#24292e"

    @property
    def gradient(self) -> str:
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

    def fetch(self, limit: int = 15, language: str = "", since: str = "daily") -> SourceResult:
        """
        获取 GitHub Trending 项目

        Args:
            limit: 获取数量
            language: 语言筛选
            since: 时间范围 (daily/weekly/monthly)
        """
        try:
            url = self._build_url(language, since)
            html = self._fetch_page(url)
            items = self._parse_items(html, limit)
            return self._create_success_result(items)
        except Exception as e:
            return self._create_error_result(str(e))

    def _build_url(self, language: str, since: str) -> str:
        """构建请求 URL"""
        url = self.BASE_URL
        if language:
            url = f"{url}/{language}"
        url = f"{url}?since={since}"
        return url

    def _fetch_page(self, url: str) -> str:
        """获取页面 HTML"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text

    def _parse_items(self, html: str, limit: int) -> list[NewsItem]:
        """解析 HTML 提取项目信息"""
        soup = BeautifulSoup(html, "html.parser")
        items = []

        articles = soup.select("article.Box-row")[:limit]

        for rank, article in enumerate(articles, 1):
            try:
                item = self._parse_article(article, rank)
                if item:
                    items.append(item)
            except Exception as e:
                print(f"解析项目 {rank} 失败: {e}")
                continue

        return items

    def _parse_article(self, article, rank: int) -> Optional[NewsItem]:
        """解析单个项目"""
        # 项目名称和链接
        name_elem = article.select_one("h2 a")
        if not name_elem:
            return None

        repo_path = name_elem.get("href", "").strip("/")
        name = repo_path.replace("/", " / ").strip()
        url = f"https://github.com/{repo_path}"

        # 描述
        desc_elem = article.select_one("p.col-9")
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        # 翻译描述
        description_cn = translate_to_chinese(description) if description else ""

        # 编程语言
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        language = lang_elem.get_text(strip=True) if lang_elem else ""

        # 星标数
        stars_elem = article.select_one("a[href$='/stargazers']")
        stars = self._format_number(stars_elem.get_text(strip=True)) if stars_elem else "0"

        # Fork 数
        forks_elem = article.select_one("a[href$='/forks']")
        forks = self._format_number(forks_elem.get_text(strip=True)) if forks_elem else "0"

        # 今日新增
        today_elem = article.select_one("span.d-inline-block.float-sm-right")
        stars_today = ""
        if today_elem:
            today_text = today_elem.get_text(strip=True)
            stars_today = today_text.replace("stars today", "").replace("stars this week", "").replace("stars this month", "").strip()

        # 获取 Open Graph 封面图
        og_image = self._get_og_image(url)

        return NewsItem(
            source=self.source_type,
            title=name,
            url=url,
            description=description,
            description_cn=description_cn,
            image_url=og_image,
            score=self._parse_int(stars),
            rank=rank,
            extra={
                "language": language,
                "stars": stars,
                "forks": forks,
                "stars_today": stars_today
            }
        )

    def _format_number(self, num_str: str) -> str:
        """格式化数字字符串"""
        return num_str.replace(",", "").strip()

    def _parse_int(self, num_str: str) -> int:
        """解析数字"""
        try:
            clean = num_str.replace(",", "").replace("k", "000").replace("K", "000")
            return int(float(clean))
        except:
            return 0

    def _get_og_image(self, repo_url: str) -> str:
        """获取仓库的 Open Graph 封面图"""
        try:
            response = requests.get(repo_url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"
            })
            soup = BeautifulSoup(response.text, "html.parser")
            og_image = soup.select_one('meta[property="og:image"]')
            if og_image:
                return og_image.get("content", "")
        except:
            pass

        # 使用 GitHub 默认的社交预览图
        repo_path = repo_url.replace("https://github.com/", "")
        return f"https://opengraph.githubassets.com/1/{repo_path}"


if __name__ == "__main__":
    # 测试
    source = GitHubTrendingSource()
    result = source.fetch(limit=3)

    if result.success:
        print(f"获取到 {result.count} 个项目")
        for item in result.items:
            print(f"#{item.rank} {item.title}")
            print(f"  描述: {item.description_cn}")
            print(f"  Stars: {item.score}")
            print()
    else:
        print(f"获取失败: {result.error_message}")
