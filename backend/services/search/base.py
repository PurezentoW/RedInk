"""搜索服务抽象基类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchResult:
    """搜索结果数据类"""
    title: str
    url: str
    snippet: str
    content: str  # 完整内容
    source: str  # 搜索引擎名称
    score: float = 0.0
    published_date: Optional[str] = None
    thumbnail_url: Optional[str] = None


@dataclass
class SearchQuery:
    """搜索查询数据类"""
    query: str
    max_results: int = 5
    language: str = "zh-CN"
    region: str = "CN"
    safe_search: str = "Moderate"
    timeout: int = 30


class BaseSearchProvider(ABC):
    """搜索引擎提供商抽象基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.max_results = config.get('max_results', 5)
        self.timeout = config.get('timeout', 30)

    @abstractmethod
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """执行搜索

        Args:
            query: 搜索查询对象

        Returns:
            搜索结果列表

        Raises:
            Exception: 搜索失败时抛出异常
        """
        pass

    def is_available(self) -> bool:
        """检查搜索引擎是否可用"""
        return self.enabled

    def get_name(self) -> str:
        """获取搜索引擎名称"""
        return self.__class__.__name__
