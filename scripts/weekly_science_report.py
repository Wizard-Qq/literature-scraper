#!/usr/bin/env python3
"""
Science 每周报告 - 主入口脚本

用法:
    python3 scripts/weekly_science_report.py [--week-start YYYY-MM-DD] [--send-email]
"""
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from reporters.weekly_report import WeeklyReportGenerator
from reporters.email_sender import send_email
from config.settings import load_settings
from config.secrets import load_secrets


def get_week_start(date: datetime = None) -> str:
    """获取指定日期所在周的周一"""
    if date is None:
        date = datetime.now()
    monday = date - timedelta(days=date.weekday())
    return monday.strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description="生成 Science 每周报告")
    parser.add_argument("--week-start", type=str, default=None, 
                        help="周起始日期 (YYYY-MM-DD, 默认为本周一)")
    parser.add_argument("--send-email", action="store_true", help="发送邮件")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = "DEBUG" if args.debug else "INFO"
    logger.add("/opt/data/literature-scraper/logs/weekly_{time}.log", level=log_level)
    
    week_start = args.week_start or get_week_start()
    logger.info(f"开始生成 Science 每周报告...")
    logger.info(f"周期：{week_start} 起")
    
    # 加载配置
    settings = load_settings()
    secrets = load_secrets()
    
    # 生成报告
    generator = WeeklyReportGenerator()
    report = generator.generate_weekly_report(week_start=week_start)
    
    if not report:
        logger.error("周报生成失败")
        sys.exit(1)
    
    logger.info(f"周报生成成功：{report['summary_zh']}")
    logger.info(f"总计：{report['total_count']} 篇文章")
    logger.info(f"HTML 路径：{report['html_path']}")
    
    # 发送邮件
    if args.send_email:
        logger.info("准备发送邮件...")
        
        # 读取 HTML 内容
        html_path = Path(report['html_path'])
        html_body = html_path.read_text(encoding='utf-8')
        
        # 构建邮件
        subject = f"Science 每周报告 ({report['week_start']} - {report['week_end']})"
        
        send_email(
            to_email=settings['email']['recipient'],
            subject=subject,
            html_body=html_body,
            smtp_server=settings['smtp']['server'],
            smtp_port=settings['smtp']['port'],
            smtp_user=settings['email']['sender'],
            smtp_password=secrets['email_password']
        )
        
        logger.info(f"邮件已发送至 {settings['email']['recipient']}")
    
    logger.info("每周报告生成完成 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
