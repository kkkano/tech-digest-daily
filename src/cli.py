"""
Tech Digest Daily CLI。

示例：
  python src/cli.py run --format markdown --limit 8
  python src/cli.py run --format json --limit 8 --output digest.json
  python src/cli.py send feishu --limit 5
"""

import argparse
import sys
from contextlib import redirect_stdout
from pathlib import Path

from core.logger import logger
from email_sender import send_digest_email
from engine import get_config, mark_digest_sent, run_digest
from feishu_sender import send_digest_feishu
from renderers import render_json, render_markdown


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    """添加生成日报时的通用选项。"""
    parser.add_argument("--limit", type=int, default=None, help="输出或推送的最大条数")
    parser.add_argument("--no-ai", action="store_true", help="禁用 AI 总结")
    parser.add_argument("--no-enrich", action="store_true", help="跳过深度信息补充")
    parser.add_argument("--no-history", action="store_true", help="禁用历史去重")


def _load_config(args: argparse.Namespace) -> dict:
    """读取并应用 CLI 覆盖配置。"""
    config = get_config()
    if getattr(args, "no_ai", False):
        config["enable_ai_summary"] = False
    if getattr(args, "no_history", False):
        config["enable_history_dedup"] = False
    return config


def _generate_digest(args: argparse.Namespace):
    """运行生成流程，并把日志与第三方 print 输出导向 stderr。"""
    config = _load_config(args)
    with redirect_stdout(sys.stderr):
        return run_digest(
            config,
            enrich=not getattr(args, "no_enrich", False),
            summarize=not getattr(args, "no_ai", False),
        )


def _write_output(text: str, output: str | None) -> None:
    """写入文件或 stdout。"""
    if not output:
        print(text, end="")
        return

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"已写入 {path}", file=sys.stderr)


def cmd_run(args: argparse.Namespace) -> int:
    """生成日报并输出 Markdown 或 JSON。"""
    digest = _generate_digest(args)
    if args.format == "json":
        text = render_json(digest, limit=args.limit)
    else:
        text = render_markdown(digest, limit=args.limit)

    _write_output(text, args.output)
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    """生成适合聊天窗口预览的 Markdown。"""
    digest = _generate_digest(args)
    _write_output(render_markdown(digest, limit=args.limit or 5), args.output)
    return 0


def cmd_send(args: argparse.Namespace) -> int:
    """发送日报到指定渠道。"""
    config = _load_config(args)

    with redirect_stdout(sys.stderr):
        digest = run_digest(
            config,
            enrich=not args.no_enrich,
            summarize=not args.no_ai,
        )

        if not digest.has_items:
            print("去重后无新内容，跳过发送", file=sys.stderr)
            return 0

        if args.channel == "email":
            if not config["to_email"]:
                print("未配置 TO_EMAIL", file=sys.stderr)
                return 2
            success = send_digest_email(digest.results, config["to_email"], digest.ai_summary)
        elif args.channel == "feishu":
            webhook_url = args.webhook_url or config["feishu_webhook_url"]
            secret = args.feishu_secret or config["feishu_secret"]
            if not webhook_url:
                print("未配置 FEISHU_WEBHOOK_URL", file=sys.stderr)
                return 2
            success = send_digest_feishu(
                digest,
                webhook_url,
                secret=secret,
                limit=args.limit or 5,
            )
        else:
            print(f"未知发送渠道: {args.channel}", file=sys.stderr)
            return 2

    if success:
        mark_digest_sent(digest)
        print("sent")
        return 0

    print("send failed", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    """创建 CLI 参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="tech-digest",
        description="生成、预览或推送 Tech Digest Daily。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="生成日报并输出")
    run_parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式",
    )
    run_parser.add_argument("--output", help="输出文件路径，默认输出到 stdout")
    _add_common_options(run_parser)
    run_parser.set_defaults(handler=cmd_run)

    preview_parser = subparsers.add_parser("preview", help="生成聊天窗口预览")
    preview_parser.add_argument("--output", help="输出文件路径，默认输出到 stdout")
    _add_common_options(preview_parser)
    preview_parser.set_defaults(handler=cmd_preview)

    send_parser = subparsers.add_parser("send", help="发送日报")
    send_parser.add_argument("channel", choices=["email", "feishu"], help="发送渠道")
    send_parser.add_argument("--webhook-url", help="飞书自定义机器人 Webhook URL")
    send_parser.add_argument("--feishu-secret", help="飞书自定义机器人签名密钥")
    _add_common_options(send_parser)
    send_parser.set_defaults(handler=cmd_send)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 入口。"""
    logger.set_stream(sys.stderr)
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.handler(args)
    except KeyboardInterrupt:
        print("已中断", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
