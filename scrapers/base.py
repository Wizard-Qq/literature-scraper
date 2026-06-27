"""
文献追踪系统 - 基础爬虫类
所有具体爬虫都继承此基类
"""
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from loguru import logger
from scrapling import StealthyFetcher

from .models import Article, CrawlResult, SourceType


FETCHER_PARAMS = {
    "headless": True,
    "disable_resources": True,  # 禁用图片/CSS/字体加速
    "timeout": 300000,  # 5 分钟超时
    "wait": 180000,  # 180 秒等待 Cloudflare ⭐ 关键参数 (2026-06-28 验证)
    "solve_cloudflare": True,
    "browser_type": "chromium",
    "stealth": True,  # 启用隐身模式
}


class BaseScraper(ABC):
    """爬虫基类"""
    
    def __init__(self, config: dict):
        """
        初始化爬虫
        
        Args:
            config: 数据源配置（来自 settings.yaml）
        """
        self.config = config
        self.source_name = config.get("name", "unknown")
        self.base_url = config.get("base_url", "")
        self.timeout = config.get("timeout", 180000)
        self.wait_time = config.get("wait_time", 60000)
        self.solve_cloudflare = config.get("solve_cloudflare", True)
        
        self.fetcher = StealthyFetcher(
            headless=FETCHER_PARAMS["headless"],
            disable_resources=FETCHER_PARAMS["disable_resources"],
            timeout=self.timeout,
            wait=self.wait_time,
            solve_cloudflare=self.solve_cloudflare,
        )
        
        logger.info(f"爬虫初始化完成：{self.source_name}")
    
    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        """数据源类型（由子类实现）"""
        pass
    
    @abstractmethod
    def parse_article(self, html: str, url: str) -> Optional[Article]:
        """
        从 HTML 中解析文章信息
        
        Args:
            html: 页面 HTML
            url: 页面 URL
            
        Returns:
            文章对象，解析失败返回 None
        """
        pass
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """
        获取页面内容
        
        Args:
            url: 目标 URL
            retries: 重试次数
            
        Returns:
            HTML 内容，失败返回 None
        """
        for attempt in range(retries):
            try:
                logger.info(f"获取页面：{url} (尝试 {attempt + 1}/{retries})")
                
                # 更新 fetcher 参数
                self.fetcher = StealthyFetcher(
                    headless=FETCHER_PARAMS["headless"],
                    disable_resources=FETCHER_PARAMS["disable_resources"],
                    timeout=self.timeout,
                    wait=self.wait_time,
                    solve_cloudflare=self.solve_cloudflare,
                )
                
                response = self.fetcher.fetch(url)
                
                if response.status != 200:
                    logger.warning(f"状态码异常：{response.status}")
                    if attempt < retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                
                # 使用 body 获取完整 HTML
                return response.body.decode('utf-8') if response.body else None
                
            except Exception as e:
                logger.error(f"获取失败：{e}")
                if attempt < retries - 1:
                    logger.info(f"等待 {10 * (attempt + 1)} 秒后重试...")
                    time.sleep(10 * (attempt + 1))
                else:
                    logger.error(f"获取失败：{url}")
                    return None
        
        return None
    
    def crawl(self, urls: List[str], max_articles: int = 10) -> CrawlResult:
        """
        爬取文章
        
        Args:
            urls: 文章 URL 列表
            max_articles: 最大文章数
            
        Returns:
            爬取结果
        """
        logger.info(f"开始爬取 {self.source_name}，目标 {len(urls)} 个 URL")
        
        articles = []
        errors = []
        
        for i, url in enumerate(urls[:max_articles]):
            try:
                html = self.fetch_page(url)
                
                if html:
                    article = self.parse_article(html, url)
                    if article:
                        articles.append(article)
                        logger.success(f"✓ 解析成功：{article.title[:50]}...")
                    else:
                        errors.append(f"解析失败：{url}")
                else:
                    errors.append(f"获取失败：{url}")
                
                # 礼貌延迟
                if i < len(urls) - 1:
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"爬取异常：{e}")
                errors.append(f"{url}: {str(e)}")
        
        return CrawlResult(
            success=len(articles) > 0,
            source=self.source_type,
            articles=articles,
            errors=errors,
        )
    
    @abstractmethod
    def get_latest_urls(self, limit: int = 10) -> List[str]:
        """
        获取最新文章 URL 列表
        
        Args:
            limit: 最大 URL 数
            
        Returns:
            URL 列表
        """
        pass
