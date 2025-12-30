"""Tavily AI 搜索引擎实现"""
import logging
from typing import List, Dict, Any
from backend.services.search.base import BaseSearchProvider, SearchResult, SearchQuery

logger = logging.getLogger(__name__)


class TavilySearchProvider(BaseSearchProvider):
    """Tavily AI 搜索引擎（需要 API Key）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("Tavily 需要 api_key 配置")

        try:
            from tavily import TavilyClient
            self.client = TavilyClient(api_key=self.api_key)
        except ImportError:
            raise ValueError(
                "tavily-python 包未安装\n"
                "解决方案：\n"
                "1. 运行: uv pip install tavily-python\n"
                "2. 或: pip install tavily-python"
            )

    def search(self, query: SearchQuery) -> List[SearchResult]:
        """执行 Tavily 搜索"""
        try:
            logger.info(f"使用 Tavily 搜索: {query.query[:50]}...")

            response = self.client.search(
                query=query.query,
                max_results=self.max_results,
                search_depth="basic",
                include_answer=False,
                include_raw_content=False
            )

            results = []
            for item in response.get('results', []):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('content', '')[:500],
                    content=item.get('content', ''),
                    source='Tavily',
                    score=item.get('score', 1.0)
                ))

            logger.info(f"Tavily 搜索完成，获得 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"Tavily 搜索失败: {str(e)}", exc_info=True)
            return []
