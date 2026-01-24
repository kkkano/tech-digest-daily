# GitHub Trending Daily 📧

每天早上 8 点（北京时间）自动获取 GitHub 热门趋势项目，生成精美的邮件报告发送到你的邮箱。

## ✨ 特性

- 🔥 **每日趋势** - 自动抓取 GitHub Trending 页面
- 🖼️ **精美封面** - 包含每个项目的 Open Graph 预览图
- 🌏 **中文简介** - 自动翻译项目描述为中文
- ⏰ **定时发送** - 每天北京时间早上 8 点准时到达
- 🎨 **漂亮邮件** - 精心设计的 HTML 邮件模板
- 🆓 **完全免费** - 使用 GitHub Actions + Resend 免费服务

## 📸 邮件预览

邮件包含：
- 项目排名和名称
- 项目封面图（Open Graph 图片）
- 中文简介描述
- 编程语言标签
- 星标数、Fork 数、今日新增

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角 `Fork` 按钮。

### 2. 获取 Resend API Key（免费）

1. 访问 [resend.com](https://resend.com) 注册账号
2. 进入 Dashboard → API Keys → Create API Key
3. 复制生成的 API Key

### 3. 配置 Secrets

进入你 Fork 的仓库 → Settings → Secrets and variables → Actions → New repository secret

添加以下 Secrets：

| 名称 | 必需 | 说明 |
|------|------|------|
| `TO_EMAIL` | ✅ | 接收邮件的邮箱地址 |
| `RESEND_API_KEY` | ✅ | Resend API Key |

### 4. 启用 Actions

进入 Actions 页面，点击 "I understand my workflows, go ahead and enable them"

### 5. 测试运行

1. 进入 Actions → GitHub Trending Daily
2. 点击 "Run workflow"
3. 可选填写获取数量和语言筛选
4. 点击绿色的 "Run workflow" 按钮

## ⚙️ 配置选项

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TO_EMAIL` | 必填 | 接收邮件的邮箱 |
| `RESEND_API_KEY` | - | Resend API Key |
| `REPO_LIMIT` | 25 | 获取项目数量 |
| `LANGUAGE_FILTER` | 空 | 语言筛选（如 python, typescript） |

### 修改发送时间

编辑 `.github/workflows/daily.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 时间，北京时间 = UTC + 8
```

常用时间设置：
- `'0 0 * * *'` = 北京时间 08:00
- `'0 1 * * *'` = 北京时间 09:00
- `'0 23 * * *'` = 北京时间 07:00

### 使用 SMTP 替代 Resend

如果你更喜欢使用 Gmail/QQ邮箱等 SMTP 服务：

1. 添加以下 Secrets：
   - `SMTP_SERVER`: SMTP 服务器地址
   - `SMTP_PORT`: 端口（通常是 465）
   - `SMTP_USER`: 邮箱账号
   - `SMTP_PASSWORD`: 授权码/应用密码

2. 修改 workflow 文件，取消 SMTP 相关环境变量的注释

常用 SMTP 配置：

| 邮箱 | SMTP 服务器 | 端口 |
|------|-------------|------|
| Gmail | smtp.gmail.com | 465 |
| QQ邮箱 | smtp.qq.com | 465 |
| 163邮箱 | smtp.163.com | 465 |

## 📁 项目结构

```
github-trending-daily/
├── .github/
│   └── workflows/
│       └── daily.yml      # GitHub Actions 工作流
├── src/
│   ├── trending.py        # GitHub Trending 爬取模块
│   ├── email_sender.py    # 邮件发送模块
│   └── main.py            # 主程序
├── requirements.txt       # Python 依赖
└── README.md
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
