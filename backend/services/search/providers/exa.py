"""Exa.ai 搜索引擎实现"""
import logging
from typing import List, Dict, Any
from backend.services.search.base import BaseSearchProvider, SearchResult, SearchQuery

logger = logging.getLogger(__name__)


class ExaSearchProvider(BaseSearchProvider):
    """Exa.ai 搜索引擎（需要 API Key）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        if not self.api_key:
            raise ValueError("Exa.ai 需要 api_key 配置")

        try:
            from exa_py import Exa
            self.client = Exa(api_key=self.api_key)
        except ImportError:
            raise ValueError(
                "exa-py 包未安装\n"
                "解决方案：\n"
                "1. 运行: uv pip install exa-py\n"
                "2. 或: pip install exa-py"
            )

    def search(self, query: SearchQuery) -> List[SearchResult]:
        """执行 Exa 搜索"""
        try:
            logger.info(f"使用 Exa 搜索: {query.query[:50]}...")

            response = self.client.search_and_contents(
                query=query.query,
                num_results=self.max_results,
                use_autoprompt=True,
                text=True
            )

            results = []
            for item in response.results:
                results.append(SearchResult(
                    title=item.title or '',
                    url=item.url,
                    snippet=(item.text or '')[:500] if item.text else '',
                    content=item.text or '',
                    source='Exa',
                    score=item.score or 1.0
                ))

            logger.info(f"Exa 搜索完成，获得 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"Exa 搜索失败: {str(e)}", exc_info=True)
            return []
