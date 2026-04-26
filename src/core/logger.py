"""
日志系统 - 结构化日志支持
支持控制台彩色输出 + 文件日志
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器"""

    # ANSI 颜色码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'

    # Emoji 图标
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✨',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
    }

    def format(self, record):
        # 添加颜色和图标
        levelname = record.levelname
        icon = self.ICONS.get(levelname, '')
        color = self.COLORS.get(levelname, '')

        # 格式化时间
        time_str = datetime.now().strftime('%H:%M:%S')

        # 构建日志消息
        if color and sys.stdout.isatty():
            # 终端环境，使用颜色
            formatted = f"{color}{time_str}{self.RESET} {icon} {record.getMessage()}"
        else:
            # 非终端环境（如 GitHub Actions），不使用 ANSI 颜色
            formatted = f"[{time_str}] {icon} [{levelname}] {record.getMessage()}"

        return formatted


class PlainFormatter(logging.Formatter):
    """GitHub Actions 友好的纯文本格式化器"""

    ICONS = {
        'DEBUG': '[DEBUG]',
        'INFO': '[INFO]',
        'WARNING': '[WARN]',
        'ERROR': '[ERROR]',
        'CRITICAL': '[CRIT]',
    }

    def format(self, record):
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_tag = self.ICONS.get(record.levelname, '[LOG]')
        return f"{time_str} {level_tag} {record.getMessage()}"


class TechDigestLogger:
    """Tech Digest 专用日志器"""

    def __init__(self, name: str = "TechDigest"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        self._setup_handlers()

    def _setup_handlers(self):
        """设置日志处理器"""
        # 清除现有处理器
        self._logger.handlers.clear()

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # 根据环境选择格式化器
        if sys.stdout.isatty():
            console_handler.setFormatter(ColoredFormatter())
        else:
            console_handler.setFormatter(PlainFormatter())

        self._logger.addHandler(console_handler)

    def set_level(self, level: str):
        """设置日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
        }
        self._logger.setLevel(level_map.get(level.upper(), logging.INFO))

    def set_stream(self, stream):
        """切换日志输出流，用于 CLI/MCP 保持 stdout 干净。"""
        for handler in self._logger.handlers:
            if hasattr(handler, "setStream"):
                handler.setStream(stream)

    # ==================== 基础日志方法 ====================

    def debug(self, msg: str, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    # ==================== 业务日志方法 ====================

    def header(self, title: str):
        """打印标题头"""
        line = "=" * 60
        self._logger.info(line)
        self._logger.info(f"🔥 {title}")
        self._logger.info(line)

    def section(self, title: str):
        """打印分节标题"""
        self._logger.info("-" * 60)
        self._logger.info(title)

    def source_result(self, name: str, success: bool, count: int = 0, error: str = ""):
        """打印数据源获取结果"""
        if success:
            self._logger.info(f"✅ {name}: {count} 条")
        else:
            self._logger.error(f"❌ {name}: {error or '获取失败'}")

    def progress(self, current: int, total: int, message: str = ""):
        """打印进度"""
        percent = (current / total * 100) if total > 0 else 0
        bar_len = 20
        filled = int(bar_len * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        self._logger.info(f"[{bar}] {percent:.0f}% {message}")

    def stats(self, **kwargs):
        """打印统计信息"""
        for key, value in kwargs.items():
            self._logger.info(f"  📊 {key}: {value}")

    def success(self, msg: str):
        """打印成功消息"""
        self._logger.info(f"🎉 {msg}")

    def fail(self, msg: str):
        """打印失败消息"""
        self._logger.error(f"😢 {msg}")

    def ai_thinking(self, title: str, content: str):
        """打印 AI 思考过程"""
        line = "=" * 70
        self._logger.info("")
        self._logger.info(line)
        self._logger.info(f"🧠 {title}")
        self._logger.info(line)
        # 分行打印内容
        for line_content in content.split('\n'):
            self._logger.info(line_content)
        self._logger.info("=" * 70)
        self._logger.info("")


# 全局日志实例
logger = TechDigestLogger()


def setup_logger(level: str = "INFO") -> TechDigestLogger:
    """设置并返回日志器"""
    logger.set_level(level)
    return logger


if __name__ == "__main__":
    # 测试日志系统
    logger.header("Tech Digest Daily - 测试")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告")
    logger.error("这是一条错误")

    logger.section("📡 正在获取数据源...")
    logger.source_result("GitHub Trending", True, 15)
    logger.source_result("Hacker News", True, 10)
    logger.source_result("Product Hunt", False, error="403 Forbidden")

    logger.section("📊 统计信息")
    logger.stats(
        total_items=25,
        github_count=15,
        hn_count=10,
    )

    logger.ai_thinking("AI 思考过程", "这是 AI 正在分析的内容...\n包含多行文本")

    logger.success("任务完成！")
