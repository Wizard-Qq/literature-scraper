"""
通讯作者背景调查模块
查询作者的机构、研究领域、发表记录等
"""
import re
import json
from typing import List, Dict, Optional
from loguru import logger


class AuthorBackgroundChecker:
    """
    作者背景调查
    
    功能：
    1. 从机构页面获取官方信息
    2. 搜索作者的 Google Scholar / ResearchGate
    3. 提取研究领域关键词
    4. 生成中文摘要
    """
    
    def __init__(self):
        self.search_base_urls = [
            "https://scholar.google.com/scholar?q={author}+{affiliation}",
            "https://pubmed.ncbi.nlm.nih.gov/?term={author}[Author]",
            "https://www.researchgate.net/search/publication?q={author}",
        ]
    
    def check_background(self, author_name: str, affiliation: Optional[str] = None) -> Dict:
        """
        查询作者背景
        
        Returns:
            {
                "name": str,
                "affiliation": str,
                "research_areas": List[str],
                "key_publications": List[str],
                "h_index": Optional[int],
                "summary_zh": str  # 中文总结
            }
        """
        logger.info(f"查询作者背景：{author_name}")
        
        # 策略 1: 尝试从 Science 页面已获取的信息中提取
        # （在之前的爬虫中已获取机构信息）
        
        # 策略 2: 搜索 Google Scholar（需要 API 或 HTML 解析）
        scholar_info = self._query_google_scholar(author_name, affiliation)
        
        # 策略 3: 搜索 PubMed 获取发表记录
        pubmed_info = self._query_pubmed(author_name)
        
        # 整合信息
        background = {
            "name": author_name,
            "affiliation": affiliation or "Unknown",
            "research_areas": self._extract_research_areas(scholar_info, pubmed_info),
            "key_publications": self._get_top_publications(pubmed_info),
            "h_index": scholar_info.get("h_index"),
            "summary_zh": self._generate_summary_zh(author_name, affiliation, scholar_info, pubmed_info)
        }
        
        return background
    
    def _query_google_scholar(self, author_name: str, affiliation: Optional[str]) -> Dict:
        """查询 Google Scholar 信息（简化版）"""
        # 注意：Google Scholar 有反爬机制，生产环境需要使用官方 API 或代理
        # 这里仅做框架，实际需要更完善的实现
        
        return {
            "h_index": None,
            "citations": None,
            "top_papers": []
        }
    
    def _query_pubmed(self, author_name: str) -> List[Dict]:
        """查询 PubMed 发表记录"""
        # 可以使用 NCBI E-utilities API
        # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=author_name
        
        # 简化返回
        return []
    
    def _extract_research_areas(self, scholar_info: Dict, pubmed_info: List) -> List[str]:
        """提取研究领域关键词"""
        areas = []
        
        # 从 Scholar 信息提取
        if scholar_info.get("top_papers"):
            for paper in scholar_info["top_papers"]:
                # 从标题/关键词提取领域
                pass
        
        # 从 PubMed 提取 MeSH 关键词
        if pubmed_info:
            for paper in pubmed_info[:5]:
                if paper.get("mesh_terms"):
                    areas.extend(paper["mesh_terms"][:3])
        
        # 去重
        return list(set(areas))[:10]
    
    def _get_top_publications(self, pubmed_info: List) -> List[str]:
        """获取代表性论文"""
        return [p.get("title", "") for p in pubmed_info[:5]] if pubmed_info else []
    
    def _generate_summary_zh(self, name: str, affiliation: Optional[str], 
                             scholar_info: Dict, pubmed_info: List) -> str:
        """生成中文背景总结"""
        parts = []
        
        # 机构
        if affiliation:
            parts.append(f"来自{affiliation}")
        
        # 研究领域
        research_areas = self._extract_research_areas(scholar_info, pubmed_info)
        if research_areas:
            areas_zh = self._translate_areas(research_areas[:5])
            parts.append(f"主要从事{'、'.join(areas_zh)}等研究")
        
        # 代表作
        publications = self._get_top_publications(pubmed_info)
        if publications:
            parts.append(f"发表代表作 {len(publications)} 篇")
        
        summary = "。".join(parts) if parts else "信息待补充"
        return summary + "。"
    
    def _translate_areas(self, areas: List[str]) -> List[str]:
        """翻译研究领域为中文"""
        # 简单映射表（可扩展）
        translation_map = {
            "Molecular Biology": "分子生物学",
            "Genetics": "遗传学",
            "Biochemistry": "生物化学",
            "Cell Biology": "细胞生物学",
            "Neuroscience": "神经科学",
            "Immunology": "免疫学",
            "Bioinformatics": "生物信息学",
            "Synthetic Biology": "合成生物学",
            "Systems Biology": "系统生物学",
            "Computational Biology": "计算生物学",
        }
        
        return [translation_map.get(area, area) for area in areas]


class BatchBackgroundChecker:
    """批量作者背景查询"""
    
    def __init__(self):
        self.checker = AuthorBackgroundChecker()
    
    def check_multiple(self, authors: List[Dict], max_concurrent: int = 3) -> List[Dict]:
        """
        批量查询多位作者背景
        
        Args:
            authors: [{"name": "...", "affiliation": "..."}, ...]
            max_concurrent: 最大并发数
        
        Returns:
            [{"name": "...", "background": {...}}, ...]
        """
        results = []
        
        # 简单串行实现（后续可改为并发）
        for author in authors:
            background = self.checker.check_background(
                author.get("name", ""),
                author.get("affiliation")
            )
            results.append({
                "name": author.get("name", ""),
                "background": background
            })
        
        return results


if __name__ == "__main__":
    # 测试
    checker = AuthorBackgroundChecker()
    
    # 示例：查询某作者
    background = checker.check_background(
        "Jennifer Doudna",
        "University of California, Berkeley"
    )
    
    print(f"作者：{background['name']}")
    print(f"机构：{background['affiliation']}")
    print(f"研究领域：{background['research_areas']}")
    print(f"总结：{background['summary_zh']}")
