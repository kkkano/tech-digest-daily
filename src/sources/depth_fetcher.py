"""
深度信息获取器
进入仓库/文章详情页获取更丰富的信息
"""

import requests
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
import re
import os


class DepthFetcher:
    """深度信息获取器"""

    GITHUB_API = "https://api.github.com"

    def __init__(self, github_token: Optional[str] = None):
        """
        初始化

        Args:
            github_token: GitHub Token（提高 API 限额）
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TechDigest/1.0"
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    def enrich_github_item(self, item) -> None:
        """
        丰富 GitHub 项目信息

        Args:
            item: NewsItem 对象（会被原地修改）
        """
        try:
            # 从 URL 提取 owner/repo
            match = re.match(r'https://github\.com/([^/]+)/([^/]+)', item.url)
            if not match:
                return

            owner, repo = match.groups()

            # 并发获取多种信息
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self._get_readme_summary, owner, repo): "readme",
                    executor.submit(self._get_languages, owner, repo): "languages",
                    executor.submit(self._get_recent_commits, owner, repo): "commits",
                }

                for future in as_completed(futures, timeout=10):
                    key = futures[future]
                    try:
                        result = future.result()
                        if key == "readme" and result:
                            item.readme_summary = result
                        elif key == "languages" and result:
                            item.tech_stack = result
                        elif key == "commits" and result:
                            item.recent_activity = result
                    except Exception:
                        pass

        except Exception as e:
            print(f"  ⚠️ 深度获取失败 ({item.title}): {e}")

    def enrich_items_batch(self, items: list, source_type) -> None:
        """
        批量丰富项目信息

        Args:
            items: NewsItem 列表
            source_type: 数据源类型
        """
        from models import SourceType

        if source_type != SourceType.GITHUB:
            return  # 目前只支持 GitHub 深度获取

        print(f"  🔍 正在获取 {len(items)} 个仓库的深度信息...")

        # 只处理前 N 个（避免太慢）
        items_to_enrich = items[:10]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.enrich_github_item, item): item
                for item in items_to_enrich
            }

            done_count = 0
            for future in as_completed(futures, timeout=30):
                done_count += 1
                # 静默处理，不打印每个

        print(f"  ✅ 深度信息获取完成 ({done_count}/{len(items_to_enrich)})")

    def _get_readme_summary(self, owner: str, repo: str) -> Optional[str]:
        """获取 README 摘要"""
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}/readme"

        try:
            response = requests.get(url, headers=self.headers, timeout=8)
            if response.status_code != 200:
                return None

            data = response.json()
            content = data.get("content", "")

            if not content:
                return None

            # Base64 解码
            try:
                readme_text = base64.b64decode(content).decode("utf-8", errors="ignore")
            except:
                return None

            # 提取摘要（取前 500 字符，清理 markdown）
            summary = self._clean_markdown(readme_text)[:500]

            # 如果太短就不返回
            if len(summary) < 50:
                return None

            return summary

        except Exception:
            return None

    def _get_languages(self, owner: str, repo: str) -> list[str]:
        """获取仓库使用的语言"""
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}/languages"

        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code != 200:
                return []

            languages = response.json()
            # 按使用量排序，返回前 5 个
            sorted_langs = sorted(languages.items(), key=lambda x: -x[1])
            return [lang for lang, _ in sorted_langs[:5]]

        except Exception:
            return []

    def _get_recent_commits(self, owner: str, repo: str) -> Optional[str]:
        """获取最近的提交活动摘要"""
        url = f"{self.GITHUB_API}/repos/{owner}/{repo}/commits"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params={"per_page": 5},
                timeout=5
            )
            if response.status_code != 200:
                return None

            commits = response.json()
            if not commits:
                return None

            # 检查最近更新时间
            latest_date = commits[0].get("commit", {}).get("committer", {}).get("date", "")

            # 获取最近几条 commit message
            messages = []
            for commit in commits[:3]:
                msg = commit.get("commit", {}).get("message", "").split("\n")[0][:50]
                if msg:
                    messages.append(msg)

            if messages:
                return f"最近更新: {latest_date[:10]} | " + " / ".join(messages)

            return None

        except Exception:
            return None

    def _clean_markdown(self, text: str) -> str:
        """清理 Markdown 格式，提取纯文本"""
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        # 移除行内代码
        text = re.sub(r'`[^`]+`', '', text)
        # 移除链接，保留文本
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # 移除图片
        text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除标题标记
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        # 移除加粗/斜体
        text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
        text = re.sub(r'_+([^_]+)_+', r'\1', text)
        # 压缩空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()


# 便捷函数
def enrich_results(results: list, github_token: Optional[str] = None) -> None:
    """
    丰富所有数据源结果的深度信息

    Args:
        results: SourceResult 列表
        github_token: GitHub Token
    """
    fetcher = DepthFetcher(github_token)

    for result in results:
        if result.success and result.items:
            fetcher.enrich_items_batch(result.items, result.source)


if __name__ == "__main__":
    # 测试
    from models import NewsItem, SourceType

    item = NewsItem(
        source=SourceType.GITHUB,
        title="microsoft/vscode",
        url="https://github.com/microsoft/vscode",
        description="Visual Studio Code"
    )

    fetcher = DepthFetcher()
    fetcher.enrich_github_item(item)

    print(f"README 摘要: {item.readme_summary[:200] if item.readme_summary else 'N/A'}...")
    print(f"技术栈: {item.tech_stack}")
    print(f"最近活动: {item.recent_activity}")
