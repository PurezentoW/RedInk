"""DuckDuckGo 搜索引擎实现（免费）"""
import logging
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from backend.services.search.base import BaseSearchProvider, SearchResult, SearchQuery

logger = logging.getLogger(__name__)


class DuckDuckGoSearchProvider(BaseSearchProvider):
    """DuckDuckGo 搜索引擎（免费，无需 API Key）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ddgs = DDGS()

    def search(self, query: SearchQuery) -> List[SearchResult]:
        """执行 DuckDuckGo 搜索"""
        try:
            logger.info(f"使用 DuckDuckGo 搜索: {query.query[:50]}...")

            results = []
            search_response = self.ddgs.text(
                query.query,
                max_results=self.max_results,
                region=query.region,
                safesearch=query.safe_search.lower()
            )

            if not search_response:
                logger.warning("DuckDuckGo 搜索未返回结果")
                return []

            for item in search_response:
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('body', ''),
                    content='',  # 稍后获取完整内容
                    source='DuckDuckGo',
                    score=1.0
                ))

            logger.info(f"DuckDuckGo 搜索完成，获得 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo 搜索失败: {str(e)}")
            raise Exception(f"DuckDuckGo 搜索失败: {str(e)}")
