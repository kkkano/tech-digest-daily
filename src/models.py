"""
统一数据模型
定义所有数据源共用的数据结构
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum
import hashlib


class SourceType(Enum):
    """数据源类型"""
    GITHUB = "github"
    HACKERNEWS = "hackernews"
    PRODUCTHUNT = "producthunt"
    DEVTO = "devto"


class ContentType(Enum):
    """内容类型 - 用于邮件分类"""
    PROJECT = "project"    # 开源项目（GitHub）
    ARTICLE = "article"    # 文章（HN、Dev.to）
    PRODUCT = "product"    # 产品（Product Hunt）


# 数据源到内容类型的映射
SOURCE_TO_CONTENT = {
    SourceType.GITHUB: ContentType.PROJECT,
    SourceType.HACKERNEWS: ContentType.ARTICLE,
    SourceType.PRODUCTHUNT: ContentType.PRODUCT,
    SourceType.DEVTO: ContentType.ARTICLE,
}

# 内容类型配置
CONTENT_CONFIG = {
    ContentType.PROJECT: {
        "title": "🔧 开源项目",
        "icon": "🔧",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "description": "GitHub 上的热门开源项目"
    },
    ContentType.ARTICLE: {
        "title": "📰 技术文章",
        "icon": "📰",
        "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "description": "来自 Hacker News 和 Dev.to 的热门文章"
    },
    ContentType.PRODUCT: {
        "title": "🚀 新品发布",
        "icon": "🚀",
        "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "description": "Product Hunt 上的最新产品"
    },
}

# 来源显示名称
SOURCE_DISPLAY = {
    SourceType.GITHUB: "GitHub",
    SourceType.HACKERNEWS: "Hacker News",
    SourceType.PRODUCTHUNT: "Product Hunt",
    SourceType.DEVTO: "Dev.to",
}


@dataclass
class NewsItem:
    """统一的资讯项数据模型"""
    # 核心字段
    source: SourceType          # 数据源
    title: str                  # 标题
    url: str                    # 链接
    description: str            # 英文描述

    # 可选字段
    description_cn: str = ""    # 中文描述
    image_url: Optional[str] = None  # 封面图
    score: Optional[int] = None      # 热度分数（stars/points/votes）
    comments: Optional[int] = None   # 评论数
    author: Optional[str] = None     # 作者
    rank: Optional[int] = None       # 排名
    created_at: Optional[datetime] = None

    # 深度信息（从详情页获取）
    readme_summary: Optional[str] = None      # README 摘要
    tech_stack: list[str] = field(default_factory=list)  # 技术栈
    recent_activity: Optional[str] = None     # 最近活动

    # 数据源特有字段
    extra: dict = field(default_factory=dict)

    @property
    def content_type(self) -> ContentType:
        """获取内容类型"""
        return SOURCE_TO_CONTENT.get(self.source, ContentType.ARTICLE)

    @property
    def source_display(self) -> str:
        """获取来源显示名称"""
        return SOURCE_DISPLAY.get(self.source, self.source.value)

    @property
    def unique_id(self) -> str:
        """基于 URL 生成唯一 ID，用于去重"""
        return hashlib.md5(self.url.encode()).hexdigest()[:16]

    def __hash__(self):
        return hash(self.unique_id)

    def __eq__(self, other):
        if not isinstance(other, NewsItem):
            return False
        return self.unique_id == other.unique_id

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "source": self.source.value,
            "content_type": self.content_type.value,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "description_cn": self.description_cn,
            "image_url": self.image_url,
            "score": self.score,
            "comments": self.comments,
            "author": self.author,
            "rank": self.rank,
            "readme_summary": self.readme_summary,
            "tech_stack": self.tech_stack,
            "extra": self.extra
        }


@dataclass
class SourceResult:
    """数据源返回结果"""
    source: SourceType
    items: list[NewsItem]
    success: bool
    error_message: Optional[str] = None

    @property
    def count(self) -> int:
        """返回项目数量"""
        return len(self.items)


@dataclass
class AISummary:
    """AI 智能总结结果"""
    summary: str                    # 今日总结
    recommendations: list[dict]     # 个性化推荐列表
    generated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: dict) -> "AISummary":
        """从字典创建"""
        return cls(
            summary=data.get("summary", ""),
            recommendations=data.get("recommendations", [])
        )


@dataclass
class UserProfile:
    """用户 GitHub 偏好数据"""
    username: str
    starred_repos: list[dict]       # Star 的仓库
    own_repos: list[dict]           # 自己的仓库
    following: list[str]            # 关注的人
    recent_activity: list[dict]     # 最近活动

    def get_interests_summary(self) -> str:
        """生成兴趣摘要，用于 LLM Prompt"""
        # 提取 Star 仓库的语言和主题
        languages = {}
        topics = []

        for repo in self.starred_repos[:30]:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
            topics.extend(repo.get("topics", []))

        # 排序语言
        top_languages = sorted(languages.items(), key=lambda x: -x[1])[:5]

        # 统计主题
        topic_counts = {}
        for t in topics:
            topic_counts[t] = topic_counts.get(t, 0) + 1
        top_topics = sorted(topic_counts.items(), key=lambda x: -x[1])[:10]

        return {
            "top_languages": [lang for lang, _ in top_languages],
            "top_topics": [topic for topic, _ in top_topics],
            "starred_count": len(self.starred_repos),
            "own_repos_count": len(self.own_repos),
            "following_count": len(self.following)
        }
