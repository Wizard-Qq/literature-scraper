"""
文献追踪系统 - 每日爬取任务入口

用法:
    python scripts/run_daily.py --source all
    python scripts/run_daily.py --source science --limit 20
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime
from loguru import logger

from config_manager import get_config
from scrapers.science import ScienceScraper
from storage.database import Database
from reporters.email_sender import send_email


# 配置日志
logger.remove()
logger.add(
    root_dir / "logs" / "daily_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:HH:mm:ss} | {level} | {message}"
)
logger.add(sys.stdout, level="INFO")


def run_daily_crawl(source: str = "all", limit: int = 10):
    """
    执行每日爬取任务
    
    Args:
        source: 数据源 (science/nature/cell/all)
        limit: 每个源最大文章数
    """
    logger.info(f"🚀 开始每日爬取任务 [{source}]")
    
    config = get_config()
    db = Database()
    
    sources_to_run = []
    if source == "all":
        sources_to_run = ["science", "nature", "cell"]
    else:
        sources_to_run = [source]
    
    total_articles = 0
    
    for source_name in sources_to_run:
        try:
            logger.info(f"\n{'='*50}")
            logger.info(f"爬取源：{source_name}")
            logger.info(f"{'='*50}")
            
            # 获取配置
            source_config = config.sources_config.get(source_name, {})
            if not source_config.get("enabled", True):
                logger.info(f"跳过 {source_name} (未启用)")
                continue
            
            # 初始化爬虫
            if source_name == "science":
                scraper = ScienceScraper(source_config)
            else:
                logger.warning(f"暂不支持 {source_name}，跳过")
                continue
            
            # 获取文章 URL
            urls = scraper.get_latest_urls(limit=limit * 2)
            
            if not urls:
                logger.warning("未找到文章链接")
                continue
            
            # 爬取文章
            result = scraper.crawl(urls, max_articles=limit)
            
            # 保存到数据库
            saved_count = db.save_articles(result.articles)
            total_articles += saved_count
            
            logger.success(f"{source_name}: {saved_count}/{result.article_count} 篇文章已保存")
            
            # 记录错误
            for error in result.errors:
                logger.warning(f"错误：{error}")
            
        except Exception as e:
            logger.error(f"{source_name} 爬取失败：{e}")
    
    logger.info(f"\n{'='*50}")
    logger.success(f"✅ 今日爬取完成：共 {total_articles} 篇新文章")
    logger.info(f"{'='*50}")
    
    # 生成简单报告（TODO: 完善报告内容）
    report_subject = f"文献追踪日报 - {datetime.now().strftime('%Y-%m-%d')}"
    report_content = generate_daily_report(db)
    
    # 发送邮件
    send_email(
        subject=report_subject,
        content=report_content,
        report_type="日报"
    )
    
    db.close()


def generate_daily_report(db: Database) -> str:
    """生成日报 HTML"""
    stats = db.get_stats(days=1)
    new_articles = db.get_new_articles(days=1)
    
    html = f"""
    <h3>📊 今日概览</h3>
    <p>统计时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    
    <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        <tr style="background: #f5f5f5;">
            <th style="padding: 10px; border: 1px solid #ddd;">数据源</th>
            <th style="padding: 10px; border: 1px solid #ddd;">新增文章</th>
        </tr>
    """
    
    for source, data in stats.items():
        html += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">{source}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{data['count']}</td>
        </tr>
        """
    
    html += """</table>
    
    <h3>📄 最新文章</h3>
    <ul>
    """
    
    for article in new_articles[:10]:  # 只显示前 10 篇
        html += f"""
        <li style="margin-bottom: 10px;">
            <strong>{article['title']}</strong><br>
            <small style="color: #666;">{article['source']} | {article['doi']}</small>
        </li>
        """
    
    html += """
    </ul>
    
    <p style="color: #999; font-size: 0.9em;">
        完整数据请查看数据库
    </p>
    """
    
    return html


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行每日文献爬取任务")
    parser.add_argument("--source", default="all", 
                       choices=["science", "nature", "cell", "all"],
                       help="数据源")
    parser.add_argument("--limit", type=int, default=10, 
                       help="每个源最大文章数")
    
    args = parser.parse_args()
    
    run_daily_crawl(source=args.source, limit=args.limit)
