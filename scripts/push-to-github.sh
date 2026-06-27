#!/bin/bash
# 推送脚本 - 网络恢复后手动运行

cd /opt/data/literature-scraper

echo "🚀 开始推送到 GitHub..."
echo "仓库：https://github.com/Wizard-Qq/literature-scraper"
echo ""

# 推送
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo "📦 查看仓库：https://github.com/Wizard-Qq/literature-scraper"
else
    echo ""
    echo "❌ 推送失败，请检查网络连接"
fi
