"""
邮件发送模块
支持多种免费邮件服务：Resend、Gmail SMTP
支持新的多源邮件模板和旧的单源模板（向后兼容）
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Union
import requests

# 向后兼容：支持旧的 TrendingRepo
try:
    from trending import TrendingRepo
except ImportError:
    TrendingRepo = None

# 新的模板系统
from models import SourceResult, AISummary
from templates.email_template import EmailTemplate


def send_via_resend(to_email: str, subject: str, html_content: str, api_key: str) -> bool:
    """
    使用 Resend API 发送邮件
    免费额度：3000封/月
    """
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "from": "Tech Digest <onboarding@resend.dev>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }

    response = requests.post(url, json=data, headers=headers, timeout=30)
    if response.status_code == 200:
        print(f"✅ 邮件发送成功 (Resend) -> {to_email}")
        return True
    else:
        print(f"❌ 邮件发送失败: {response.text}")
        return False


def send_via_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    from_name: str = "Tech Digest Daily"
) -> bool:
    """
    使用 SMTP 发送邮件
    支持 Gmail、QQ邮箱、163邮箱等
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{smtp_user}>"
        msg["To"] = to_email

        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())

        print(f"✅ 邮件发送成功 (SMTP) -> {to_email}")
        return True

    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False


def send_html_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    发送 HTML 邮件 - 自动选择邮件服务
    优先级：Resend > SMTP
    """
    # 方式1: Resend (推荐)
    resend_api_key = os.environ.get("RESEND_API_KEY")
    if resend_api_key:
        return send_via_resend(to_email, subject, html_content, resend_api_key)

    # 方式2: SMTP
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if smtp_server and smtp_user and smtp_password:
        return send_via_smtp(
            to_email, subject, html_content,
            smtp_server, smtp_port, smtp_user, smtp_password
        )

    print("❌ 未配置邮件服务，请设置 RESEND_API_KEY 或 SMTP 相关环境变量")
    return False


def send_digest_email(
    results: list[SourceResult],
    to_email: str,
    ai_summary: Optional[AISummary] = None
) -> bool:
    """
    发送技术资讯日报邮件（新版多源）

    Args:
        results: 各数据源的结果列表
        to_email: 接收邮箱
        ai_summary: AI 智能总结（可选）

    Returns:
        是否发送成功
    """
    date_str = datetime.now().strftime("%Y年%m月%d日")
    subject = f"🔥 技术资讯日报 - {date_str}"

    # 使用新模板生成 HTML
    template = EmailTemplate()
    html_content = template.generate(results, date_str, ai_summary)

    return send_html_email(to_email, subject, html_content)


# ========== 向后兼容：旧版 API ==========

def generate_html_email(repos: list, date_str: str) -> str:
    """生成精美的 HTML 邮件内容（向后兼容）"""

    projects_html = ""
    for repo in repos:
        lang_badge = f'<span style="background:#3572A5;color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{repo.language}</span>' if repo.language else ""

        stars_today_text = repo.stars_today if repo.stars_today else "N/A"

        projects_html += f'''
        <div style="margin-bottom:24px;border:1px solid #e1e4e8;border-radius:12px;overflow:hidden;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
            <a href="{repo.url}" target="_blank" style="display:block;">
                <img src="{repo.og_image}" alt="{repo.name}" style="width:100%;height:auto;display:block;border-bottom:1px solid #e1e4e8;">
            </a>
            <div style="padding:16px;">
                <div style="display:flex;align-items:center;margin-bottom:8px;">
                    <span style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;font-weight:bold;padding:4px 10px;border-radius:8px;margin-right:10px;">#{repo.rank}</span>
                    <a href="{repo.url}" target="_blank" style="font-size:18px;font-weight:600;color:#0366d6;text-decoration:none;">{repo.name}</a>
                </div>
                <p style="color:#586069;margin:8px 0;line-height:1.6;">{repo.description_cn}</p>
                <div style="display:flex;align-items:center;gap:12px;margin-top:12px;flex-wrap:wrap;">
                    {lang_badge}
                    <span style="color:#586069;">⭐ {repo.stars}</span>
                    <span style="color:#586069;">🍴 {repo.forks}</span>
                    <span style="color:#28a745;font-weight:500;">📈 今日 {stars_today_text}</span>
                </div>
            </div>
        </div>
        '''

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;background-color:#f6f8fa;margin:0;padding:20px;">
        <div style="max-width:680px;margin:0 auto;">
            <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:30px;border-radius:16px 16px 0 0;text-align:center;">
                <h1 style="margin:0 0 8px 0;font-size:28px;">🔥 GitHub 每日趋势</h1>
                <p style="margin:0;opacity:0.9;font-size:16px;">{date_str}</p>
            </div>
            <div style="background:#f6f8fa;padding:24px;border-radius:0 0 16px 16px;">
                <p style="color:#586069;margin-bottom:20px;text-align:center;">
                    今日发现 <strong style="color:#0366d6;">{len(repos)}</strong> 个热门开源项目，让我们一起看看吧！
                </p>
                {projects_html}
                <div style="text-align:center;margin-top:30px;padding-top:20px;border-top:1px solid #e1e4e8;">
                    <p style="color:#959da5;font-size:13px;margin:0;">
                        由 GitHub Trending Daily 自动发送<br>
                        <a href="https://github.com/trending" target="_blank" style="color:#0366d6;">查看更多趋势项目</a>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

    return html


def send_email(repos: list, to_email: str) -> bool:
    """
    发送趋势邮件 - 自动选择邮件服务（向后兼容）
    优先级：Resend > SMTP
    """
    date_str = datetime.now().strftime("%Y年%m月%d日")
    subject = f"🔥 GitHub 每日趋势 - {date_str}"
    html_content = generate_html_email(repos, date_str)

    return send_html_email(to_email, subject, html_content)
