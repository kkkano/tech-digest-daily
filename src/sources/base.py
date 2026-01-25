"""
数据源基类
定义所有数据源必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Optional
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import NewsItem, SourceType, SourceResult


class BaseSource(ABC):
    """数据源抽象基类"""

    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        """返回数据源类型"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """显示名称（用于邮件标题）"""
        pass

    @property
    @abstractmethod
    def icon(self) -> str:
        """图标 emoji"""
        pass

    @property
    def color(self) -> str:
        """主题颜色（用于邮件样式）"""
        return "#333333"

    @property
    def gradient(self) -> str:
        """渐变背景（用于邮件样式）"""
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

    @abstractmethod
    def fetch(self, limit: int = 10) -> SourceResult:
        """
        获取数据

        Args:
            limit: 获取项目数量

        Returns:
            SourceResult 包含获取结果
        """
        pass

    def _create_success_result(self, items: list[NewsItem]) -> SourceResult:
        """创建成功的结果"""
        return SourceResult(
            source=self.source_type,
            items=items,
            success=True
        )

    def _create_error_result(self, error_message: str) -> SourceResult:
        """创建失败的结果"""
        return SourceResult(
            source=self.source_type,
            items=[],
            success=False,
            error_message=error_message
        )
