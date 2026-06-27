# Science.org 爬虫经验总结

## 项目概述
自动化爬取 Science.org 期刊文章，绕过 Cloudflare "managed" 级别验证，提取文章元数据。

## 技术栈
- **Scrapling**: v0.4.9 (StealthyFetcher)
- **Patchright**: v1.60.1 (浏览器后端)
- **Python**: 3.13.5
- **虚拟环境**: `/opt/venv/`

---

## ✅ 成功配置（2026-06-28 实测验证）

### 核心参数
```python
from scrapling.fetchers import StealthyFetcher

fetcher = StealthyFetcher()
response = fetcher.fetch(
    url,
    solve_cloudflare=True,
    timeout=300000,    # 5 分钟超时
    wait=180000,       # 3 分钟等待 Cloudflare ⭐ 关键
    load_dom=True,
    headless=True,
    network_idle=True
)
```

### 实际表现
| 指标 | 数值 |
|------|------|
| 总耗时 | ~7 分钟 (431 秒) |
| Cloudflare 验证 | ~4 分钟 |
| 内容大小 | 684KB |
| 状态码 | 200 |
| Turnstile 级别 | "managed" (最高) |

### 成功日志特征
```
[INFO] Cloudflare captcha is solved
[INFO] Fetched (307) <GET ...> (referer: https://www.google.com/)
[INFO] Fetched (200) <GET ...> (referer: https://www.google.com/)
```

---

## ⚠️ 失败教训

### 1. 等待时间不足
- **失败参数**: `wait=90000ms` (90 秒)
- **表现**: 陷入循环重试，永远无法通过验证
- **日志特征**:
  ```
  [INFO] Cloudflare page didn't disappear after 10s, continuing...
  [INFO] Looks like Cloudflare captcha is still present, solving again
  ```
- **解决**: 增加到 `wait=180000ms` (3 分钟)

### 2. 使用 response.text 而非 response.body
- **问题**: `response.text` 可能返回解码后的不完整内容
- **解决**: 始终使用 `response.body` 获取原始字节
  ```python
  html = response.body.decode('utf-8', errors='ignore')
  ```

### 3. 参数传递给 fetcher.configure() 而非 fetch()
- **错误方式** (v0.4.9 已废弃):
  ```python
  StealthyFetcher.configure(timeout=300000, wait=180000)  # ❌ 不支持这些参数
  ```
- **正确方式**:
  ```python
  fetcher.fetch(url, timeout=300000, wait=180000)  # ✅ 直接传给 fetch()
  ```

### 4. 过早判断失败
- **问题**: 前 2-3 分钟都在验证，不要过早终止
- **解决**: 设置 `timeout=300000ms`，耐心等待 7 分钟

---

## 📋 代码检查清单

### 基础配置
- [ ] Scrapling >= 0.4.9
- [ ] Patchright >= 1.60.1
- [ ] Python >= 3.12
- [ ] 虚拟环境已激活

### Fetcher 参数
- [ ] `solve_cloudflare=True`
- [ ] `timeout=300000` (5 分钟)
- [ ] `wait=180000` (3 分钟) ⭐
- [ ] `load_dom=True`
- [ ] `headless=True`
- [ ] `network_idle=True`

### 内容提取
- [ ] 使用 `response.body` 而非 `response.text`
- [ ] 解码时加 `errors='ignore'`
- [ ] 保存原始 HTML 供调试

### 超时处理
- [ ] 外层 timeout >= 480 秒 (8 分钟)
- [ ] 日志记录关键时间点
- [ ] 失败时保存部分结果

---

## 🔧 调试技巧

### 1. 查看 Cloudflare 验证状态
```python
content = response.body.decode('utf-8', errors='ignore')
if "Just a moment" in content or "Verifying" in content:
    print("❌ 仍被 Cloudflare 拦截")
else:
    print("✅ 成功获取页面")
```

### 2. 保存 HTML 供分析
```python
with open('/tmp/debug_output.html', 'wb') as f:
    f.write(response.body)
```

### 3. 提取关键元数据
```python
import re

# 标题
title = re.search(r'<title[^>]*>([^<]+)</title>', content)

# 作者
authors = re.findall(r'<meta[^>]*name=["\']citation_author["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)

# 摘要
abstract = re.search(r'<meta[^>]*name=["\']dc.Description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)

# DOI
doi = re.search(r'<meta[^>]*name=["\']citation_doi["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
```

### 4. 日志监控
成功标志:
```
[INFO] Cloudflare captcha is solved
[INFO] Fetched (307) <GET ...> (referer: https://www.google.com/)
[INFO] Fetched (200) <GET ...>
```

失败标志 (循环重试):
```
[INFO] Cloudflare page didn't disappear after 10s, continuing...
[INFO] Looks like Cloudflare captcha is still present, solving again
```

---

## 📊 各网站对比

| 网站 | Turnstile 级别 | 等待时间 | 成功率 | 备注 |
|------|---------------|----------|--------|------|
| Cell.com | 低 | ~60 秒 | ✅ 高 | 最容易 |
| Nature.com | 中 | ~90 秒 | ✅ 高 | 适中 |
| Science.org | managed (最高) | ~240 秒 | ✅ 高 | 需要耐心 |

---

## 📚 相关文件

- **成功配置文档**: `/opt/data/literature-scraper/docs/SCIENCE_SUCCESS_CONFIG.md`
- **主脚本**: `/opt/data/scripts/science_article_scraper.py`
- **测试脚本**: `/opt/data/literature-scraper/scripts/test_long_wait.py`
- **日志文件**: `/tmp/science_scraper_test.log`
- **输出示例**: `/tmp/science_success_test.html`

---

## 🔄 版本历史

| 日期 | 变更 | 状态 |
|------|------|------|
| 2026-06-26 | 初始参数 `wait=90000ms` | ❌ 失败 |
| 2026-06-28 | 优化为 `wait=180000ms` | ✅ 成功 |
| 2026-06-28 | 文档化经验教训 | ✅ 完成 |

---

## 💡 最佳实践

1. **耐心等待**: Science.org 需要 7 分钟，不要过早终止
2. **批量处理**: 单篇验证成功后再批量运行
3. **错误处理**: 捕获异常并保存部分结果
4. **日志记录**: 记录关键时间点便于调试
5. **参数隔离**: 不同网站用不同配置
6. **HTML 存档**: 保存原始 HTML 供后续分析

---

*最后更新: 2026-06-28*
*验证状态: ✅ 已实测通过*
