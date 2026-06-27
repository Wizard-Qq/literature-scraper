# 文献追踪系统 - 项目重构计划

## 当前问题
1. 脚本分散，缺乏统一管理
2. 配置硬编码，难以维护
3. 缺少日志和错误处理
4. 没有数据持久化
5. 报告内容过于简单

## 重构目标

### 架构设计
```
literature-scraper/
├── config/
│   ├── settings.yaml          # 主配置（API key, 邮箱等）
│   ├── sources.yaml           # 数据源配置（URL, 选择器）
│   └── keywords.yaml          # 关键词追踪配置
├── scrapers/
│   ├── base.py                # 基础爬虫类
│   ├── science.py             # Science.org 爬虫
│   ├── nature.py              # Nature.com 爬虫
│   └── cell.py                # Cell.com 爬虫
├── processors/
│   ├── extractor.py           # 数据提取器
│   ├── filter.py              # 关键词过滤
│   └── dedup.py               # 去重
├── storage/
│   ├── database.py            # SQLite 数据库
│   └── json_store.py          # JSON 存储
├── reporters/
│   ├── daily.py               # 日报生成
│   ├── weekly.py              # 周报生成
│   └── email_sender.py        # 邮件发送
├── scripts/
│   ├── run_daily.py           # 每日任务入口
│   └── run_weekly.py          # 每周任务入口
├── data/                      # 数据文件（git 忽略）
│   ├── articles/
│   └── cache/
├── logs/                      # 日志文件（git 忽略）
└── tests/                     # 测试
```

## 核心功能

1. **统一爬虫接口** - 所有爬虫继承基类
2. **可配置数据源** - YAML 配置驱动
3. **智能去重** - 基于标题/DOI 去重
4. **关键词过滤** - 只保留相关文章
5. **增量更新** - 只抓取新文章
6. **丰富报告** - 包含摘要/关键词/分类

## 依赖管理
- scrapling: Cloudflare bypass
- pyyaml: 配置管理
- loguru: 日志
- pydantic: 数据验证
- sqlite3: 本地数据库

## 下一步
1. 实现基础爬虫类
2. 配置系统
3. 数据库层
4. 报告生成器
5. 定时任务集成
