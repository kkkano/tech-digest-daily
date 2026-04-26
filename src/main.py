"""
Tech Digest Daily 传统入口。

保留 GitHub Actions 里的 `python main.py` 跑法：
生成 digest -> 发送邮件 -> 成功后写入历史去重记录。
"""

import sys

from core.logger import logger
from email_sender import send_digest_email
from engine import get_config, mark_digest_sent, run_digest


def main() -> None:
    """生成并发送技术日报邮件。"""
    config = get_config()

    if not config["to_email"]:
        logger.error("未设置 TO_EMAIL 环境变量")
        sys.exit(1)

    logger.info(f"📧 目标邮箱: {config['to_email']}")

    try:
        digest = run_digest(config)
    except Exception as e:
        logger.fail(f"任务失败: {e}")
        sys.exit(1)

    if not digest.has_items:
        logger.warning("去重后无新内容，跳过发送")
        sys.exit(0)

    logger.section("📨 正在发送邮件...")
    success = send_digest_email(digest.results, config["to_email"], digest.ai_summary)

    if success:
        mark_digest_sent(digest)
        logger.success("任务完成！")
        sys.exit(0)

    logger.fail("任务失败")
    sys.exit(1)


if __name__ == "__main__":
    main()
