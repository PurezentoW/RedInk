"""DuckDuckGo 搜索引擎实现（免费）"""
import logging
from typing import List, Dict, Any
from ddgs import DDGS
from backend.services.search.base import BaseSearchProvider, SearchResult, SearchQuery
from backend.services.search.url_utils import get_website_name

logger = logging.getLogger(__name__)


class DuckDuckGoSearchProvider(BaseSearchProvider):
    """DuckDuckGo 搜索引擎（免费，无需 API Key）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 使用新的 ddgs 包，添加超时设置
        timeout = self.config.get('timeout', 30)
        self.ddgs = DDGS(timeout=timeout)

    def search(self, query: SearchQuery) -> List[SearchResult]:
        """执行 DuckDuckGo 搜索"""
        try:
            logger.info(f"使用 DuckDuckGo 搜索: {query.query[:50]}...")

            results = []
            # 使用 text 方法进行搜索，添加更多参数避免被封禁
            search_response = self.ddgs.text(
                query.query,
                max_results=self.max_results,
                region=query.region or "cn-zh",  # 默认中文区域
            )

            if not search_response:
                logger.warning("DuckDuckGo 搜索未返回结果")
                return []

            for item in search_response:
                url = item.get('link', '')
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=url,
                    snippet=item.get('body', ''),
                    content='',  # 稍后获取完整内容
                    source=get_website_name(url),  # 使用网站名称而不是搜索引擎名称
                    score=1.0
                ))

            logger.info(f"DuckDuckGo 搜索完成，获得 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo 搜索失败: {str(e)}", exc_info=True)
            # 不抛出异常，而是返回空列表，让系统能够继续运行
            return []
