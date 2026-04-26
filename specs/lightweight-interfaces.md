# 轻量接口规格

## 目标

保持 Tech Digest Daily 的轻量日报引擎定位，同时把同一份生成结果暴露给 CLI、飞书 Webhook 卡片、Agent Skill 和 stdio MCP Server。

## 范围

### 本次实现

- 从现有抓取、去重、深度补充、AI 总结流程生成一个 `DigestResult`。
- 将日报渲染为 Markdown，供聊天窗口和 CLI 使用。
- 将日报渲染为 JSON，供程序和机器人消费。
- 通过飞书自定义机器人 Webhook 推送交互式卡片。
- 提供一个简洁 skill，告诉 agent 什么时候用 MCP、CLI 或飞书。
- 提供本地 stdio MCP Server，暴露少量工作流工具。
- 文档化飞书应用机器人的交互路径，但不引入 Web 服务框架。

### 本次不做

- Dashboard、数据库、账号系统、订阅管理。
- 长期运行的 HTTP MCP 服务。
- 完整飞书应用事件服务器、OAuth/token 生命周期。
- 重写现有数据源、邮件模板或 AI 总结器内部逻辑。

## 需求

1. CLI 输出
   - `python src/cli.py run --format markdown` 将 Markdown 输出到 stdout。
   - `python src/cli.py run --format json` 将 JSON 输出到 stdout。
   - 日志和第三方 `print` 输出走 stderr，保证 stdout 可被 bot 直接消费。

2. 飞书 Webhook
   - `python src/cli.py send feishu` 推送交互式卡片到 `FEISHU_WEBHOOK_URL`。
   - 设置 `FEISHU_SECRET` 时，payload 包含 `timestamp` 和 `sign`。
   - 缺少 webhook 配置时给出明确错误，不发送请求。

3. Skill 包
   - `skills/tech-digest-daily/SKILL.md` 说明 MCP、CLI、Markdown/JSON、飞书的路由策略。
   - skill 不复制项目源码，不包含 secret。

4. stdio MCP
   - `src/mcp_server.py` 暴露带 `tech_digest_` 前缀的少量工具。
   - server 使用 stdio，普通日志不得写入 stdout。
   - MCP 依赖放在 `requirements-mcp.txt`，不加重默认 GitHub Actions。

5. 飞书应用机器人交互
   - 第一版只文档化应用机器人路径。
   - 运行时契约为 CLI/MCP 优先：事件服务器收到消息后调用 CLI 或 MCP，再回复飞书。

## 设计

```text
sources/* + dedup/* + ai/*
          |
          v
      engine.py
          |
          +--> main.py          -> email
          +--> cli.py           -> markdown/json/email/feishu
          +--> mcp_server.py    -> MCP tools
          +--> feishu_sender.py -> Feishu card webhook
          +--> renderers/*      -> markdown/json
```

`engine.py` 是唯一生成边界，只返回 `DigestResult`，不决定结果发往哪个渠道。输出渠道保持薄适配，避免邮件定时任务和机器人逻辑互相缠绕。

## 外部文档对齐

- MCP 按官方 server 模型实现：工具是可调用动作，resources/prompts 暂不需要。
- 本地 agent 集成优先使用 stdio transport。
- stdio MCP 遵守 stdout 协议边界，普通日志全部写 stderr。
- 飞书 Webhook 按自定义机器人模式发送 JSON payload，使用 `msg_type=interactive` 和消息卡片元素；签名机器人附带 `timestamp/sign`。

参考文档：

- MCP server concepts: https://modelcontextprotocol.io/docs/learn/server-concepts
- MCP transports: https://modelcontextprotocol.io/docs/concepts/transports
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- 飞书自定义机器人: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot?lang=zh-CN

## 文件

- `src/engine.py`: 共享日报生成管线。
- `src/main.py`: 兼容旧 GitHub Actions 邮件入口。
- `src/cli.py`: `run`、`preview`、`send` 命令。
- `src/renderers/markdown.py`: 面向人和 bot 的 Markdown 输出。
- `src/renderers/json_renderer.py`: 面向自动化的 JSON 输出。
- `src/feishu_sender.py`: 飞书 Webhook 卡片构造和发送。
- `src/mcp_server.py`: 可选 stdio MCP Server。
- `requirements-mcp.txt`: 可选 MCP 依赖。
- `skills/tech-digest-daily/SKILL.md`: agent 调用说明。

## 验证

- `python -m compileall src`
- `python src/cli.py --help`
- `python src/cli.py run --format json --limit 1 --no-ai --no-enrich --no-history`
- 安装 MCP 依赖后，用 MCP 客户端或 inspector 运行 `python src/mcp_server.py`。

## 飞书应用机器人路径

飞书应用机器人需要事件回调服务、请求校验、应用凭证、token 刷新和回复 API。为了保持本仓库轻量，第一版不把这些部署逻辑塞进日报引擎。

未来最小服务：

```text
飞书事件回调
  -> 校验请求
  -> 解析用户意图
  -> 调用 `python src/cli.py run --format markdown --limit 5`
  -> 通过飞书 OpenAPI 回复文本或卡片
```

这样日报引擎保持无状态，机器人服务自己负责凭证、重试、回调校验和部署。
