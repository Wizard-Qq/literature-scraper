"""
Science 期刊爬虫 - 专业版
获取 Latest News 文章详细信息 + 作者机构 + 通迅作者背景
"""
import re
import json
import time
from typing import List, Dict, Optional
from datetime import datetime

from loguru import logger
from scrapling import StealthyFetcher

from .base import BaseScraper
from .models import Article, SourceType


class AuthorInfo:
    """作者信息"""
    def __init__(self, name: str, affiliation: str = None, is_corresponding: bool = False):
        self.name = name
        self.affiliation = affiliation
        self.is_corresponding = is_corresponding
    
    def to_dict(self):
        return {
            "name": self.name,
            "affiliation": self.affiliation,
            "is_corresponding": self.is_corresponding
        }


class ScienceArticle(Article):
    """Science 文章（扩展版）"""
    authors_detail: List[Dict] = []  # 作者详细信息
    corresponding_authors: List[Dict] = []  # 通讯作者
    article_category: str = ""  # 文章类别（Research Article, News 等）
    published_date: Optional[str] = None
    chinese_translation: Dict = None  # 中文翻译


class ScienceLatestNewsScraper(BaseScraper):
    """Science Latest News 爬虫"""
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {
                "name": "Science Latest News",
                "base_url": "https://www.science.org",
                "timeout": 300000,  # 5 分钟
                "wait_time": 120000,  # 120 秒等待 Cloudflare
                "solve_cloudflare": True,
            }
        super().__init__(config)
        
        self.latest_news_url = f"{self.base_url}/action/showFeed?mjKey=1&miKey=1"
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.SCIENCE
    
    def get_latest_news_urls(self, limit: int = 10) -> List[str]:
        """
        获取 Latest News 页面文章链接
        
        策略：访问 Latest News 页面，提取最新文章
        """
        logger.info("获取 Science Latest News...")
        
        # 访问 Latest News 页面
        news_page_url = f"{self.base_url}/news"
        html = self.fetch_page(news_page_url)
        
        if not html:
            logger.error("获取 Latest News 页面失败")
            return []
        
        # 提取文章链接
        # Science 的新闻文章通常在 /news/ 路径下
        pattern = r'href="(/news/[^"]+)"'
        matches = re.findall(pattern, html)
        
        # 去重并构建完整 URL
        urls = []
        seen = set()
        for match in matches:
            full_url = f"{self.base_url}{match}"
            if full_url not in seen:
                seen.add(full_url)
                urls.append(full_url)
            
            if len(urls) >= limit * 2:  # 多获取一些用于过滤
                break
        
        logger.info(f"找到 {len(urls)} 篇 Latest News 文章")
        return urls[:limit]
    
    def get_latest_urls(self, limit: int = 10) -> List[str]:
        """实现基类抽象方法 - 获取最新 URL 列表"""
        return self.get_latest_news_urls(limit)
    
    def parse_article(self, html: str, url: str) -> Optional[ScienceArticle]:
        """
        解析 Science 文章页面
        
        提取：
        - 标题、DOI、URL
        - 作者列表（含机构、通讯作者标识）
        - 摘要
        - 文章类别
        - 发表时间
        """
        try:
            # 标题
            title_match = re.search(r'<meta name="dc\.Title" content="([^"]+)"', html)
            title = title_match.group(1) if title_match else "Unknown"
            
            # DOI
            doi_match = re.search(r'10\.1126/([^"]+)', html)
            doi = f"10.1126/{doi_match.group(1)}" if doi_match else url
            
            # 文章类别
            category = ""
            category_match = re.search(r'"articleType"\s*:\s*"([^"]+)"', html)
            if category_match:
                category = category_match.group(1)
            
            # 作者信息（详细解析）
            authors = self._parse_authors(html)
            
            # 通讯作者（通常最后几位或有标注）
            corresponding = self._find_corresponding_authors(authors, html)
            
            # 摘要
            abstract = ""
            abstract_match = re.search(r'<meta name="dc\.Description" content="([^"]+)"', html)
            if abstract_match:
                abstract = abstract_match.group(1)
            
            # 发表时间
            pub_date = None
            date_match = re.search(r'<meta name="dc\.Date" content="([^"]+)"', html)
            if date_match:
                pub_date = date_match.group(1)
            
            # 关键词
            keywords = []
            keyword_matches = re.findall(r'<meta name="dc\.Subject" content="([^"]+)"', html)
            keywords = [kw for kw in keyword_matches if kw.strip()][:5]
            
            article = ScienceArticle(
                title=title,
                doi=doi,
                url=url,
                source=self.source_type,
                authors=[a['name'] for a in authors],
                abstract=abstract,
                keywords=keywords,
                article_type=category,
                html_content=html[:100000],
                # 扩展字段
                authors_detail=[a.to_dict() for a in authors],
                corresponding_authors=[a.to_dict() for a in corresponding],
                article_category=category,
                published_date=pub_date,
            )
            
            logger.debug(f"解析成功：{title[:50]}...")
            return article
            
        except Exception as e:
            logger.error(f"解析失败：{e}")
            return None
    
    def _parse_authors(self, html: str) -> List[AuthorInfo]:
        """解析作者信息"""
        authors = []
        
        # 尝试从 meta 标签提取
        author_matches = re.findall(r'<meta name="dc\.Creator" content="([^"]+)"', html)
        
        for author_str in author_matches:
            # 清理作者名
            name = author_str.strip()
            if " [" in name:
                name = name.split(" [")[0].strip()
            
            if name and name not in [a.name for a in authors]:
                # 尝试提取机构（从后续标签或 JSON 数据）
                affiliation = self._extract_affiliation(html, name)
                
                authors.append(AuthorInfo(
                    name=name,
                    affiliation=affiliation,
                    is_corresponding=False  # 后续单独标记
                ))
        
        # 如果没有从 meta 找到，尝试从页面结构提取
        if not authors:
            # 查找作者列表区域
            author_section = re.search(r'<div[^>]*class="[^"]*author[^"]*"[^>]*>.*?</div>', html, re.DOTALL)
            if author_section:
                # 进一步解析...
                pass
        
        return authors
    
    def _extract_affiliation(self, html: str, author_name: str) -> Optional[str]:
        """尝试提取作者机构"""
        # 策略 1: 从 JSON 数据提取
        json_match = re.search(r'author":\s*\[(.*?)\]', html, re.DOTALL)
        if json_match:
            try:
                author_json = json.loads(f'[{json_match.group(1)}]')
                for author in author_json:
                    if author.get('given', '') in author_name or author.get('family', '') in author_name:
                        affils = author.get('affiliation', [])
                        if affils:
                            # 只取第一个机构的名称
                            return affils[0].get('name', '') if isinstance(affils[0], dict) else str(affils[0])
            except:
                pass
        
        # 策略 2: 从页面文本搜索作者名附近的机构信息
        # （简化版，实际需要更复杂的解析）
        
        return None
    
    def _find_corresponding_authors(self, authors: List[AuthorInfo], html: str) -> List[AuthorInfo]:
        """
        识别通讯作者
        
        策略：
        1. 查找页面中的 "Correspondence" 或 "corresponding author" 标注
        2. 查找作者列表最后几位
        3. 查找邮箱标注（* 符号）
        """
        corresponding = []
        
        # 策略 1: 查找 Corresondence 部分
        corr_section = re.search(r'Correspondence.*?(?:to|:).*?(?:@[^\\s<]+)', html, re.IGNORECASE)
        if corr_section:
            corr_text = corr_section.group(0)
            for author in authors:
                if author.name.lower() in corr_text.lower():
                    author.is_corresponding = True
                    corresponding.append(author)
        
        # 策略 2: 如果没有明确标注，取最后 2-3 位作者
        if not corresponding and len(authors) >= 2:
            last_authors = authors[-3:] if len(authors) > 3 else authors
            for author in last_authors:
                author.is_corresponding = True
                corresponding.append(author)
        
        return corresponding


def translate_to_chinese(text: str) -> str:
    """
    简单的中文翻译（占位符）
    
    TODO: 集成翻译 API（百度/谷歌/DeepL）
    目前返回简易翻译
    """
    if not text:
        return ""
    
    # 临时方案：返回原文 + 标注
    return f"[待翻译] {text}"
    # 后续可接入翻译 API
    # return translation_api.translate(text, target='zh-CN')


if __name__ == "__main__":
    # 测试
    scraper = ScienceLatestNewsScraper()
    urls = scraper.get_latest_news_urls(limit=3)
    print(f"找到 {len(urls)} 个链接:")
    for url in urls[:5]:
        print(f"  - {url}")
