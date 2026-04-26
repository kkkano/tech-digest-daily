# AGENTS.md

## 架构意图

Tech Digest Daily 是一个轻量技术资讯日报引擎。数据源抓取、去重、深度补充、AI 总结统一收敛到 `engine.py`，邮件、CLI、飞书和 MCP 都只是输出适配器。

## 目录结构

```text
github-trending-daily/
├── src/
│   ├── engine.py              # 生成 DigestResult 的唯一主流程边界
│   ├── main.py                # 兼容 GitHub Actions 的邮件入口
│   ├── cli.py                 # Markdown/JSON 预览与发送命令
│   ├── feishu_sender.py       # 飞书自定义机器人卡片推送
│   ├── mcp_server.py          # 可选 stdio MCP 工具入口
│   ├── renderers/             # 输出渲染层
│   ├── sources/               # GitHub/HN/Product Hunt/Dev.to 数据源
│   ├── dedup/                 # 内存与历史去重
│   ├── ai/                    # LLM 总结与 GitHub 偏好分析
│   ├── templates/             # 邮件 HTML 模板
│   └── core/                  # 日志等基础设施
├── skills/tech-digest-daily/  # 给 agent/bot 使用的 skill 包
├── specs/                     # 轻量功能规格说明
├── data/                      # 历史去重记录
└── .github/workflows/         # GitHub Actions 定时任务
```

## 模块边界

- `engine.py` 只负责生成日报结果，不发送、不渲染、不绑定具体渠道。
- `main.py` 只保留原邮件工作流，避免破坏现有 Actions。
- `cli.py` 只做参数解析和渠道分发；stdout 保持为机器可消费输出，日志走 stderr。
- `mcp_server.py` 只做 MCP 薄封装；stdio 模式严禁向 stdout 写普通日志。
- `feishu_sender.py` 只负责 webhook payload 和发送，不处理飞书应用机器人事件。
- `renderers/` 不抓数据、不发网络请求，只把 `DigestResult` 转成 Markdown 或 JSON。

## 开发规则

- 优先复用 `engine.run_digest()`，不要在新入口里复制抓取/去重/AI 流程。
- 新增输出渠道时先写 renderer/sender，不要改 sources 和 AI 内部逻辑。
- 涉及 secrets 的变量只从环境变量读取，不写入日志、spec、skill 或示例输出。
- MCP 依赖保持可选，放在 `requirements-mcp.txt`，不要让默认 GitHub Actions 变重。
- 架构变更后同步更新本文件和 `specs/` 中对应规格。

## 变更日志

- 2026-04-26: 增加共享 engine、CLI、Markdown/JSON 渲染、飞书 webhook、stdio MCP、agent skill 与轻量规格文档。
