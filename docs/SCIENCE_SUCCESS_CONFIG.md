# Science.org 爬取成功配置

## 成功参数（2026-06-28 实测验证）

```python
fetcher.fetch(
    url,
    solve_cloudflare=True,
    timeout=300000,    # 5 分钟超时
    wait=180000,       # 3 分钟等待 Cloudflare
    load_dom=True,
    headless=True,
    network_idle=True
)
```

## 实际表现
- **总耗时**: ~7 分钟（431 秒）
- **Cloudflare 验证**: "managed"级别（最高难度）
- **验证时间**: ~4 分钟解决 captcha
- **最终状态**: 200 OK
- **内容大小**: 684KB 完整 HTML

## 成功日志特征
```
[INFO] Cloudflare captcha is solved
[INFO] Fetched (307) <GET ...> (referer: https://www.google.com/)
[INFO] Fetched (200) <GET ...> (referer: https://www.google.com/)
```

## 提取的元数据
- ✅ 标题：从 `<title>` 标签
- ✅ 摘要：从 `<meta name="dc.Description">`
- ✅ 作者：从 `<meta name="citation_author">`
- ✅ DOI：从 `<meta name="citation_doi">`
- ✅ 日期：从 `<meta name="citation_date">`
- ✅ 全文：5 个以上长段落

## 注意事项
1. 每篇文章需要 5-10 分钟
2. 不要频繁请求（间隔至少 30 秒）
3. 使用 response.body 而非 response.text
4. 日志显示 "managed" 是正常现象，需要耐心等待

## 对比其他期刊
| 网站 | Cloudflare 级别 | 等待时间 | 成功率 |
|------|----------------|----------|--------|
| Cell.com | 低 | ~60 秒 | ✅ 高 |
| Nature.com | 中 | ~90 秒 | ✅ 高 |
| Science.org | managed (最高) | ~240 秒 | ✅ 高（需耐心） |
