"""搜索服务 - 集成多个搜索引擎"""
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from backend.services.search.base import SearchQuery, SearchResult
from backend.services.search.factory import get_search_provider

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务，提供统一的搜索接口"""

    def __init__(self):
        self.config = self._load_search_config()
        self.active_provider_name = self.config.get('active_provider', 'duckduckgo')
        self.active_provider = self._get_active_provider()

    def _load_search_config(self) -> dict:
        """加载搜索配置文件"""
        config_path = Path(__file__).parent.parent / 'search_providers.yaml'

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                logger.info(f"搜索配置加载成功: active={config.get('active_provider')}")
                return config
            except Exception as e:
                logger.error(f"搜索配置加载失败: {str(e)}")

        # 默认配置
        logger.warning("使用默认搜索配置")
        return {
            'active_provider': 'duckduckgo',
            'providers': {
                'duckduckgo': {
                    'type': 'duckduckgo',
                    'max_results': 5,
                    'enabled': True
                }
            }
        }

    def _get_active_provider(self):
        """获取当前激活的搜索引擎"""
        providers_config = self.config.get('providers', {})
        active_config = providers_config.get(self.active_provider_name, {})

        try:
            provider = get_search_provider(active_config)
            if not provider.is_available():
                logger.warning(f"搜索引擎 {self.active_provider_name} 不可用")
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

            search_query = SearchQuery(
                query=query,
                max_results=max_results,
                timeout=self.config.get('search_config', {}).get('fallback', {}).get('timeout_seconds', 30)
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
