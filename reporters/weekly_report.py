"""
Science 每周报告生成器
- Commentary
- Editorial
- Careers
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from loguru import logger

from .science_news import ScienceLatestNewsScraper


class WeeklyReportGenerator:
    """每周报告生成（Commentary + Editorial + Careers）"""
    
    def __init__(self, output_dir: str = "/opt/data/literature-scraper/output"):
        self.output_dir = Path(output_dir)
        self.scraper = ScienceLatestNewsScraper()
    
    def generate_weekly_report(self, week_start: str = None) -> Dict:
        """
        生成每周报告
        
        内容：
        1. Commentary 评论文章
        2. Editorial 编辑文章
        3. Careers 职业发展
        
        Args:
            week_start: ISO 日期格式 (YYYY-MM-DD)，默认为本周一
        
        Returns:
            {
                "week_start": str,
                "week_end": str,
                "categories": {
                    "commentary": [...],
                    "editorial": [...],
                    "careers": [...]
                },
                "html_path": str,
                "summary_zh": str
            }
        """
        # 计算本周范围
        if week_start is None:
            today = datetime.now()
            # 本周一
            monday = today - timedelta(days=today.weekday())
            week_start = monday.strftime("%Y-%m-%d")
        
        week_start_dt = datetime.strptime(week_start, "%Y-%m-%d")
        week_end_dt = week_start_dt + timedelta(days=6)
        week_end = week_end_dt.strftime("%Y-%m-%d")
        
        logger.info(f"生成周报：{week_start} 至 {week_end}")
        
        # 抓取三类文章
        categories = {
            "commentary": self._scrape_category("commentary", limit=10),
            "editorial": self._scrape_category("editorial", limit=10),
            "careers": self._scrape_category("careers", limit=10),
        }
        
        # 生成 HTML
        html_path = self._generate_html(categories, week_start, week_end)
        
        # 中文总结
        summary_zh = self._generate_summary_zh(categories)
        
        return {
            "week_start": week_start,
            "week_end": week_end,
            "categories": categories,
            "html_path": str(html_path),
            "summary_zh": summary_zh,
            "total_count": sum(len(v) for v in categories.values())
        }
    
    def _scrape_category(self, category: str, limit: int = 10) -> List[Dict]:
        """
        抓取特定类别的文章
        
        Science URL 模式:
        - Commentary: /section/commentary
        - Editorial: /section/editorial
        - Careers: /section/careers
        """
        logger.info(f"抓取 {category} 类别文章...")
        
        base_url = f"{self.scraper.base_url}/section/{category}"
        
        # 访问分类页面
        html = self.scraper.fetch_page(base_url)
        if not html:
            logger.warning(f"无法获取 {category} 页面")
            return []
        
        # 提取文章列表（简化实现）
        # 实际需要解析页面中的文章链接
        articles = []
        
        # TODO: 实现详细的分类页面解析
        # 目前返回占位数据
        
        logger.info(f"抓取到 {len(articles)} 篇 {category} 文章")
        return articles
    
    def _generate_html(self, categories: Dict, week_start: str, week_end: str) -> Path:
        """生成 HTML 周报"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Science 每周报告 - {week_start} 至 {week_end}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.6; }}
        h1 {{ color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; background: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .section {{ margin: 30px 0; }}
        .article {{ background: #f9f9f9; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #0066cc; }}
        .title {{ font-size: 1.1em; font-weight: bold; color: #0066cc; }}
        .meta {{ color: #888; font-size: 0.9em; margin: 5px 0; }}
        .empty {{ color: #999; font-style: italic; padding: 20px; text-align: center; }}
    </style>
</head>
<body>
    <h1>📊 Science 每周报告</h1>
    <p><strong>周期：</strong>{week_start} 至 {week_end}</p>
"""
        
        # Commentary
        html_content += """
    <div class="section">
        <h2>💬 Commentary（评论）</h2>
"""
        if categories['commentary']:
            for article in categories['commentary']:
                html_content += self._render_article(article)
        else:
            html_content += '        <div class="empty">本周无更新</div>\n'
        
        html_content += """    </div>
"""
        
        # Editorial
        html_content += """
    <div class="section">
        <h2>✏️ Editorial（编辑文章）</h2>
"""
        if categories['editorial']:
            for article in categories['editorial']:
                html_content += self._render_article(article)
        else:
            html_content += '        <div class="empty">本周无更新</div>\n'
        
        html_content += """    </div>
"""
        
        # Careers
        html_content += """
    <div class="section">
        <h2>🎓 Careers（职业发展）</h2>
"""
        if categories['careers']:
            for article in categories['careers']:
                html_content += self._render_article(article)
        else:
            html_content += '        <div class="empty">本周无更新</div>\n'
        
        html_content += """
    </div>
</body>
</html>
"""
        
        # 保存
        html_path = self.output_dir / f"weekly_report_{week_start.replace('-', '')}.html"
        html_path.write_text(html_content, encoding='utf-8')
        
        logger.info(f"周报已保存：{html_path}")
        return html_path
    
    def _render_article(self, article: Dict) -> str:
        """渲染单篇文章 HTML"""
        return f"""
        <div class="article">
            <div class="title">{article.get('title', '无标题')}</div>
            <div class="meta">
                作者：{', '.join(article.get('authors', []))} | 
                日期：{article.get('date', '未知')}
            </div>
            <div>{article.get('abstract', '')}</div>
            <div class="meta"><a href="{article.get('url', '#')}">阅读原文</a></div>
        </div>
"""
    
    def _generate_summary_zh(self, categories: Dict) -> str:
        """生成中文周总结"""
        counts = {k: len(v) for k, v in categories.items()}
        
        parts = []
        if counts['commentary'] > 0:
            parts.append(f"评论文章 {counts['commentary']} 篇")
        if counts['editorial'] > 0:
            parts.append(f"编辑文章 {counts['editorial']} 篇")
        if counts['careers'] > 0:
            parts.append(f"职业发展 {counts['careers']} 篇")
        
        if parts:
            return f"本周 Science 更新：{'；'.join(parts)}。"
        else:
            return "本周暂无更新。"


if __name__ == "__main__":
    # 测试
    generator = WeeklyReportGenerator()
    report = generator.generate_weekly_report()
    
    print(f"\n周报生成：{report['summary_zh']}")
    print(f"HTML 路径：{report['html_path']}")
    print(f"总计：{report['total_count']} 篇文章")
