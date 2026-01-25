"""
数据源模块
提供各种数据源的爬取功能
"""

from .base import BaseSource
from .github_trending import GitHubTrendingSource
from .hackernews import HackerNewsSource
from .producthunt import ProductHuntSource
from .devto import DevToSource
from .depth_fetcher import DepthFetcher, enrich_results

__all__ = [
    "BaseSource",
    "GitHubTrendingSource",
    "HackerNewsSource",
    "ProductHuntSource",
    "DevToSource",
    "DepthFetcher",
    "enrich_results"
]
