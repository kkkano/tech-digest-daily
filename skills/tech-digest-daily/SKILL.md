---
name: tech-digest-daily
description: Use when the user wants to generate, preview, summarize, or send a lightweight daily technology digest from the tech-digest-daily project; supports CLI, MCP tools, Markdown/JSON output, email delivery, and Feishu webhook card delivery.
---

# Tech Digest Daily

使用这个 skill 操作本地 `tech-digest-daily` 运行时，不要重新推导调用流程。

## 决策树

1. 如果存在名为 `tech_digest_mcp` 的 MCP server，优先调用 MCP tool。
2. 如果 MCP 不可用但可以执行 shell，使用仓库根目录下的 CLI。
3. 如果用户要求推送飞书群，使用飞书 Webhook 发送。
4. 如果用户要本地预览或聊天回复，返回 Markdown。
5. 如果结果要交给其他程序处理，返回 JSON。

## MCP Tools

可用时优先使用这些工具：

- `tech_digest_get_daily_digest`: 生成 Markdown 或 JSON 日报。
- `tech_digest_get_recommendations`: 只返回精选推荐区。
- `tech_digest_send_feishu`: 生成日报并发送飞书卡片。

推荐默认参数：

```text
response_format = "markdown"
limit = 8
enable_ai = true
enable_enrich = true
use_history_dedup = true
```

预览和演示时，如果用户希望无视历史发送记录看到当前内容，可以设置 `use_history_dedup=false`。

## CLI Commands

从仓库根目录运行：

```bash
python src/cli.py run --format markdown --limit 8
python src/cli.py run --format json --limit 8
python src/cli.py preview --limit 5
python src/cli.py send email
python src/cli.py send feishu --limit 5
```

按需使用这些参数：

- `--no-ai`: 避免调用 LLM。
- `--no-enrich`: 跳过 GitHub README 等深度补充，提升预览速度。
- `--no-history`: 预览或测试时禁用历史去重。
- `--output PATH`: 把 Markdown/JSON 写入文件，而不是 stdout。

## Environment

按渠道配置：

```text
Email:  TO_EMAIL plus RESEND_API_KEY or SMTP_* variables
Feishu: FEISHU_WEBHOOK_URL, optional FEISHU_SECRET
AI:     LLM_API_KEY, optional LLM_API_URL
GitHub: GITHUB_TOKEN, optional GITHUB_USERNAME
```

不要在用户可见输出中打印 API Key、Webhook URL、飞书签名密钥或完整 LLM Prompt。

## Bot Behavior

聊天回复要保持短：

1. 有 AI 总结时先给总结。
2. 最多展示五条推荐。
3. 保留原文链接。
4. AI 失败时按热度最高内容兜底。
5. 所有数据源失败时，说明需要检查网络、API Key 或数据源配置。

## Failure Handling

- 缺少 `LLM_API_KEY`: 除非用户明确要求 AI，否则继续生成非 AI 日报。
- 缺少 `FEISHU_WEBHOOK_URL`: 请求配置 webhook，或退回 Markdown 输出。
- 历史去重后为空: 说明暂无新内容，并建议预览时使用 `--no-history`。
- MCP 依赖缺失: 使用 `pip install -r requirements-mcp.txt` 安装，或退回 CLI。
