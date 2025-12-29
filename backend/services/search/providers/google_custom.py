"""Google Custom Search API 实现"""
import logging
import requests
from typing import List, Dict, Any
from backend.services.search.base import BaseSearchProvider, SearchResult, SearchQuery

logger = logging.getLogger(__name__)


class GoogleCustomSearchProvider(BaseSearchProvider):
    """Google Custom Search API 搜索引擎"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.search_engine_id = config.get('search_engine_id')
        self.params = config.get('params', {})

        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Custom Search 配置不完整，搜索引擎已禁用")
            self.enabled = False

    def search(self, query: SearchQuery) -> List[SearchResult]:
        """执行 Google Custom Search"""
        if not self.is_available():
            raise Exception("Google Custom Search 未配置或已禁用")

        try:
            logger.info(f"使用 Google Custom Search 搜索: {query.query[:50]}...")

            # 构建请求参数
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query.query,
                'num': min(self.max_results, 10),  # Google 限制最多 10
                'safe': self.params.get('safe', 'active'),
                'gl': self.params.get('gl', query.region),
                'hl': self.params.get('hl', query.language)
            }

            # 发送请求
            response = requests.get(
                'https://www.googleapis.com/customsearch/v1',
                params=params,
                timeout=self.timeout
            )

            if response.status_code != 200:
                error_msg = response.json().get('error', {}).get('message', '未知错误')
                raise Exception(f"Google API 错误: {error_msg}")

            data = response.json()

            # 解析结果
            results = []
            for item in data.get('items', []):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    content='',  # 稍后获取完整内容
                    source='Google',
                    score=1.0
                ))

            logger.info(f"Google Custom Search 完成，获得 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"Google Custom Search 失败: {str(e)}")
            raise
