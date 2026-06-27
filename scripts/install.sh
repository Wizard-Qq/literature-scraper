#!/bin/bash
# Science 期刊报告系统 - 安装脚本

set -e

PROJECT_DIR="/opt/data/literature-scraper"
VENV_DIR="/opt/venv"
PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip3"

echo "🚀 开始安装 Science 期刊报告系统..."

# 1. 创建必要目录
echo "📁 创建目录结构..."
mkdir -p "$PROJECT_DIR"/{logs,output,data}

# 2. 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 创建 Python 虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

# 3. 安装依赖
echo "📦 安装 Python 依赖..."
"$PIP" install --upgrade pip
"$PIP" install scrapling loguru pydantic pyyaml
# 注意：scrapling 会自动安装 playwright，需要额外安装浏览器
# playwright install chromium

# 4. 安装 crontab
echo "⏰ 安装定时任务..."
crontab "$PROJECT_DIR/config/crontab_science.txt"

# 5. 验证 crontab
echo "✅ 已安装的定时任务:"
crontab -l

# 6. 创建日志文件
touch "$PROJECT_DIR/logs/cron_daily.log"
touch "$PROJECT_DIR/logs/cron_weekly.log"
chmod 644 "$PROJECT_DIR/logs/"*.log

echo ""
echo "✨ 安装完成！"
echo ""
echo "📋 定时任务说明:"
echo "  - 每日报告：每天早上 8:00 发送 Latest News（10 篇文章）"
echo "  - 每周报告：每周六下午 2:00 发送 Commentary/Editorial/Careers"
echo ""
echo "📧 邮件接收地址：$(grep recipient "$PROJECT_DIR/config/settings.yaml" | cut -d: -f2 | tr -d ' ')"
echo ""
echo "🔧 常用命令:"
echo "  # 手动运行每日报告"
echo "  cd $PROJECT_DIR && $PYTHON scripts/daily_science_report.py --limit 3 --send-email"
echo ""
echo "  # 手动运行每周报告"
echo "  cd $PROJECT_DIR && $PYTHON scripts/weekly_science_report.py --send-email"
echo ""
echo "  # 查看日志"
echo "  tail -f $PROJECT_DIR/logs/cron_daily.log"
echo ""
echo "  # 卸载定时任务"
echo "  crontab -r"
echo ""
