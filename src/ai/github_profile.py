"""
GitHub 用户偏好获取
获取用户的 Star、仓库、关注等数据用于个性化推荐
"""

import requests
from typing import Optional
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import UserProfile


class GitHubProfileFetcher:
    """GitHub 用户偏好获取器"""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        """
        初始化

        Args:
            token: GitHub Personal Access Token（可选，用于提高 API 限额）
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "TechDigest/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def get_user_profile(self, username: str) -> UserProfile:
        """
        获取用户完整的偏好数据

        Args:
            username: GitHub 用户名

        Returns:
            UserProfile 对象
        """
        print(f"正在获取 {username} 的 GitHub 偏好数据...")

        starred = self.get_starred_repos(username, limit=50)
        repos = self.get_user_repos(username, limit=30)
        following = self.get_following(username, limit=30)
        activity = self.get_recent_events(username, limit=20)

        return UserProfile(
            username=username,
            starred_repos=starred,
            own_repos=repos,
            following=following,
            recent_activity=activity
        )

    def get_starred_repos(self, username: str, limit: int = 50) -> list[dict]:
        """获取用户 Star 的仓库"""
        url = f"{self.BASE_URL}/users/{username}/starred"
        params = {"per_page": min(limit, 100), "sort": "updated"}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            repos = response.json()

            return [
                {
                    "name": repo.get("full_name", ""),
                    "description": repo.get("description", ""),
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                    "stars": repo.get("stargazers_count", 0),
                    "url": repo.get("html_url", "")
                }
                for repo in repos[:limit]
            ]
        except Exception as e:
            print(f"获取 starred repos 失败: {e}")
            return []

    def get_user_repos(self, username: str, limit: int = 30) -> list[dict]:
        """获取用户自己的仓库"""
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {"per_page": min(limit, 100), "sort": "updated", "type": "owner"}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            repos = response.json()

            return [
                {
                    "name": repo.get("name", ""),
                    "description": repo.get("description", ""),
                    "language": repo.get("language"),
                    "topics": repo.get("topics", []),
                    "stars": repo.get("stargazers_count", 0),
                    "url": repo.get("html_url", "")
                }
                for repo in repos[:limit]
                if not repo.get("fork", False)  # 排除 fork 的仓库
            ]
        except Exception as e:
            print(f"获取 user repos 失败: {e}")
            return []

    def get_following(self, username: str, limit: int = 30) -> list[str]:
        """获取用户关注的人"""
        url = f"{self.BASE_URL}/users/{username}/following"
        params = {"per_page": min(limit, 100)}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            users = response.json()

            return [user.get("login", "") for user in users[:limit]]
        except Exception as e:
            print(f"获取 following 失败: {e}")
            return []

    def get_recent_events(self, username: str, limit: int = 20) -> list[dict]:
        """获取用户最近的活动"""
        url = f"{self.BASE_URL}/users/{username}/events/public"
        params = {"per_page": min(limit, 100)}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            events = response.json()

            return [
                {
                    "type": event.get("type", ""),
                    "repo": event.get("repo", {}).get("name", ""),
                    "created_at": event.get("created_at", "")
                }
                for event in events[:limit]
            ]
        except Exception as e:
            print(f"获取 events 失败: {e}")
            return []


if __name__ == "__main__":
    # 测试
    fetcher = GitHubProfileFetcher()
    profile = fetcher.get_user_profile("kkkano")

    print(f"用户: {profile.username}")
    print(f"Star 数: {len(profile.starred_repos)}")
    print(f"仓库数: {len(profile.own_repos)}")
    print(f"关注数: {len(profile.following)}")

    interests = profile.get_interests_summary()
    print(f"兴趣摘要: {interests}")
