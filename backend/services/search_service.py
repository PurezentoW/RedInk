"""搜索服务 - 集成多个搜索引擎"""
import logging
from typing import List, Dict, Any
from backend.services.search.base import SearchQuery, SearchResult
from backend.services.search.factory import get_search_provider

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务，提供统一的搜索接口（单例模式）"""

    _instance = None
    _config = None
    active_provider_name = None
    active_provider = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.reload_config()

    @classmethod
    def reload_config(cls):
        """重新加载配置"""
        from backend.config import Config
        cls._config = Config.load_search_providers_config()
        cls.active_provider_name = cls._config.get('active_provider', 'duckduckgo')
        cls.active_provider = cls._get_active_provider()
        logger.info(f"搜索配置已重新加载: active={cls.active_provider_name}")

    @classmethod
    def _get_active_provider(cls):
        """获取当前激活的搜索引擎"""
        providers_config = cls._config.get('providers', {})
        active_config = providers_config.get(cls.active_provider_name, {})

        try:
            provider = get_search_provider(active_config)
            if not provider.is_available():
                logger.warning(f"搜索引擎 {cls.active_provider_name} 不可用")
                return None
            return provider
        except Exception as e:
            logger.error(f"初始化搜索引擎失败: {str(e)}")
            return None

    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """执行搜索

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            搜索结果字典
        """
        if not self.active_provider:
            return {
                'success': False,
                'error': '搜索引擎不可用，请检查配置'
            }

        try:
            logger.info(f"开始搜索: {query[:50]}...")

            # 从当前激活的 provider 配置中读取 timeout
            provider_config = self._config.get('providers', {}).get(self.active_provider_name, {})
            timeout = provider_config.get('timeout', 30)

            search_query = SearchQuery(
                query=query,
                max_results=max_results,
                timeout=timeout
            )

            results = self.active_provider.search(search_query)

            # 获取网页内容
            results_with_content = self._fetch_content(results)

            # 整理搜索内容
            research_content = []
            for result in results_with_content:
                if result.content:
                    research_content.append({
                        'title': result.title,
                        'url': result.url,
                        'snippet': result.snippet,
                        'content': result.content[:2000],  # 限制内容长度
                        'source': result.source
                    })

            logger.info(f"搜索完成，获得 {len(research_content)} 个有效结果")

            return {
                'success': True,
                'has_research': len(research_content) > 0,
                'research_content': research_content,
                'search_summary': self._generate_search_summary(research_content)
            }

        except Exception as e:
            logger.error(f"搜索执行失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'has_research': False
            }

    def _fetch_content(self, results: List[SearchResult]) -> List[SearchResult]:
        """获取网页完整内容"""
        # 简化实现：使用 snippet 作为 content
        # 完整实现可以使用 web_reader 或其他爬虫工具
        for result in results:
            if not result.content:
                result.content = result.snippet

        return results

    def _generate_search_summary(self, research_content: List[Dict]) -> str:
        """生成搜索内容摘要"""
        if not research_content:
            return ""

        # 简单摘要：列出所有标题
        titles = [item['title'] for item in research_content]
        return f"找到 {len(titles)} 条相关内容：" + "、".join(titles[:3])
