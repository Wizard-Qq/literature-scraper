# 文献追踪系统 (Literature Scraper)

📚 自动化爬取科学期刊网站（Science, Nature, Cell）并生成每日/每周报告

## 功能特性

- 🔐 绕过 Cloudflare 反爬虫验证
- 📧 自动发送日报和周报邮件
- 📊 追踪"虚拟细胞"、"合成生物学"等关键词
- ⏰ 定时任务，每日/周自动推送

## 快速开始

### 1. 安装依赖

```bash
pip3 install scrapling pyyaml --break-system-packages
playwright install chromium
```

### 2. 配置邮箱

```bash
cp config/email_config.example.yaml config/email_config.yaml
# 编辑 config/email_config.yaml，填写 QQ 邮箱和授权码
```

### 3. 设置定时任务

```bash
crontab config/crontab.txt
```

### 4. 测试邮件发送

```bash
python3 scripts/email_sender.py --type test
```

## 目录结构

```
literature-scraper/
├── config/
│   ├── email_config.example.yaml  # 邮箱配置模板
│   └── crontab.txt                # 定时任务配置
├── scrapers/
│   ├── science_scraper.py
│   ├── nature_scraper.py
│   └── cell_scraper.py
├── scripts/
│   ├── email_sender.py            # 邮件发送脚本
│   └── run_all.py                 # 批量运行脚本
├── output/                         # 爬取结果
├── logs/                           # 日志文件
└── README.md
```

## 配置邮箱

### 获取 QQ 邮箱授权码

1. 登录 [QQ 邮箱网页版](https://mail.qq.com)
2. 点击 **设置** → **账户**
3. 找到 **POP3/SMTP 服务**，点击 **开启**
4. 按提示发送短信验证
5. 获得 16 位授权码（形如 `xxxxxxxxxxxxxxxx`）
6. 填入 `config/email_config.yaml`

## 手动运行

```bash
# 发送测试邮件
python3 scripts/email_sender.py --type test

# 发送日报
python3 scripts/email_sender.py --type daily

# 发送周报
python3 scripts/email_sender.py --type weekly
```

## 查看日志

```bash
# 查看发送日志
tail -f logs/email_daily.log

# 查看爬取日志
tail -f logs/scraping.log
```

## 技术栈

- **爬虫**: Scrapling + Playwright
- **反反爬虫**: Cloudflare bypass
- **定时任务**: Cron
- **邮件发送**: Python smtplib

## 注意事项

- ⚠️ 不要将 `config/email_config.yaml` 提交到 Git
- ⚠️ Science.org 爬取较慢（3-5 分钟/篇），请耐心等待
- ⚠️ 如遇到验证码，脚本会自动重试

## License

MIT License
