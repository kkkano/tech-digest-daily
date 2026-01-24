"""
GitHub Trending Daily - 主程序
每日自动获取 GitHub 趋势并发送邮件
"""

import os
import sys
from datetime import datetime

from trending import get_trending
from email_sender import send_email


def main():
    """主函数"""
    print("=" * 50)
    print(f"🚀 GitHub Trending Daily - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 从环境变量获取配置
    to_email = os.environ.get("TO_EMAIL")
    limit = int(os.environ.get("REPO_LIMIT", "25"))
    language = os.environ.get("LANGUAGE_FILTER", "")

    if not to_email:
        print("❌ 错误：未设置 TO_EMAIL 环境变量")
        sys.exit(1)

    print(f"📧 目标邮箱: {to_email}")
    print(f"📊 获取数量: {limit}")
    print(f"🔤 语言筛选: {language if language else '全部'}")
    print("-" * 50)

    # 获取趋势项目
    print("📡 正在获取 GitHub Trending...")
    try:
        repos = get_trending(language=language, limit=limit)
        print(f"✅ 成功获取 {len(repos)} 个趋势项目")
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        sys.exit(1)

    # 打印项目列表
    print("-" * 50)
    for repo in repos[:5]:  # 只打印前5个
        print(f"  #{repo.rank} {repo.name} ⭐{repo.stars}")
    if len(repos) > 5:
        print(f"  ... 还有 {len(repos) - 5} 个项目")
    print("-" * 50)

    # 发送邮件
    print("📤 正在发送邮件...")
    success = send_email(repos, to_email)

    if success:
        print("=" * 50)
        print("🎉 任务完成！")
        sys.exit(0)
    else:
        print("=" * 50)
        print("😢 任务失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
