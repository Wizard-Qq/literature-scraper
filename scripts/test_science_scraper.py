#!/usr/bin/env python3
"""
Science 爬虫快速测试脚本

测试流程：
1. 抓取 Latest News 页面
2. 提取 3 篇文章链接
3. 解析 1 篇文章详情
4. 展示作者信息和通迅作者识别
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.science_news import ScienceLatestNewsScraper
from scrapers.author_background import AuthorBackgroundChecker
from loguru import logger

# 配置日志
logger.add(sys.stderr, level="DEBUG")


def test_latest_news_fetching():
    """测试 1: 获取 Latest News 列表"""
    print("\n" + "="*60)
    print("测试 1: 抓取 Latest News 页面")
    print("="*60)
    
    scraper = ScienceLatestNewsScraper()
    
    # 获取 5 个链接
    urls = scraper.get_latest_news_urls(limit=5)
    
    print(f"\n✅ 找到 {len(urls)} 个链接:")
    for i, url in enumerate(urls, 1):
        print(f"  [{i}] {url}")
    
    return urls


def test_article_parsing(url: str):
    """测试 2: 解析文章详情"""
    print("\n" + "="*60)
    print(f"测试 2: 解析文章详情")
    print(f"URL: {url}")
    print("="*60)
    
    scraper = ScienceLatestNewsScraper()
    
    # 抓取文章
    html = scraper.fetch_page(url)
    if not html:
        print("❌ 抓取失败")
        return None
    
    print(f"✅ 抓取成功，HTML 大小：{len(html)} 字节")
    
    # 解析
    article = scraper.parse_article(html, url)
    if not article:
        print("❌ 解析失败")
        return None
    
    print(f"\n📄 文章信息:")
    print(f"  标题：{article.title}")
    print(f"  DOI: {article.doi}")
    print(f"  类别：{article.article_category}")
    print(f"  作者数：{len(article.authors_detail)}")
    print(f"  通讯作者数：{len(article.corresponding_authors)}")
    
    # 展示作者详情
    if article.authors_detail:
        print(f"\n👥 作者列表:")
        for i, author in enumerate(article.authors_detail[:5], 1):
            corr_mark = " (通讯)" if author.get('is_corresponding') else ""
            print(f"  [{i}] {author['name']}{corr_mark}")
            if author.get('affiliation'):
                print(f"      机构：{author['affiliation']}")
    
    # 展示通迅作者
    if article.corresponding_authors:
        print(f"\n📧 通讯作者:")
        for corr in article.corresponding_authors[:3]:
            print(f"  • {corr.get('name', 'Unknown')}")
    
    return article


def test_author_background(author_name: str, affiliation: str = None):
    """测试 3: 作者背景调查"""
    print("\n" + "="*60)
    print(f"测试 3: 作者背景调查")
    print(f"作者：{author_name}")
    print("="*60)
    
    checker = AuthorBackgroundChecker()
    background = checker.check_background(author_name, affiliation)
    
    print(f"\n📚 背景信息:")
    print(f"  机构：{background.get('affiliation', 'Unknown')}")
    print(f"  研究领域：{', '.join(background.get('research_areas', [])[:5])}")
    print(f"  代表作数：{len(background.get('key_publications', []))}")
    print(f"\n🇨🇳 中文总结:")
    print(f"  {background.get('summary_zh', '无')}")


def main():
    print("\n🧪 Science 爬虫测试套件\n")
    
    # 测试 1: 获取链接
    urls = test_latest_news_fetching()
    if not urls:
        print("\n❌ 测试 1 失败，终止")
        return 1
    
    # 测试 2: 解析文章（仅测试第 1 篇）
    if urls:
        article = test_article_parsing(urls[0])
        
        # 测试 3: 作者背景（如果有通迅作者）
        if article and article.corresponding_authors:
            corr = article.corresponding_authors[0]
            test_author_background(
                corr.get('name', 'Unknown'),
                corr.get('affiliation')
            )
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
