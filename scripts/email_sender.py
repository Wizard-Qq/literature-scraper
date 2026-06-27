#!/usr/bin/env python3
"""
文献追踪报告邮件发送器
支持日报和周报两种模式
"""

import smtplib
import yaml
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "email_config.yaml"

def load_config():
    """加载邮箱配置"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"配置文件不存在：{CONFIG_PATH}\n请先复制 config/email_config.example.yaml 为 email_config.yaml 并填写配置")
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def send_email(subject: str, content: str, report_type: str = "日报"):
    """发送邮件"""
    config = load_config()
    smtp_config = config['smtp']
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_config['sender_email']
    msg['To'] = smtp_config['recipient_email']
    msg['Subject'] = f"[{report_type}] {subject} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 添加 HTML 内容
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c5aa0;">{subject}</h2>
        <p style="color: #666; font-size: 0.9em;">发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        {content}
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 0.8em;">
            此邮件由 UGREEN NAS 文献追踪系统自动发送<br>
            如有问题请联系管理员
        </p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    # 发送
    try:
        if smtp_config.get('use_ssl', True):
            server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
        else:
            server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
            server.starttls()
        
        server.login(smtp_config['sender_email'], smtp_config['sender_password'])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 邮件发送成功：{subject}")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

def generate_daily_report():
    """生成日报内容"""
    # TODO: 从爬取日志中汇总数据
    today = datetime.now().strftime('%Y-%m-%d')
    
    content = """
    <h3>📊 今日爬取概览</h3>
    <table style="border-collapse: collapse; width: 100%;">
        <tr style="background: #f5f5f5;">
            <th style="padding: 10px; border: 1px solid #ddd;">网站</th>
            <th style="padding: 10px; border: 1px solid #ddd;">文章数</th>
            <th style="padding: 10px; border: 1px solid #ddd;">状态</th>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Science.org</td>
            <td style="padding: 10px; border: 1px solid #ddd;">0</td>
            <td style="padding: 10px; border: 1px solid #ddd;">⏳ 进行中</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Nature.com</td>
            <td style="padding: 10px; border: 1px solid #ddd;">0</td>
            <td style="padding: 10px; border: 1px solid #ddd;">⏳ 进行中</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">Cell.com</td>
            <td style="padding: 10px; border: 1px solid #ddd;">0</td>
            <td style="padding: 10px; border: 1px solid #ddd;">⏳ 进行中</td>
        </tr>
    </table>
    
    <h3>📄 最新文章</h3>
    <p>今日暂无新文章（系统初始化中...）</p>
    
    <h3>🔍 关键词追踪</h3>
    <ul>
        <li>virtual cell: 0 篇</li>
        <li>synthetic biology: 0 篇</li>
        <li>systems biology: 0 篇</li>
    </ul>
    """
    
    return "文献追踪日报", content

def generate_weekly_report():
    """生成周报内容"""
    content = """
    <h3>📈 本周统计</h3>
    <p>本周共爬取文章：0 篇</p>
    <p>成功：0 篇 | 失败：0 篇</p>
    
    <h3>🎯 重点关注领域进展</h3>
    <ul>
        <li>虚拟细胞研究：本周暂无更新</li>
        <li>合成生物学：本周暂无更新</li>
    </ul>
    
    <h3>📚 推荐延伸阅读</h3>
    <p>暂无推荐（系统初始化中...）</p>
    """
    
    return "文献追踪周报", content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='发送文献追踪报告邮件')
    parser.add_argument('--type', choices=['daily', 'weekly', 'test'], required=True, 
                       help='报告类型：daily=日报, weekly=周报, test=测试邮件')
    parser.add_argument('--subject', help='自定义邮件主题（可选）')
    
    args = parser.parse_args()
    
    if args.type == 'test':
        subject = "测试邮件"
        content = "<p>这是一封测试邮件，确认邮件发送功能正常。</p>"
        report_type = "测试"
    elif args.type == 'daily':
        subject, content = generate_daily_report()
        report_type = "日报"
    elif args.type == 'weekly':
        subject, content = generate_weekly_report()
        report_type = "周报"
    
    if args.subject:
        subject = args.subject
    
    send_email(subject, content, report_type)
