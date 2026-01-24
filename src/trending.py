"""
GitHub Trending 爬取模块
获取每日热门项目，包含链接、封面图、简介
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class TrendingRepo:
    """趋势项目数据结构"""
    rank: int
    name: str  # owner/repo
    url: str
    description: str
    description_cn: str  # 中文简介
    language: Optional[str]
    stars: str
    forks: str
    stars_today: str
    og_image: str  # Open Graph 封面图


def get_trending(language: str = "", since: str = "daily", limit: int = 25) -> list[TrendingRepo]:
    """
    获取 GitHub Trending 项目

    Args:
        language: 编程语言筛选，空字符串表示全部
        since: 时间范围 (daily/weekly/monthly)
        limit: 获取数量，默认25

    Returns:
        TrendingRepo 列表
    """
    url = f"https://github.com/trending/{language}?since={since}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    repos = []

    articles = soup.select("article.Box-row")[:limit]

    for rank, article in enumerate(articles, 1):
        # 项目名称和链接
        h2 = article.select_one("h2 a")
        if not h2:
            continue

        repo_path = h2.get("href", "").strip("/")
        repo_url = f"https://github.com/{repo_path}"

        # 描述
        desc_elem = article.select_one("p.col-9")
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        # 编程语言
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        language_name = lang_elem.get_text(strip=True) if lang_elem else None

        # 星标数
        stars_elem = article.select_one("a[href$='/stargazers']")
        stars = stars_elem.get_text(strip=True) if stars_elem else "0"

        # Fork 数
        forks_elem = article.select_one("a[href$='/forks']")
        forks = forks_elem.get_text(strip=True) if forks_elem else "0"

        # 今日新增星标
        stars_today_elem = article.select_one("span.d-inline-block.float-sm-right")
        stars_today = ""
        if stars_today_elem:
            stars_today = stars_today_elem.get_text(strip=True)

        # Open Graph 封面图 URL
        og_image = f"https://opengraph.githubassets.com/1/{repo_path}"

        # 翻译描述为中文
        description_cn = translate_to_chinese(description)

        repos.append(TrendingRepo(
            rank=rank,
            name=repo_path,
            url=repo_url,
            description=description,
            description_cn=description_cn,
            language=language_name,
            stars=stars,
            forks=forks,
            stars_today=stars_today,
            og_image=og_image,
        ))

    return repos


def translate_to_chinese(text: str) -> str:
    """
    使用免费翻译 API 将英文翻译为中文
    使用 Google Translate 免费接口
    """
    if not text:
        return ""

    try:
        # 使用 Google Translate 免费 API
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": text
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result and result[0]:
                translated = "".join([item[0] for item in result[0] if item[0]])
                return translated
    except Exception:
        pass

    return text  # 翻译失败返回原文


def format_number(num_str: str) -> str:
    """格式化数字显示"""
    num_str = num_str.strip().replace(",", "")
    if not num_str:
        return "0"

    # 提取数字部分
    match = re.search(r"[\d.]+", num_str)
    if not match:
        return num_str

    return match.group()


if __name__ == "__main__":
    # 测试
    repos = get_trending(limit=5)
    for repo in repos:
        print(f"#{repo.rank} {repo.name}")
        print(f"  描述: {repo.description_cn}")
        print(f"  语言: {repo.language} | ⭐ {repo.stars} | 今日 +{repo.stars_today}")
        print(f"  封面: {repo.og_image}")
        print()
