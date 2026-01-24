# 🔥 GitHub Trending Daily

<p align="center">
  <img src="https://img.shields.io/badge/GitHub-Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Resend-Email-000000?style=for-the-badge&logo=mail.ru&logoColor=white" alt="Resend">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>📧 每天早上 8 点，自动将 GitHub 热门趋势项目发送到你的邮箱</b>
</p>

<p align="center">
  <a href="#-效果预览">效果预览</a> •
  <a href="#-特性">特性</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#️-配置选项">配置选项</a> •
  <a href="#-常见问题">常见问题</a>
</p>

---

## 📸 效果预览

每天早上你会收到这样一封精美的邮件：

### 邮件内容包含

| 元素 | 说明 |
|------|------|
| 🏆 **项目排名** | 今日 GitHub 趋势排名 |
| 🖼️ **项目封面** | Open Graph 社交预览图，直观了解项目 |
| 📝 **中文简介** | 自动翻译的项目描述，无需翻译器 |
| 💻 **编程语言** | 彩色标签显示项目主要语言 |
| ⭐ **星标统计** | 总星数、Fork 数、今日新增 |
| 🔗 **直达链接** | 点击即可跳转到 GitHub 项目页 |

### 邮件样式

```
┌─────────────────────────────────────────────────┐
│     🔥 GitHub 每日趋势 - 2026年01月24日          │
│         今日发现 25 个热门开源项目               │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │         [项目封面预览图]                   │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │ #1  microsoft/vscode                 │ │  │
│  │  │                                      │ │  │
│  │  │ Visual Studio Code - 一个轻量级但    │ │  │
│  │  │ 功能强大的源代码编辑器               │ │  │
│  │  │                                      │ │  │
│  │  │ TypeScript  ⭐165k  🍴29k  📈+521    │ │  │
│  │  └──────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │         [项目封面预览图]                   │  │
│  │  ┌──────────────────────────────────────┐ │  │
│  │  │ #2  facebook/react                   │ │  │
│  │  │ ...                                  │ │  │
│  └───────────────────────────────────────────┘  │
│                    ...                          │
└─────────────────────────────────────────────────┘
```

---

## ✨ 特性

- 🔥 **每日趋势** - 自动抓取 GitHub Trending 页面最热门项目
- 🖼️ **精美封面** - 每个项目都附带 Open Graph 社交预览图
- 🌏 **中文简介** - 使用 Google 翻译自动将项目描述翻译为中文
- ⏰ **定时发送** - 每天北京时间早上 8 点准时送达
- 🎨 **精美设计** - 响应式 HTML 邮件模板，手机电脑都好看
- 🔢 **自定义数量** - 可配置获取 1-25 个项目
- 🔤 **语言筛选** - 可指定只看某种编程语言的趋势
- 🆓 **完全免费** - GitHub Actions + Resend 全部免费

---

## 🚀 快速开始

只需 **5 分钟**，即可完成部署！

### 📋 前置条件

- 一个 GitHub 账号
- 一个邮箱地址（用于接收趋势邮件）
- 一个 [Resend](https://resend.com) 账号（免费，1分钟注册）

---

### 第一步：Fork 本仓库

1. 点击本页面右上角的 **`Fork`** 按钮
2. 在弹出页面中点击 **`Create fork`**
3. 等待 Fork 完成，你将拥有自己的仓库副本

<details>
<summary>📷 点击查看截图</summary>

> 点击右上角 Fork 按钮，然后确认创建

</details>

---

### 第二步：获取 Resend API Key（免费）

[Resend](https://resend.com) 是一个现代化的邮件发送服务，**免费额度每月 3000 封**，完全够用！

1. 访问 **https://resend.com**
2. 点击 **`Start for free`** 或使用 GitHub 账号直接登录
3. 登录后，点击左侧菜单的 **`API Keys`**
4. 点击 **`Create API Key`** 按钮
5. 输入名称（如 `github-trending`），点击 **`Add`**
6. **⚠️ 重要：立即复制生成的 API Key**（以 `re_` 开头），关闭后无法再次查看！

<details>
<summary>📷 点击查看截图</summary>

```
Resend Dashboard
├── API Keys (点击这里)
│   └── Create API Key
│       ├── Name: github-trending
│       └── Add → 复制生成的 Key
```

</details>

---

### 第三步：配置 GitHub Secrets

Secrets 是 GitHub 安全存储敏感信息的方式，你的 API Key 和邮箱地址会被加密保存。

1. 进入你 Fork 的仓库页面
2. 点击 **`Settings`**（设置）选项卡
3. 在左侧菜单找到 **`Secrets and variables`** → **`Actions`**
4. 点击 **`New repository secret`** 按钮
5. 添加以下两个 Secret：

| Name | Value | 说明 |
|------|-------|------|
| `TO_EMAIL` | `你的邮箱地址` | 接收趋势邮件的邮箱，如 `example@gmail.com` |
| `RESEND_API_KEY` | `re_xxxxxxxx` | 第二步获取的 Resend API Key |

<details>
<summary>📷 详细步骤</summary>

```
Settings → Secrets and variables → Actions → New repository secret

第一个 Secret:
┌─────────────────────────────────┐
│ Name:   TO_EMAIL                │
│ Secret: your-email@example.com  │
│         [Add secret]            │
└─────────────────────────────────┘

第二个 Secret:
┌─────────────────────────────────┐
│ Name:   RESEND_API_KEY          │
│ Secret: re_xxxxxxxxxxxxxxxxxx   │
│         [Add secret]            │
└─────────────────────────────────┘
```

</details>

---

### 第四步：启用 GitHub Actions

Fork 的仓库默认会禁用 Actions，需要手动启用：

1. 点击仓库的 **`Actions`** 选项卡
2. 你会看到一个黄色提示框
3. 点击 **`I understand my workflows, go ahead and enable them`**

---

### 第五步：测试运行 🎉

现在来测试一下是否配置成功！

1. 点击 **`Actions`** 选项卡
2. 在左侧选择 **`GitHub Trending Daily`** 工作流
3. 点击右侧的 **`Run workflow`** 下拉按钮
4. 可选：修改 `获取项目数量`（默认 25）和 `语言筛选`（默认全部）
5. 点击绿色的 **`Run workflow`** 按钮
6. 等待约 30 秒，刷新页面查看运行状态
7. 如果显示 ✅ 绿色对勾，说明成功了！
8. **去检查你的邮箱吧！** 📬

<details>
<summary>⚠️ 如果邮件在垃圾箱</summary>

首次收到邮件可能会被归类到垃圾邮件，请：
1. 在垃圾邮件中找到邮件
2. 标记为"非垃圾邮件"
3. 将发件人添加到联系人

之后的邮件就会正常收到了！

</details>

---

## 🎊 大功告成！

现在每天早上 8 点（北京时间），你都会收到一封精美的 GitHub 趋势邮件！

---

## ⚙️ 配置选项

### 环境变量说明

| 变量 | 必需 | 默认值 | 说明 |
|------|:----:|--------|------|
| `TO_EMAIL` | ✅ | - | 接收邮件的邮箱地址 |
| `RESEND_API_KEY` | ✅ | - | Resend API Key |
| `REPO_LIMIT` | ❌ | `25` | 获取项目数量（1-25） |
| `LANGUAGE_FILTER` | ❌ | 空 | 语言筛选，如 `python`、`typescript` |

### 修改发送时间

编辑 `.github/workflows/daily.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 时间
```

**常用时间对照表：**

| Cron 表达式 | UTC 时间 | 北京时间 |
|-------------|----------|----------|
| `'0 0 * * *'` | 00:00 | **08:00** |
| `'0 1 * * *'` | 01:00 | 09:00 |
| `'0 23 * * *'` | 23:00 | 07:00（次日） |
| `'30 0 * * *'` | 00:30 | 08:30 |

### 筛选特定编程语言

想只看 Python 项目？在手动触发时填写语言，或修改 workflow 默认值：

```yaml
LANGUAGE_FILTER: ${{ github.event.inputs.language || 'python' }}
```

支持的语言：`python`、`javascript`、`typescript`、`go`、`rust`、`java`、`c++` 等

---

## 🔧 使用 SMTP 替代 Resend

如果你更喜欢使用 Gmail/QQ邮箱/163邮箱 等 SMTP 服务：

### 1. 添加 SMTP Secrets

| Name | Value | 示例 |
|------|-------|------|
| `SMTP_SERVER` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口 | `465` |
| `SMTP_USER` | 邮箱账号 | `your@gmail.com` |
| `SMTP_PASSWORD` | 授权码/应用密码 | `xxxx xxxx xxxx xxxx` |

### 2. 修改 workflow 文件

编辑 `.github/workflows/daily.yml`，取消 SMTP 相关行的注释：

```yaml
env:
  TO_EMAIL: ${{ secrets.TO_EMAIL }}
  # RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}  # 注释掉
  SMTP_SERVER: ${{ secrets.SMTP_SERVER }}
  SMTP_PORT: ${{ secrets.SMTP_PORT }}
  SMTP_USER: ${{ secrets.SMTP_USER }}
  SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
```

### 3. 常用 SMTP 配置

| 邮箱服务 | SMTP 服务器 | 端口 | 密码类型 |
|----------|-------------|------|----------|
| Gmail | `smtp.gmail.com` | `465` | [应用专用密码](https://support.google.com/accounts/answer/185833) |
| QQ邮箱 | `smtp.qq.com` | `465` | [授权码](https://service.mail.qq.com/detail/0/75) |
| 163邮箱 | `smtp.163.com` | `465` | [授权码](https://help.mail.163.com/faqDetail.do?code=d7a5dc8471cd0c0e8b4b8f4f8e49998b374173cfe9171305fa1ce630d7f67ac2) |
| Outlook | `smtp.office365.com` | `587` | 账号密码 |

---

## 📁 项目结构

```
github-trending-daily/
├── .github/
│   └── workflows/
│       └── daily.yml          # GitHub Actions 定时任务配置
├── src/
│   ├── trending.py            # GitHub Trending 爬取模块
│   ├── email_sender.py        # 邮件生成和发送模块
│   └── main.py                # 主程序入口
├── requirements.txt           # Python 依赖
└── README.md                  # 本文档
```

---

## ❓ 常见问题

<details>
<summary><b>Q: 没有收到邮件怎么办？</b></summary>

1. **检查垃圾邮件文件夹** - 首次邮件可能被归类为垃圾邮件
2. **检查 Actions 运行状态** - 进入 Actions 页面查看是否有 ❌ 失败
3. **检查 Secrets 配置** - 确保 `TO_EMAIL` 和 `RESEND_API_KEY` 配置正确
4. **查看运行日志** - 点击失败的 workflow run，查看详细错误信息

</details>

<details>
<summary><b>Q: 为什么用 Resend 而不是其他服务？</b></summary>

- ✅ **免费额度充足**：每月 3000 封，完全够用
- ✅ **无需验证域名**：使用 `onboarding@resend.dev` 即可发送
- ✅ **API 简单**：一个 HTTP 请求即可发送
- ✅ **送达率高**：专业邮件服务，不易进垃圾箱

</details>

<details>
<summary><b>Q: 可以发送到多个邮箱吗？</b></summary>

可以！修改 `TO_EMAIL` Secret，用逗号分隔多个邮箱：

```
email1@example.com,email2@example.com
```

然后修改 `src/email_sender.py` 中的发送逻辑即可。

</details>

<details>
<summary><b>Q: 如何修改邮件模板样式？</b></summary>

编辑 `src/email_sender.py` 中的 `generate_html_email` 函数，修改 HTML/CSS 样式即可。

</details>

<details>
<summary><b>Q: GitHub Actions 会产生费用吗？</b></summary>

不会！公开仓库的 GitHub Actions **完全免费**，没有分钟数限制。

</details>

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- 🐛 发现 Bug？[提交 Issue](../../issues/new)
- 💡 有新想法？[参与讨论](../../discussions)
- 🔧 想改进代码？[提交 PR](../../pulls)

---

## 📄 许可证

[MIT License](LICENSE) © 2026

---

<p align="center">
  如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！
</p>

<p align="center">
  Made with ❤️ by <a href="https://github.com/kkkano">kkkano</a>
</p>
