# 文献追踪系统 v2.0

🔬 **自动化文献追踪系统** - 爬取 Science/Nature/Cell 最新论文，每日自动推送

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ 特性

- 🕷️ **智能爬虫** - 绕过 Cloudflare 反爬虫
- 📧 **邮件推送** - 每日/每周自动发送报告
- 🗄️ **数据持久化** - SQLite 数据库存储
- 🔍 **关键词过滤** - 只追踪你关心的领域
- 📊 **统计报表** - 多维度数据分析
- ⚙️ **配置驱动** - YAML 配置，灵活可扩展

---

## 📦 快速开始

### 1. 安装依赖

```bash
cd /opt/data/literature-scraper
pip3 install -r requirements.txt --break-system-packages
playwright install chromium
```

### 2. 配置系统

```bash
# 编辑配置文件
nano config/settings.yaml
nano config/secrets.yaml  # 填写邮箱授权码
```

### 3. 测试运行

```bash
# 测试邮件发送
python3 reporters/email_sender.py test

# 测试 Science 爬虫
python3 -c "from scrapers.science import ScienceScraper; s = ScienceScraper(); urls = s.get_latest_urls(3); print(urls)"

# 运行每日任务
python3 scripts/run_daily.py --source science --limit 5
```

### 4. 设置定时任务

```bash
# 启用 cron 任务
crontab config/crontab.txt

# 查看任务列表
crontab -l
```

---

## 📁 项目结构

```
literature-scraper/
├── config/                  # 配置文件
│   ├── settings.yaml       # 主配置
│   ├── secrets.yaml        # 敏感信息（勿提交）
│   └── crontab.txt         # 定时任务
├── scrapers/               # 爬虫模块
│   ├── base.py            # 基础爬虫类
│   ├── science.py         # Science 爬虫
│   ├── models.py          # 数据模型
│   └── __init__.py
├── storage/                # 数据存储
│   ├── database.py        # SQLite 数据库
│   └── __init__.py
├── reporters/              # 报告生成
│   ├── email_sender.py    # 邮件发送
│   └── __init__.py
├── scripts/                # 入口脚本
│   ├── run_daily.py       # 每日任务
│   └── run_weekly.py      # 每周任务
├── data/                   # 数据目录（git 忽略）
│   ├── articles.db        # SQLite 数据库
│   └── cache/             # 缓存
├── logs/                   # 日志目录（git 忽略）
├── requirements.txt
└── README.md
```

---

## 🔧 配置说明

### 数据源配置 (config/settings.yaml)

```yaml
sources:
  science:
    enabled: true
    timeout: 300000  # 5 分钟超时
    wait_time: 90000  # Cloudflare 等待时间
```

### 关键词过滤

```yaml
keywords:
  must_include:
    - "virtual cell"
    - "synthetic biology"
  exclude:
    - "review"
```

### 邮箱配置

参考 `config/settings.yaml` 和 `config/secrets.yaml`

---

## 📊 使用示例

### 手动爬取

```python
from scrapers.science import ScienceScraper
from storage.database import Database

# 初始化
scraper = ScienceScraper()
db = Database()

# 获取文章
urls = scraper.get_latest_urls(limit=10)
result = scraper.crawl(urls)

# 保存
db.save_articles(result.articles)
```

### 查看数据库

```bash
sqlite3 data/articles.db
SELECT * FROM articles ORDER BY crawled_at DESC LIMIT 10;
```

---

## 🤝 参考项目

架构设计参考：
- [ai-news-digest](https://github.com/) - AI 新闻聚合
- [zotero-arxiv-daily](https://github.com/) - ArXiv 每日推送

---

## 📝 开发计划

- [ ] Nature/Cell 爬虫实现
- [ ] PDF 自动下载
- [ ] AI 摘要生成
- [ ] 微信推送
- [ ] Web 界面

---

## ⚠️ 注意事项

1. **不要提交敏感信息** - `secrets.yaml` 已加入 `.gitignore`
2. **礼貌爬取** - 设置合理的延迟和并发限制
3. **遵守 robots.txt** - 尊重网站的爬虫协议
4. **科学使用** - 避免高频请求导致 IP 被封

---

## 📄 License

MIT License

---

**维护者**: Hermes Agent on UGREEN NAS  
**版本**: v2.0.0  
**最后更新**: 2026-06-27
