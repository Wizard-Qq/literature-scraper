# Science 期刊自动报告系统

自动抓取 [Science.org](https://www.science.org) 最新文章，每日/每周发送邮件报告。

## 📋 功能特性

### 每日报告（每天 8:00 AM）
- **Latest News**: 最新科研新闻
- **内容**:
  - 标题 + 中文翻译
  - 作者列表 + 机构信息
  - 摘要 + 中文翻译
  - 通讯作者背景调查（机构 + 研究领域）
  -关键词标签

### 每周报告（每周六 2:00 PM）
- **Commentary**: 评论文章
- **Editorial**: 编辑文章
- **Careers**: 职业发展
- **中文总结**: 本周更新概览

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /opt/data/literature-scraper
./scripts/install.sh
```

这会：
- 创建 Python 虚拟环境
- 安装 scrapling, loguru, pydantic 等依赖
- 配置 crontab 定时任务
- 创建日志目录

### 2. 配置（已完成）

配置文件位于 `config/`:

```yaml
# config/settings.yaml
email:
  sender: "2892335188@qq.com"
  recipient: "2892335188@qq.com"

smtp:
  server: smtp.qq.com
  port: 465

scraping:
  sources:
    - science
  daily_limit: 10
```

```yaml
# config/secrets.yaml (已 gitignore)
email_password: "你的 QQ 邮箱授权码"
github_token: "你的 GitHub PAT"
```

### 3. 手动测试

```bash
# 测试每日报告（3 篇文章，不发送邮件）
cd /opt/data/literature-scraper
/opt/venv/bin/python3 scripts/daily_science_report.py --limit 3 --debug

# 测试每日报告（发送邮件）
/opt/venv/bin/python3 scripts/daily_science_report.py --limit 3 --send-email

# 测试每周报告
/opt/venv/bin/python3 scripts/weekly_science_report.py --send-email
```

---

## 📂 项目结构

```
/opt/data/literature-scraper/
├── scrapers/
│   ├── base.py              # 爬虫基类
│   ├── models.py            # 数据模型
│   ├── science_news.py      # Science Latest News 爬虫
│   └── author_background.py # 作者背景调查
├── reporters/
│   ├── daily_report.py      # 每日报告生成
│   ├── weekly_report.py     # 每周报告生成
│   └── email_sender.py      # 邮件发送
├── scripts/
│   ├── daily_science_report.py   # 每日报告入口
│   ├── weekly_science_report.py  # 每周报告入口
│   └── install.sh                # 安装脚本
├── config/
│   ├── settings.yaml        # 配置（可提交）
│   ├── secrets.yaml         # 密钥（不提交）
│   └── crontab_science.txt  # 定时任务
├── output/                   # 生成的 HTML 报告
├── logs/                     # 日志文件
└── data/                     # SQLite 数据库
```

---

## 🔧 技术细节

### Cloudflare 绕过

Science.org 使用 Cloudflare Turnstile 验证（managed 级别），我们使用：

- **Scrapling v0.4.9** + **Patchright v1.60.1**
- 参数：
  - `timeout: 300000ms` (5 分钟)
  - `wait_time: 90000ms` (90 秒等待)
  - `solve_cloudflare: true`
- 单篇文章耗时：3-5 分钟

### 通讯作者识别策略

1. **页面标注**: 查找 "Correspondence" 或 邮箱（* 符号）
2. **位置规则**: 作者列表最后 2-3 位
3. **背景调查**: 查询机构 + Google Scholar + PubMed

### 翻译方案

当前使用占位符 `translate_to_chinese()`，后续可接入：

- 百度翻译 API
- DeepL API
- 本地 NMT 模型

---

## 📧 邮件模板

### 每日报告示例

```
主题：Science 每日报告 - 2026-06-27（10 篇 Latest News）

内容：
- 文章 1: [标题] + [中文翻译]
  作者：XXX, YYY, ZZZ (通讯)
  机构：Harvard University; MIT; ...
  摘要：[英文] + [中文]
  通讯作者背景：XXX 教授来自 Harvard University，主要从事分子生物学研究...

- 文章 2: ...
```

### 每周报告示例

```
主题：Science 每周报告 (2026-06-23 至 2026-06-29)

内容：
💬 Commentary（评论）- 3 篇
  - 文章 1: ...
  - 文章 2: ...

✏️ Editorial（编辑文章）- 2 篇
  - ...

🎓 Careers（职业发展）- 1 篇
  - ...

本周 Science 更新：评论文章 3 篇；编辑文章 2 篇；职业发展 1 篇。
```

---

## ⏰ 定时任务说明

```bash
# 查看当前 crontab
crontab -l

# 日志位置
tail -f /opt/data/literature-scraper/logs/cron_daily.log
tail -f /opt/data/literature-scraper/logs/cron_weekly.log

# 临时禁用 crontab
crontab -r

# 重新启用
crontab /opt/data/literature-scraper/config/crontab_science.txt
```

---

## 🐛 故障排除

### 问题 1: Cloudflare 验证失败

**现象**: 抓取返回空内容或 403 错误

**解决**:
1. 增加 `wait_time`（当前 90 秒）
2. 使用住宅 IP 代理
3. 降低并发（每次 1 篇）

### 问题 2: 邮件发送失败

**现象**: SMTP connection refused

**检查**:
1. QQ 邮箱授权码是否正确
2. 端口 465 是否开放（SSL）
3. 防火墙设置

```bash
# 测试 SMTP 连接
telnet smtp.qq.com 465
```

### 问题 3: 中文翻译缺失

**现状**: `translate_to_chinese()` 返回 `[待翻译]` 占位符

**解决**: 接入真实翻译 API（百度/DeepL）

---

## 📊 性能估算

| 任务 | 文章数 | 单篇耗时 | 总耗时 |
|------|--------|---------|--------|
| 每日报告 | 10 篇 | 3-5 分钟 | 30-50 分钟 |
| 每周报告 | 30 篇 | 3-5 分钟 | 1.5-2.5 小时 |

**建议**: 每日报告提前到 6:00 AM 开始抓取，确保 8:00 AM 准时发送

---

## 📝 后续扩展

1. **翻译 API 集成**: 百度翻译/DeepL
2. **作者背景增强**: Google Scholar API 接入
3. **PDF 下载**: 自动下载全文 PDF
4. **多期刊支持**: Nature, Cell, PNAS
5. **智能推送**: 根据关键词筛选（virtual cell, synthetic biology）

---

## 📄 许可证

MIT License

## 👥 作者

- 项目发起：生命科学博士生
- 开发维护：Hermes Agent (UGREEN NAS)
