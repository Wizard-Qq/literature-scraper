#!/usr/bin/env python3
"""
Science 每日报告 - 主入口脚本

用法:
    python3 scripts/daily_science_report.py [--date YYYY-MM-DD] [--limit N] [--send-email]
"""
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from reporters.daily_report import DailyReportGenerator
from reporters.email_sender import send_email
from config.settings import load_settings
from config.secrets import load_secrets


def main():
    parser = argparse.ArgumentParser(description="生成 Science 每日报告")
    parser.add_argument("--date", type=str, default=None, help="报告日期 (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, default=10, help="抓取文章数量上限")
    parser.add_argument("--send-email", action="store_true", help="发送邮件")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = "DEBUG" if args.debug else "INFO"
    logger.add("/opt/data/literature-scraper/logs/daily_{time}.log", level=log_level)
    logger.info(f"开始生成 Science 每日报告...")
    logger.info(f"日期：{args.date or '今天'}, 限制：{args.limit} 篇")
    
    # 加载配置
    settings = load_settings()
    secrets = load_secrets()
    
    # 生成报告
    generator = DailyReportGenerator()
    report = generator.generate_daily_report(date=args.date, limit=args.limit)
    
    if not report:
        logger.error("报告生成失败")
        sys.exit(1)
    
    logger.info(f"报告生成成功：{report['summary']}")
    logger.info(f"HTML 路径：{report['html_path']}")
    
    # 发送邮件
    if args.send_email:
        logger.info("准备发送邮件...")
        
        # 读取 HTML 内容
        html_path = Path(report['html_path'])
        html_body = html_path.read_text(encoding='utf-8')
        
        # 构建邮件
        subject = f"Science 每日报告 - {report['date']}（{len(report['articles'])} 篇 Latest News）"
        
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
    
    logger.info("每日报告生成完成 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
