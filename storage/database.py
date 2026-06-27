"""
数据存储层 - SQLite 数据库
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import json

from loguru import logger
from .models import Article, SourceType


class Database:
    """SQLite 数据库管理类"""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "articles.db"
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
        logger.info(f"数据库初始化：{db_path}")
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doi TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    authors TEXT,
                    abstract TEXT,
                    keywords TEXT,
                    article_type TEXT,
                    published_date TEXT,
                    crawled_at TEXT NOT NULL,
                    is_new INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doi ON articles(doi)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON articles(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_crawled ON articles(crawled_at)")
    
    def article_exists(self, doi: str) -> bool:
        """检查文章是否已存在"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM articles WHERE doi = ?", (doi,)
            )
            return cursor.fetchone() is not None
    
    def save_article(self, article: Article) -> bool:
        """保存文章"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 检查是否已存在
                if self.article_exists(article.doi):
                    logger.debug(f"文章已存在，跳过：{article.doi}")
                    return False
                
                conn.execute("""
                    INSERT INTO articles (
                        doi, title, url, source, authors, abstract,
                        keywords, article_type, published_date, crawled_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.doi,
                    article.title,
                    article.url,
                    article.source.value,
                    json.dumps(article.authors),
                    article.abstract,
                    json.dumps(article.keywords),
                    article.article_type,
                    article.published_date.isoformat() if article.published_date else None,
                    article.crawled_at.isoformat(),
                ))
                
                logger.debug(f"保存文章：{article.title[:50]}...")
                return True
                
        except sqlite3.IntegrityError as e:
            logger.warning(f"保存失败（可能重复）：{e}")
            return False
        except Exception as e:
            logger.error(f"保存异常：{e}")
            return False
    
    def save_articles(self, articles: List[Article]) -> int:
        """批量保存文章"""
        count = 0
        for article in articles:
            if self.save_article(article):
                count += 1
        return count
    
    def get_new_articles(self, days: int = 7) -> List[dict]:
        """获取最近 N 天的新文章"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM articles
                WHERE crawled_at >= datetime('now', ?)
                ORDER BY crawled_at DESC
            """, (f'-{days} days',))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self, days: int = 7) -> dict:
        """获取统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    source,
                    COUNT(*) as count,
                    COUNT(DISTINCT doi) as unique_dois
                FROM articles
                WHERE crawled_at >= datetime('now', ?)
                GROUP BY source
            """, (f'-{days} days',))
            
            stats = {}
            for row in cursor.fetchall():
                stats[row['source']] = {
                    'count': row['count'],
                    'unique_dois': row['unique_dois']
                }
            
            return stats
    
    def close(self):
        """关闭数据库连接"""
        pass  # SQLite 自动管理
