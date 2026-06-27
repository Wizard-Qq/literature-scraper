#!/usr/bin/env python3
"""
邮件发送模块 - 重构版
支持日报和周报
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from config_manager import get_config


def send_email(subject: str, content: str, report_type: str = "日报", 
               recipient_email: Optional[str] = None):
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        content: HTML 内容
        report_type: 报告类型（日报/周报/测试）
        recipient_email: 收件人（可选，默认使用配置）
    """
    config = get_config()
    smtp_config = config.email_config
    
    if not smtp_config:
        logger.error("邮箱配置缺失")
        return False
    
    recipient = recipient_email or smtp_config.get('recipient_email')
    
    if not recipient:
        logger.error("收件人地址缺失")
        return False
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_config['sender_email']
    msg['To'] = recipient
    msg['Subject'] = f"[{report_type}] {subject} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 构建完整 HTML
    full_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; font-size: 24px;">📚 文献追踪系统</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
                {report_type} | {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
            </p>
        </div>
        
        {content}
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; color: #999; font-size: 12px; text-align: center;">
            <p>此邮件由 <strong>UGREEN NAS</strong> 自动发送</p>
            <p>文献追踪系统 v2.0 | 项目地址：https://github.com/Wizard-Qq/literature-scraper</p>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(full_html, 'html', 'utf-8'))
    
    # 发送
    try:
        if smtp_config.get('use_ssl', True):
            server = smtplib.SMTP_SSL(
                smtp_config['smtp_server'], 
                smtp_config['smtp_port']
            )
        else:
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
        
        # 登录
        server.login(
            smtp_config['sender_email'], 
            smtp_config.get('sender_password', '')
        )
        
        # 发送
        server.send_message(msg)
        server.quit()
        
        logger.info(f"✅ 邮件发送成功：{subject}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 邮件发送失败：{e}")
        return False


def send_test_email():
    """发送测试邮件"""
    subject = "测试邮件"
    content = """
    <h2>✅ 邮件系统测试成功!</h2>
    <p>这是一封测试邮件，确认邮件发送功能正常。</p>
    
    <h3>系统信息</h3>
    <ul>
        <li>发送时间：{time}</li>
        <li>系统版本：v2.0</li>
        <li>配置状态：✅ 已加载</li>
    </ul>
    """.format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return send_email(subject, content, report_type="测试")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("发送测试邮件...")
        success = send_test_email()
        sys.exit(0 if success else 1)
    else:
        print("用法：python email_sender.py [test]")
        print("示例：python email_sender.py test")
