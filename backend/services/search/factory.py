"""搜索引擎工厂"""
import logging
from typing import Dict, Any
from backend.services.search.base import BaseSearchProvider

logger = logging.getLogger(__name__)


def get_search_provider(config: Dict[str, Any]) -> BaseSearchProvider:
    """工厂方法：根据配置创建搜索引擎提供商

    Args:
        config: 搜索引擎配置字典

    Returns:
        搜索引擎实例

    Raises:
        ValueError: 不支持的搜索引擎类型
    """
    provider_type = config.get('type')

    try:
        if provider_type == 'duckduckgo':
            from backend.services.search.providers.duckduckgo import DuckDuckGoSearchProvider
            return DuckDuckGoSearchProvider(config)

        elif provider_type == 'google_custom':
            from backend.services.search.providers.google_custom import GoogleCustomSearchProvider
            return GoogleCustomSearchProvider(config)

        elif provider_type == 'bing_search':
            from backend.services.search.providers.bing_search import BingSearchProvider
            return BingSearchProvider(config)

        elif provider_type == 'baidu_search':
            from backend.services.search.providers.baidu_search import BaiduSearchProvider
            return BaiduSearchProvider(config)

        elif provider_type == 'hybrid':
            from backend.services.search.providers.hybrid import HybridSearchProvider
            return HybridSearchProvider(config)

        else:
            raise ValueError(f"不支持的搜索引擎类型: {provider_type}")

    except ImportError as e:
        logger.error(f"导入搜索引擎模块失败: {str(e)}")
        raise ValueError(f"搜索引擎 {provider_type} 不可用")


def get_all_providers(configs: Dict[str, Any]) -> Dict[str, BaseSearchProvider]:
    """获取所有已配置的搜索引擎提供商

    Args:
        configs: 所有搜索引擎配置

    Returns:
        搜索引擎字典 {name: provider}
    """
    providers = {}

    for name, config in configs.items():
        try:
            provider = get_search_provider(config)
            if provider.is_available():
                providers[name] = provider
                logger.info(f"成功初始化搜索引擎: {name}")
        except Exception as e:
            logger.warning(f"初始化搜索引擎 {name} 失败: {str(e)}")

    return providers
