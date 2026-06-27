# Science 期刊报告系统 - 测试计划

## 测试目标
验证 Science 单刊报告系统的完整功能，进行多轮迭代优化

## 测试轮次

### 第一轮：基础功能测试 (Round 1)
- [ ] 依赖安装验证
- [ ] Latest News 页面抓取
- [ ] 单篇文章解析
- [ ] 作者信息提取
- [ ] 通讯作者识别

### 第二轮：报告生成测试 (Round 2)
- [ ] 每日报告 HTML 生成
- [ ] 每周报告 HTML 生成
- [ ] 邮件发送测试
- [ ] 中文翻译占位符验证

### 第三轮：定时任务测试 (Round 3)
- [ ] Crontab 安装
- [ ] 日志记录验证
- [ ] 错误处理测试
- [ ] 性能基准测试

### 第四轮：集成测试 (Round 4)
- [ ] 端到端流程测试
- [ ] 异常场景处理
- [ ] 边界条件测试
- [ ] 用户验收测试

---

## 测试脚本

```bash
# Round 1: 基础功能
python3 scripts/test_science_scraper.py

# Round 2: 报告生成
python3 scripts/daily_science_report.py --limit 2 --debug

# Round 3: 邮件测试
python3 scripts/daily_science_report.py --limit 1 --send-email

# Round 4: 性能测试
time python3 scripts/daily_science_report.py --limit 5
```

## 通过标准

| 轮次 | 指标 | 目标 |
|------|------|------|
| Round 1 | 抓取成功率 | > 80% |
| Round 2 | 报告完整率 | 100% |
| Round 3 | 邮件送达率 | 100% |
| Round 4 | 端到端耗时 | < 1 小时 (5 篇) |

## 迭代记录

### Iteration 1.0 (初始版本)
- 日期：2026-06-27
- 状态：待测试
- 问题：待发现
