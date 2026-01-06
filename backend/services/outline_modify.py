"""
大纲修改服务

提供AI辅助修改大纲功能，支持流式输出
"""

import logging
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
from backend.utils.text_client import get_text_chat_client

logger = logging.getLogger(__name__)


class OutlineModifyService:
    def __init__(self):
        logger.debug("初始化 OutlineModifyService...")
        self.text_config = self._load_text_config()
        self.client = self._get_client()
        self.modify_prompt_template = self._load_modify_prompt_template()
        logger.info(f"OutlineModifyService 初始化完成，使用服务商: {self.text_config.get('active_provider')}")

    def _load_text_config(self) -> dict:
        """加载文本生成配置（复用OutlineService的逻辑）"""
        config_path = Path(__file__).parent.parent.parent / 'text_providers.yaml'
        logger.debug(f"加载文本配置: {config_path}")

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                logger.debug(f"文本配置加载成功: active={config.get('active_provider')}")
                return config
            except yaml.YAMLError as e:
                logger.error(f"文本配置 YAML 解析失败: {e}")
                raise ValueError(
                    f"文本配置文件格式错误: text_providers.yaml\n"
                    f"YAML 解析错误: {e}\n"
                    "解决方案：检查 YAML 缩进和语法"
                )

        logger.warning("text_providers.yaml 不存在，使用默认配置")
        # 默认配置
        return {
            'active_provider': 'google_gemini',
            'providers': {
                'google_gemini': {
                    'type': 'google_gemini',
                    'model': 'gemini-2.0-flash-exp',
                    'temperature': 1.0,
                    'max_output_tokens': 8000
                }
            }
        }

    def _get_client(self):
        """根据配置获取客户端（复用OutlineService的逻辑）"""
        active_provider = self.text_config.get('active_provider', 'google_gemini')
        providers = self.text_config.get('providers', {})

        if not providers:
            logger.error("未找到任何文本生成服务商配置")
            raise ValueError(
                "未找到任何文本生成服务商配置。\n"
                "解决方案：\n"
                "1. 在系统设置页面添加文本生成服务商\n"
                "2. 或手动编辑 text_providers.yaml 文件"
            )

        if active_provider not in providers:
            available = ', '.join(providers.keys())
            logger.error(f"文本服务商 [{active_provider}] 不存在，可用: {available}")
            raise ValueError(
                f"未找到文本生成服务商配置: {active_provider}\n"
                f"可用的服务商: {available}\n"
                "解决方案：在系统设置中选择一个可用的服务商"
            )

        provider_config = providers.get(active_provider, {})

        if not provider_config.get('api_key'):
            logger.error(f"文本服务商 [{active_provider}] 未配置 API Key")
            raise ValueError(
                f"文本服务商 {active_provider} 未配置 API Key\n"
                "解决方案：在系统设置页面编辑该服务商，填写 API Key"
            )

        logger.info(f"使用文本服务商: {active_provider} (type={provider_config.get('type')})")
        return get_text_chat_client(provider_config)

    def _load_modify_prompt_template(self) -> str:
        """加载修改提示词模板"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "outline_modify_prompt.txt"
        )
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"修改提示词模板不存在: {prompt_path}")
            # 返回备用提示词
            return """你是一个小红书内容优化专家。用户已经有一个大纲初稿，现在需要你根据指令进行调整。

【原始主题】
{topic}

【当前大纲】
{current_outline}

【用户修改指令】
{instruction}

请直接输出修改后的大纲，使用 <page> 标签分割页面。
"""

    def _parse_outline(self, outline_text: str) -> List[Dict[str, Any]]:
        """
        解析大纲文本为页面列表（复用OutlineService的_parse_outline方法）

        Args:
            outline_text: 大纲文本

        Returns:
            页面列表
        """
        # 按 <page> 分割页面（兼容旧的 --- 分隔符）
        if '<page>' in outline_text:
            pages_raw = re.split(r'<page>', outline_text, flags=re.IGNORECASE)
        else:
            # 向后兼容：如果没有 <page> 则使用 ---
            pages_raw = outline_text.split("---")

        pages = []

        for index, page_text in enumerate(pages_raw):
            page_text = page_text.strip()
            if not page_text:
                continue

            page_type = "content"
            type_match = re.match(r"\[(\S+)\]", page_text)
            if type_match:
                type_cn = type_match.group(1)
                type_mapping = {
                    "封面": "cover",
                    "内容": "content",
                    "总结": "summary",
                }
                page_type = type_mapping.get(type_cn, "content")

            pages.append({
                "index": index,
                "type": page_type,
                "content": page_text
            })

        return pages

    def _generate_modify_summary(self, original_pages: List[Dict], modified_pages: List[Dict], instruction: str) -> str:
        """
        生成修改摘要

        Args:
            original_pages: 原始页面列表
            modified_pages: 修改后的页面列表
            instruction: 用户修改指令

        Returns:
            修改摘要文本
        """
        original_count = len(original_pages)
        modified_count = len(modified_pages)

        # 分析页面变化
        if modified_count < original_count:
            return f"从 {original_count} 页精简到 {modified_count} 页"
        elif modified_count > original_count:
            return f"从 {original_count} 页扩展到 {modified_count} 页"
        else:
            return f"保持 {original_count} 页，优化了内容"

    def modify_outline_stream(
        self,
        topic: str,
        current_outline: Dict[str, Any],
        instruction: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式修改大纲

        Args:
            topic: 原始主题
            current_outline: 当前大纲 {raw: str, pages: []}
            instruction: 用户修改指令

        Yields:
            SSE事件字典
            - event: "progress" | "text" | "complete" | "error"
            - data: 事件数据
        """
        try:
            logger.info(f"开始流式修改大纲: topic={topic[:50]}..., instruction={instruction[:50]}...")

            # 获取当前大纲文本
            current_outline_text = current_outline.get('raw', '')
            current_pages = current_outline.get('pages', [])

            logger.info(f"接收到的大纲数据: raw_length={len(current_outline_text)}, pages_count={len(current_pages)}")

            # 降级处理：如果 raw 为空，尝试从 pages 重建
            if not current_outline_text and current_pages:
                logger.info("raw 字段为空，尝试从 pages 重建大纲文本")
                current_outline_text = self._reconstruct_raw_from_pages(current_pages)
                logger.info(f"重建后的大纲文本长度: {len(current_outline_text)} 字符")

            if not current_outline_text:
                logger.error(f"当前大纲为空: raw_length={len(current_outline_text)}, pages_count={len(current_pages)}")
                yield {
                    "event": "error",
                    "data": {
                        "error": "当前大纲为空，无法修改。请先生成大纲内容。"
                    }
                }
                return

            # 构建修改提示词
            prompt = self.modify_prompt_template.format(
                topic=topic,
                current_outline=current_outline_text,
                instruction=instruction
            )

            logger.debug(f"修改提示词长度: {len(prompt)} 字符")

            # 从配置中获取模型参数
            active_provider = self.text_config.get('active_provider', 'google_gemini')
            providers = self.text_config.get('providers', {})
            provider_config = providers.get(active_provider, {})

            model = provider_config.get('model', 'gemini-2.0-flash-exp')
            temperature = provider_config.get('temperature', 1.0)
            max_output_tokens = provider_config.get('max_output_tokens', 8000)

            logger.info(f"调用流式文本修改 API: model={model}, temperature={temperature}")

            # 发送开始事件
            yield {
                "event": "progress",
                "data": {
                    "status": "starting",
                    "message": "正在分析修改指令..."
                }
            }

            # 调用流式生成
            stream_generator = self.client.generate_text(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                images=None,
                stream=True  # 启用流式
            )

            # 累积文本
            accumulated_text = ""

            for chunk in stream_generator:
                accumulated_text += chunk

                # 发送文本块事件（打字机效果核心）
                yield {
                    "event": "text",
                    "data": {
                        "chunk": chunk,
                        "accumulated": accumulated_text
                    }
                }

            logger.debug(f"流式修改API返回文本长度: {len(accumulated_text)} 字符")

            # 生成完成后解析页面
            modified_pages = self._parse_outline(accumulated_text)
            logger.info(f"流式大纲修改完成，共 {len(modified_pages)} 页")

            # 生成修改摘要
            summary = self._generate_modify_summary(current_pages, modified_pages, instruction)

            # 发送完成事件
            yield {
                "event": "complete",
                "data": {
                    "outline": accumulated_text,
                    "pages": modified_pages,
                    "summary": summary
                }
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"流式大纲修改失败: {error_msg}")

            # 发送错误事件
            yield {
                "event": "error",
                "data": {
                    "error": error_msg
                }
            }

    def _reconstruct_raw_from_pages(self, pages: list) -> str:
        """
        从 pages 数组重建 raw 文本

        Args:
            pages: 页面数组，每个元素包含 {type, content}

        Returns:
            str: 重建后的 raw 文本
        """
        result_parts = []

        for page in pages:
            page_type = page.get('type', 'content')
            page_content = page.get('content', '').strip()

            # 添加类型标签
            type_labels = {
                'cover': '[封面]',
                'content': '[内容]',
                'summary': '[总结]'
            }
            type_label = type_labels.get(page_type, '[内容]')

            # 组装页面内容
            if page_content:
                result_parts.append(f"{type_label}\n{page_content}")

        # 用 <page> 标签连接
        return '\n\n<page>\n\n'.join(result_parts)


def get_outline_modify_service() -> OutlineModifyService:
    """
    获取大纲修改服务实例
    每次调用都创建新实例以确保配置是最新的
    """
    return OutlineModifyService()
