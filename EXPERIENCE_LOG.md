# Science.org 爬取经验记录

## 📅 时间线

### 2026-06-26: 初步探索
- 安装 Scrapling v0.4.9 + Patchright v1.60.1
- 成功绕过 Cloudflare 验证
- 关键发现：使用 `response.body` 而非 `response.text` 获取完整 HTML

**已验证成功**:
- ✅ Cell.com: 427KB 内容，captcha 自动解决
- ✅ Nature.com: 235KB 内容，标题提取成功
- ⏳ Science.org: Turnstile "managed" 级别，需要更长等待

### 2026-06-28: 深度调试 Science.org
**问题**: Scrapling 陷入循环重试，每 10 秒检查一次 Cloudflare 状态

**尝试方案 1**: `wait=90000ms` (90 秒)
- ❌ 失败：仍然循环重试
- 日志特征：`Cloudflare page didn't disappear after 10s, continuing...`

**尝试方案 2**: `wait=180000ms` (3 分钟) + 优化参数
- ✅ 成功：431.8 秒完成抓取，684KB HTML 内容
- 关键参数：`network_idle=True`, `timeout=300000ms`

---

## ✅ 最终成功配置（2026-06-28 验证）

### 核心参数
```python
from scrapling import StealthyFetcher

fetcher = StealthyFetcher()
response = fetcher.fetch(
    url,
    solve_cloudflare=True,     # 开启自动验证
    timeout=300000,            # 5 分钟超时
    wait=180000,               # 3 分钟等待 ⭐ 关键
    load_dom=True,             # 加载 DOM
    headless=True,             # 无头模式
    network_idle=True          # 等待网络空闲 ⭐
)
```

### 实际性能
| 指标 | 数值 |
|------|------|
| 总耗时 | 431.8 秒 (~7 分钟) |
| Cloudflare 验证 | ~4 分钟 |
| 页面加载 | ~1 分钟 |
| 内容大小 | 684KB |
| 状态码 | 200 |
| Turnstile 级别 | "managed" (最高) |

### 成功日志
```
[INFO] Cloudflare captcha is solved
[INFO] Fetched (307) <GET ...> (referer: https://www.google.com/)
[INFO] Fetched (200) <GET ...> (referer: https://www.google.com/)
```

---

## ⚠️ 踩坑记录

### 1. 等待时间不足
- **失败**: `wait=90000ms` (90 秒)
- **表现**: 无限循环重试，永远卡在 Cloudflare
- **日志**: `Cloudflare page didn't disappear after 10s, continuing...`
- **原因**: Science.org Turnstile 是 "managed" 级别 (最高)，需要 3-5 分钟
- **解决**: `wait=180000ms` (3 分钟)

### 2. 使用 `response.text` 而非 `response.body`
- **问题**: `response.text` 可能返回解码后的不完整内容
- **解决**: `html = response.body.decode('utf-8', errors='ignore')`

### 3. 错误使用 `StealthyFetcher.configure()`
- **错误** (v0.4.9 不支持):
  ```python
  StealthyFetcher.configure(timeout=300000, wait=180000)
  ```
- **正确**:
  ```python
  fetcher.fetch(url, timeout=300000, wait=180000)
  ```

### 4. 过早判断失败
- **错误**: 2-3 分钟内没结果就终止
- **正确**: 设置 `timeout=300000ms`，耐心等待 7 分钟
- **监控**: 观察日志是否出现 `Cloudflare captcha is solved`

---

## 📊 各网站对比

| 网站 | Turnstile 级别 | 等待时间 | 总耗时 | 成功率 | 难度 |
|------|---------------|----------|--------|--------|------|
| Cell.com | 低 | ~60 秒 | ~2 分钟 | ✅ 高 | ⭐ 容易 |
| Nature.com | 中 | ~90 秒 | ~3 分钟 | ✅ 高 | ⭐⭐ 中等 |
| Science.org | managed (最高) | ~240 秒 | ~7 分钟 | ✅ 高 | ⭐⭐⭐⭐⭐ 困难 |

---

## 🛠️ 调试技巧

### 1. 判断是否成功
```python
content = response.body.decode('utf-8', errors='ignore')
if "Just a moment" in content or "Verifying" in content:
    print("❌ 仍被 Cloudflare 拦截")
else:
    print("✅ 成功获取页面")
```

### 2. 保存调试 HTML
```python
with open('/tmp/debug_output.html', 'wb') as f:
    f.write(response.body)
```

### 3. 提取元数据正则
```python
import re

# 标题
title_match = re.search(r'<title[^>]*>([^<]+)</title>', content)

# 作者 (citation_author meta)
authors = re.findall(
    r'<meta[^>]*name=["\']citation_author["\'][^>]*content=["\']([^"\']*)["\']',
    content, re.IGNORECASE
)

# 摘要 (dc.Description meta)
abstract_match = re.search(
    r'<meta[^>]*name=["\']dc\.Description["\'][^>]*content=["\']([^"\']*)["\']',
    content, re.IGNORECASE
)

# DOI
doi_match = re.search(
    r'<meta[^>]*name=["\']citation_doi["\'][^>]*content=["\']([^"\']*)["\']',
    content, re.IGNORECASE
)
```

---

## 📁 项目文件结构
```
/opt/data/
├── scripts/
│   ├── science_article_scraper.py   # 主爬虫脚本 (已更新 wait=180000ms)
│   ├── test_long_wait.py            # 测试脚本 (验证成功)
│   └── science_urls.txt             # 测试 URL 列表
├── literature-scraper/
│   ├── scrapers/
│   │   ├── base.py                  # 基础爬虫类 (已更新参数)
│   │   ├── science.py               # Science 专用爬虫
│   │   └── science_news.py          # Science News 爬虫
│   ├── storage/
│   │   └── database.py              # SQLite 存储
│   ├── reporters/
│   │   ├── daily_report.py          # 日报生成
│   │   └── weekly_report.py         # 周报生成
│   ├── scripts/
│   │   ├── daily_science_report.py  # 日报入口
│   │   └── weekly_science_report.py # 周报入口
│   ├── config/
│   │   ├── settings.yaml            # 主配置
│   │   └── secrets.yaml             # 密钥配置
│   └── docs/
│       ├── SCIENCE_CRAWLER_BEST_PRACTICES.md  # 最佳实践
│       └── SCIENCE_SUCCESS_CONFIG.md          # 成功配置记录
```

---

## 🔑 关键参数速查

| 参数名 | 值 | 说明 |
|--------|-----|------|
| timeout | 300000ms | 5 分钟超时 |
| wait | 180000ms | 3 分钟等待 Cloudflare ⭐ |
| solve_cloudflare | True | 开启自动验证 |
| headless | True | 无头模式 |
| load_dom | True | 加载 DOM 树 |
| network_idle | True | 等待网络空闲 |
| disable_resources | True | 禁用图片/CSS/字体 |

---

## 📝 待办事项

- [x] 验证单篇文章抓取成功
- [ ] 批量测试 5 篇文章 (~35 分钟)
- [ ] 集成到日报系统
- [ ] 测试 Nature.com (预期 3 分钟/篇)
- [ ] 测试 Cell.com (预期 2 分钟/篇)
- [ ] 实现中文翻译 (Baidu/DeepL API)
- [ ] 实现作者背景调研
- [ ] 配置 cron 定时任务 (日报 8AM, 周报 周六 2PM)
- [ ] 端到端测试： scrape → store → translate → report → email

---

*最后更新：2026-06-28*
*验证状态：✅ 单篇实测通过 (431.8 秒，684KB)*
*下一步：批量测试 or 集成日报系统*
