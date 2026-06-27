"""
配置管理模块
"""
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class Config:
    """配置管理器"""
    
    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        
        self.config_dir = config_dir
        self.settings = self._load_yaml("settings.yaml")
        self.secrets = self._load_yaml("secrets.yaml")
        
        # 合并配置
        self._merge_secrets()
        
        logger.info("配置加载完成")
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """加载 YAML 配置"""
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            logger.warning(f"配置文件不存在：{filepath}")
            return {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _merge_secrets(self):
        """合并敏感配置"""
        if "email" in self.settings and "email_password" in self.secrets:
            self.settings["email"]["sender_password"] = self.secrets["email_password"]
    
    def get(self, key: str, default=None):
        """获取配置项（支持点号嵌套）"""
        keys = key.split(".")
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def email_config(self) -> dict:
        """邮箱配置"""
        return self.settings.get("email", {})
    
    @property
    def sources_config(self) -> dict:
        """数据源配置"""
        return self.settings.get("sources", {})
    
    @property
    def scraper_config(self) -> dict:
        """爬虫策略配置"""
        return self.settings.get("scraper", {})
    
    @property
    def keywords(self) -> dict:
        """关键词配置"""
        return self.settings.get("keywords", {})
    
    @property
    def report_config(self) -> dict:
        """报告配置"""
        return self.settings.get("report", {})


# 全局配置实例
_config: Config = None

def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config
