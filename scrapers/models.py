"""
文献追踪系统 - 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """数据源类型"""
    SCIENCE = "science"
    NATURE = "nature"
    CELL = "cell"


class Article(BaseModel):
    """单篇文章模型"""
    title: str
    doi: str
    url: str
    source: SourceType
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    article_type: Optional[str] = None
    published_date: Optional[datetime] = None
    crawled_at: datetime = Field(default_factory=datetime.now)
    
    # 元数据
    html_content: Optional[str] = None
    raw_data: Optional[dict] = None
    
    def __hash__(self):
        return hash(self.doi)
    
    def __eq__(self, other):
        if not isinstance(other, Article):
            return False
        return self.doi == other.doi


class CrawlResult(BaseModel):
    """爬取结果"""
    success: bool
    source: SourceType
    articles: List[Article] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    crawl_time: datetime = Field(default_factory=datetime.now)
    article_count: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        self.article_count = len(self.articles)


class ReportData(BaseModel):
    """报告数据"""
    report_type: str  # daily, weekly
    date: datetime
    sources: List[SourceResult] = Field(default_factory=list)
    keywords_stats: dict = Field(default_factory=dict)
    summary: Optional[str] = None
    
    class SourceResult(BaseModel):
        source: SourceType
        article_count: int
        articles: List[Article]
