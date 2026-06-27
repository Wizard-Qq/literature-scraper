"""
Science.org 爬虫
"""
import re
import json
from typing import List, Optional
from datetime import datetime

from loguru import logger
from scrapling import StealthyFetcher

from .base import BaseScraper, FETCHER_PARAMS
from .models import Article, SourceType


class ScienceScraper(BaseScraper):
    """Science.org 爬虫"""
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {
                "name": "Science.org",
                "base_url": "https://www.science.org",
                "timeout": 300000,
                "wait_time": 90000,
                "solve_cloudflare": True,
            }
        super().__init__(config)
    
    @property
    def source_type(self) -> SourceType:
        return SourceType.SCIENCE
    
    def get_latest_urls(self, limit: int = 10) -> List[str]:
        """
        获取 Science.org 最新文章 URL
        
        策略：访问首页，提取最新 DOI 链接
        """
        logger.info("获取 Science.org 最新文章...")
        
        homepage = f"{self.base_url}/toc/science/current"
        html = self.fetch_page(homepage)
        
        if not html:
            logger.error("获取首页失败")
            return []
        
        # 提取 DOI 链接
        doi_pattern = r'href="(/doi/10\.[^"]+)"'
        dois = re.findall(doi_pattern, html)
        
        # 转完整 URL
        urls = [f"{self.base_url}/doi/{doi.split('/')[-1]}" for doi in dois[:limit*2]]
        
        # 去重
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        logger.info(f"找到 {len(unique_urls)} 个最新文章链接")
        return unique_urls[:limit]
    
    def parse_article(self, html: str, url: str) -> Optional[Article]:
        """
        解析 Science 文章页面
        
        提取：
        - 标题：从 meta 标签
        - 作者：从 dc.Creator meta
        - 摘要：从 dc.Description meta
        - 文章类型：从 JSON 数据
        """
        try:
            # 提取标题
            title_match = re.search(r'<meta name="dc\.Title" content="([^"]+)"', html)
            title = title_match.group(1) if title_match else "Unknown"
            
            # 提取 DOI
            doi_match = re.search(r'10\.1126/([^"]+)', html)
            doi = f"10.1126/{doi_match.group(1)}" if doi_match else url
            
            # 提取作者
            authors = []
            author_matches = re.findall(r'<meta name="dc\.Creator" content="([^"]+)"', html)
            for author in author_matches:
                # 清理作者名
                author = author.split("【")[0].strip() if " [" in author else author
                if author and author not in authors:
                    authors.append(author)
            
            # 提取摘要
            abstract_match = re.search(r'<meta name="dc\.Description" content="([^"]+)"', html)
            abstract = abstract_match.group(1) if abstract_match else None
            
            # 提取文章类型
            article_type = None
            type_match = re.search(r'"articleType"\s*:\s*"([^"]+)"', html)
            if type_match:
                article_type = type_match.group(1)
            
            # 提取关键词（如果有）
            keywords = []
            keyword_matches = re.findall(r'<meta name="dc\.Subject" content="([^"]+)"', html)
            keywords = [kw for kw in keyword_matches if kw.strip()]
            
            article = Article(
                title=title,
                doi=doi,
                url=url,
                source=self.source_type,
                authors=authors[:10],  # 限制作者数量
                abstract=abstract,
                keywords=keywords[:5],
                article_type=article_type,
                html_content=html[:100000],  # 保存部分 HTML
            )
            
            logger.debug(f"解析成功：{title[:50]}...")
            return article
            
        except Exception as e:
            logger.error(f"解析失败：{e}")
            return None
