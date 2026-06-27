"""
Science 每日报告生成器
- Latest News 文章（标题 + 作者 + 机构 + 摘要 + 中文）
- 通讯作者背景调查
"""
import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path
from loguru import logger

from .models import Article
from .science_news import ScienceLatestNewsScraper, ScienceArticle, translate_to_chinese
from .author_background import BatchBackgroundChecker


class DailyReportGenerator:
    """每日报告生成"""
    
    def __init__(self, output_dir: str = "/opt/data/literature-scraper/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.scraper = ScienceLatestNewsScraper()
        self.background_checker = BatchBackgroundChecker()
    
    def generate_daily_report(self, date: str = None, limit: int = 10) -> Dict:
        """
        生成每日报告
        
        流程：
        1. 抓取 Latest News 文章
        2. 提取作者信息
        3. 查询通讯作者背景
        4. 翻译标题和摘要
        5. 生成 HTML 报告
        
        Returns:
            {
                "date": str,
                "articles": [...],
                "html_path": str,
                "summary": str
            }
        """
        date = date or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"生成 {date} 每日报告...")
        
        # 1. 获取最新文章链接
        urls = self.scraper.get_latest_news_urls(limit=limit)
        if not urls:
            logger.error("未能获取文章链接")
            return None
        
        # 2. 抓取文章详情
        articles = []
        for url in urls:
            logger.info(f"抓取：{url}")
            html = self.scraper.fetch_page(url)
            if html:
                article = self.scraper.parse_article(html, url)
                if article:
                    articles.append(article)
        
        logger.info(f"成功抓取 {len(articles)} 篇文章")
        
        # 3. 查询通讯作者背景
        for article in articles:
            if hasattr(article, 'corresponding_authors') and article.corresponding_authors:
                for corr_author in article.corresponding_authors:
                    background = self.background_checker.check_multiple([corr_author])
                    if background:
                        corr_author['background'] = background[0].get('background', {})
        
        # 4. 翻译和格式化
        formatted_articles = []
        for article in articles:
            formatted = self._format_article(article)
            formatted_articles.append(formatted)
        
        # 5. 生成 HTML 报告
        html_path = self._generate_html(formatted_articles, date)
        
        # 6. 生成总结
        summary = f"今日共 {len(formatted_articles)} 篇 Latest News"
        
        return {
            "date": date,
            "articles": formatted_articles,
            "html_path": str(html_path),
            "summary": summary,
            "raw_articles": articles  # 保留原始数据
        }
    
    def _format_article(self, article: ScienceArticle) -> Dict:
        """格式化单篇文章"""
        # 翻译标题和摘要
        title_zh = translate_to_chinese(article.title)
        abstract_zh = translate_to_chinese(article.abstract)
        
        # 格式化作者信息
        authors_formatted = []
        for i, author in enumerate(article.authors_detail):
            authors_formatted.append({
                "name": author.get('name', ''),
                "affiliation": author.get('affiliation', ''),
                "is_corresponding": author.get('is_corresponding', False)
            })
        
        return {
            "title": article.title,
            "title_zh": title_zh,
            "authors": authors_formatted,
            "affiliations": self._extract_unique_affiliations(authors_formatted),
            "abstract": article.abstract,
            "abstract_zh": abstract_zh,
            "doi": article.doi,
            "url": article.url,
            "category": article.article_category,
            "published_date": article.published_date,
            "corresponding_authors": [
                {
                    "name": a.get('name', ''),
                    "background": a.get('background', {})
                }
                for a in getattr(article, 'corresponding_authors', [])
            ],
            "keywords": article.keywords
        }
    
    def _extract_unique_affiliations(self, authors: List[Dict]) -> List[str]:
        """提取唯一机构列表"""
        affiliations = set()
        for author in authors:
            affil = author.get('affiliation', '')
            if affil:
                affiliations.add(affil)
        return list(affiliations)
    
    def _generate_html(self, articles: List[Dict], date: str) -> Path:
        """生成 HTML 报告"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Science 每日报告 - {date}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.6; }}
        h1 {{ color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        .article {{ background: #f9f9f9; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .title {{ font-size: 1.3em; font-weight: bold; color: #0066cc; }}
        .title-zh {{ color: #666; font-size: 1.1em; margin: 5px 0 15px 0; }}
        .authors {{ color: #555; font-style: italic; margin: 10px 0; }}
        .affiliations {{ color: #777; font-size: 0.9em; margin: 10px 0; }}
        .abstract {{ background: #fff; padding: 15px; margin: 15px 0; border-left: 3px solid #0066cc; }}
        .abstract-zh {{ color: #444; }}
        .corresponding {{ background: #e7f3ff; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        .keyword {{ display: inline-block; background: #e0e0e0; padding: 3px 8px; margin: 2px; border-radius: 3px; font-size: 0.85em; }}
        .doi {{ color: #888; font-size: 0.85em; }}
    </style>
</head>
<body>
    <h1>📰 Science 每日报告</h1>
    <p><strong>日期：</strong>{date}</p>
    <p><strong>篇数：</strong>{len(articles)} 篇 Latest News</p>
    
    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
"""
        
        for i, article in enumerate(articles, 1):
            html_content += f"""
    <div class="article">
        <div class="title">[{i}] {article['title']}</div>
        <div class="title-zh">{article['title_zh']}</div>
        
        <div class="authors">
            <strong>作者：</strong>{', '.join([a['name'] + (' (通讯)' if a['is_corresponding'] else '') for a in article['authors']])}
        </div>
        
        <div class="affiliations">
            <strong>机构：</strong>{'; '.join(article['affiliations']) if article['affiliations'] else '信息待补充'}
        </div>
        
        <div class="abstract">
            <strong>摘要：</strong><br>
            {article['abstract']}
        </div>
        <div class="abstract-zh">
            <strong>中文：</strong>{article['abstract_zh']}
        </div>
        
        <div class="corresponding">
            <strong>通讯作者背景：</strong><br>
"""
            
            for corr in article['corresponding_authors']:
                bg = corr.get('background', {})
                summary_zh = bg.get('summary_zh', '信息待补充')
                html_content += f"• {corr['name']}: {summary_zh}<br>"
            
            html_content += f"""
        </div>
        
        <div>
            <span class="keyword">{'</span><span class="keyword">'.join(article['keywords'][:5])}</span>
        </div>
        
        <div class="doi">DOI: {article['doi']} | <a href="{article['url']}">原文链接</a></div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        # 保存 HTML
        html_path = self.output_dir / f"daily_report_{date.replace('-', '')}.html"
        html_path.write_text(html_content, encoding='utf-8')
        
        logger.info(f"HTML 报告已保存：{html_path}")
        return html_path


if __name__ == "__main__":
    # 测试
    generator = DailyReportGenerator()
    report = generator.generate_daily_report(limit=3)
    
    if report:
        print(f"\n生成报告：{report['summary']}")
        print(f"HTML 路径：{report['html_path']}")
