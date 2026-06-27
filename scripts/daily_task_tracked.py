#!/usr/bin/env python3
"""
每日爬取任务 - 集成任务追踪版本

用法:
    python scripts/daily_task_tracked.py --source science --limit 5
"""

import sys
import time
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, '/opt/data/task-monitor')

from task_monitor import start, step, progress, log, complete, get_monitor
from loguru import logger


def run_daily_task_tracked(source: str = "science", limit: int = 5):
    """
    带追踪的每日爬取任务
    
    自动记录：
    - 任务开始/结束
    - 每个步骤的进度
    - 错误日志
    - 最终结果
    """
    
    task_name = f"每日爬取 - {source.upper()}"
    steps_list = [
        '初始化配置',
        '获取文章链接', 
        '爬取文章详情',
        '保存到数据库',
        '生成报告',
        '发送邮件'
    ]
    
    # 开始任务追踪
    start(task_name, steps_list)
    log(f"数据源：{source}", "info")
    log(f"文章限制：{limit}", "info")
    
    try:
        # 导入必要的模块
        step('初始化配置', 0)
        progress(5, '加载配置文件...')
        time.sleep(1)
        
        from config_manager import get_config
        from scrapers.science import ScienceScraper
        from storage.database import Database
        
        config = get_config()
        scraper = ScienceScraper()
        db = Database()
        
        step('获取文章链接', 1)
        log(f'正在获取 {source} 的最新文章...')
        progress(20, '获取链接中...')
        
        urls = scraper.get_latest_urls(limit=limit * 2)
        if not urls:
            raise Exception("未找到文章链接")
        
        log(f'找到 {len(urls)} 个文章链接')
        progress(30, f'找到 {len(urls)} 篇文章')
        
        # 爬取文章
        step('爬取文章详情', 2)
        log('开始爬取文章详情...')
        progress(40, '爬取中...')
        
        result = scraper.crawl(urls[:limit], max_articles=limit)
        
        if not result.success:
            raise Exception(f"爬取失败：{result.errors}")
        
        progress(70, f'成功爬取 {result.article_count} 篇')
        log(f'✅ 爬取成功：{result.article_count} 篇')
        
        # 保存到数据库
        step('保存到数据库', 3)
        log('正在保存文章到数据库...')
        
        saved_count = db.save_articles(result.articles)
        progress(85, f'已保存 {saved_count} 篇新文章')
        log(f'💾 保存完成：{saved_count} 篇')
        
        # 生成报告
        step('生成报告', 4)
        progress(90, '生成每日报告...')
        
        from reporters.email_sender import send_email
        from datetime import datetime
        
        report_content = generate_report(source, result, saved_count)
        
        # 发送邮件
        step('发送邮件', 5)
        log('正在发送报告邮件...')
        progress(95, '邮件发送中...')
        
        subject = f"文献追踪日报 - {source} - {datetime.now().strftime('%Y-%m-%d')}"
        send_email(subject, report_content, report_type="日报")
        
        progress(100, '任务完成')
        complete(True, f'成功爬取 {saved_count} 篇新文章')
        
        logger.success(f"🎉 任务完成！爬取 {saved_count} 篇新文章")
        
    except Exception as e:
        log(f'❌ 错误：{e}', level='error')
        progress(0, f'失败：{e}')
        complete(False, str(e))
        logger.error(f"任务失败：{e}")
        raise


def generate_report(source: str, result, saved_count: int) -> str:
    """生成报告 HTML"""
    from datetime import datetime
    
    html = f"""
    <h3>📊 爬取结果</h3>
    
    <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        <tr style="background: #f5f5f5;">
            <th style="padding: 10px; border: 1px solid #ddd;">指标</th>
            <th style="padding: 10px; border: 1px solid #ddd;">数值</th>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">数据源</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{source}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">爬取文章</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{result.article_count}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">新文章</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{saved_count}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">完成时间</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
        </tr>
    </table>
    
    <h3>📄 最新文章</h3>
    <ul>
    """
    
    for i, article in enumerate(result.articles[:5], 1):
        html += f"""
        <li style="margin-bottom: 8px;">
            <strong>{i}. {article.title}</strong><br>
            <small style="color: #666;">{', '.join(article.authors[:3]) if article.authors else '未知作者'}</small>
        </li>
        """
    
    if len(result.articles) > 5:
        html += f"<li><em>... 还有 {len(result.articles) - 5} 篇</em></li>"
    
    html += """
    </ul>
    """
    
    return html


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='每日爬取任务（带追踪）')
    parser.add_argument('--source', default='science',
                       choices=['science', 'nature', 'cell', 'all'],
                       help='数据源')
    parser.add_argument('--limit', type=int, default=10,
                       help='每个源最大文章数')
    
    args = parser.parse_args()
    
    print(f"🚀 开始任务：{args.source.upper()} (limit={args.limit})")
    run_daily_task_tracked(source=args.source, limit=args.limit)
