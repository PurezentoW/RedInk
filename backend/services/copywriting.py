import json
import logging
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
from backend.utils.text_client import get_text_chat_client

logger = logging.getLogger(__name__)


class CopywritingService:
    """文案生成服务类"""

    def __init__(self):
        logger.debug("初始化 CopywritingService...")
        self.text_config = self._load_text_config()
        self.client = self._get_client()
        self.prompt_template = self._load_prompt_template()
        logger.info(f"CopywritingService 初始化完成，使用服务商: {self.text_config.get('active_provider')}")

    def _load_text_config(self) -> dict:
        """加载文本生成配置"""
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
        """根据配置获取客户端"""
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

    def _load_prompt_template(self) -> str:
        """加载文案生成提示词模板"""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "copywriting_prompt.txt"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_outline_summary(self, outline: Dict[str, Any]) -> str:
        """从大纲中提取概要信息"""
        pages = outline.get("pages", [])

        if not pages:
            return "（无大纲内容）"

        summary_parts = []
        # 只取前3页作为概要
        for page in pages[:3]:
            page_type = page.get("type", "")
            content = page.get("content", "")

            # 提取页面标题和关键内容（限制长度）
            if page_type == "cover":
                summary_parts.append(f"封面：{content[:150]}...")
            else:
                summary_parts.append(f"内容页：{content[:150]}...")

        return "\n".join(summary_parts)

    def _parse_copywriting(self, copywriting_text: str) -> Dict[str, Any]:
        """
        解析 AI 返回的文案（支持多标题）

        新JSON格式：
        {
          "titles": ["标题1", "标题2", "标题3"],
          "copywriting": "正文内容...",
          "tags": ["标签1", "标签2"]
        }

        旧格式（降级兼容）：
        标题：笔记标题

        正文：
        摘要式介绍内容...

        标签：#标签1 #标签2 #标签3
        """
        result = {
            "title": "",      # 当前选中的标题（默认第一个）
            "titles": [],     # 所有备选标题数组
            "content": "",
            "tags": []
        }

        # 尝试解析JSON格式（新格式）
        try:
            json_match = re.search(r'```json\s*(.+?)\s*```', copywriting_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)

                # 提取标题数组
                if "titles" in data and isinstance(data["titles"], list):
                    result["titles"] = [t.strip() for t in data["titles"] if t.strip()]
                    # 默认选中第一个标题
                    result["title"] = result["titles"][0] if result["titles"] else ""
                    logger.debug(f"JSON解析到 {len(result['titles'])} 个标题")
                else:
                    # 兼容旧JSON格式（只有单个title字段）
                    if "title" in data:
                        single_title = data["title"].strip()
                        result["titles"] = [single_title]
                        result["title"] = single_title

                # 提取正文
                result["content"] = data.get("copywriting", "")

                # 提取标签
                tags_data = data.get("tags", [])
                if isinstance(tags_data, list):
                    result["tags"] = tags_data
                elif isinstance(tags_data, str):
                    # 如果tags是字符串，尝试提取
                    result["tags"] = re.findall(r'#(\S+)', tags_data)

                logger.debug(f"文案JSON解析成功: title={result['title'][:30] if result['title'] else 'empty'}..., tags={result['tags']}")
                return result

        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败，降级到旧格式解析: {e}")
        except Exception as e:
            logger.warning(f"JSON解析异常，降级到旧格式解析: {e}")

        # 降级：旧格式解析（正则匹配）
        # 提取标题
        title_match = re.search(r'标题[：:]\s*(.+?)(?:\n|$)', copywriting_text)
        if title_match:
            single_title = title_match.group(1).strip()
            result["titles"] = [single_title]
            result["title"] = single_title
        else:
            # 备选模式：匹配第一行
            lines = copywriting_text.strip().split('\n')
            if lines:
                single_title = lines[0].strip()
                result["titles"] = [single_title]
                result["title"] = single_title

        # 提取正文
        content_match = re.search(
            r'正文[：:]\s*\n+(.+?)(?:\n标签[：:]|$)',
            copywriting_text,
            re.DOTALL
        )
        if content_match:
            result["content"] = content_match.group(1).strip()
        else:
            # 备选模式：提取标题后的所有文本（除了标签行）
            text_without_title = re.sub(r'标题[：:]\s*.+\n', '', copywriting_text)
            text_without_tags = re.split(r'标签[：:]', text_without_title)[0].strip()
            result["content"] = text_without_tags

        # 提取标签
        tags_match = re.search(r'标签[：:]\s*(.+)', copywriting_text)
        if tags_match:
            tags_text = tags_match.group(1)
            # 匹配 #标签 格式
            result["tags"] = re.findall(r'#(\S+)', tags_text)
        else:
            # 备选模式：在整个文本中搜索 #标签
            result["tags"] = re.findall(r'#(\S+)', copywriting_text)

        logger.debug(f"文案旧格式解析完成: title={result['title'][:30] if result['title'] else 'empty'}..., tags={result['tags']}")
        return result

    def generate_copywriting_stream(
        self,
        topic: str,
        outline: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式生成文案

        Args:
            topic: 主题
            outline: 大纲数据 {raw, pages}

        Yields:
            SSE事件字典
        """
        try:
            logger.info(f"开始流式生成文案: topic={topic[:50]}...")

            # 构建 prompt
            prompt = self._build_prompt(topic, outline)

            # 从配置中获取模型参数
            active_provider = self.text_config.get('active_provider', 'google_gemini')
            providers = self.text_config.get('providers', {})
            provider_config = providers.get(active_provider, {})

            model = provider_config.get('model', 'gemini-2.0-flash-exp')
            temperature = provider_config.get('temperature', 1.0)
            max_output_tokens = provider_config.get('max_output_tokens', 8000)

            # 发送开始事件
            yield {
                "event": "progress",
                "data": {
                    "status": "starting",
                    "message": "正在生成文案..."
                }
            }

            logger.info(f"调用流式文本生成 API: model={model}, temperature={temperature}")

            # 调用流式生成
            stream_generator = self.client.generate_text(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                stream=True
            )

            # 累积文本
            accumulated_text = ""

            for chunk in stream_generator:
                accumulated_text += chunk

                # 发送文本块事件（打字机效果）
                yield {
                    "event": "text",
                    "data": {
                        "chunk": chunk,
                        "accumulated": accumulated_text
                    }
                }

            logger.debug(f"文案生成完成，文本长度: {len(accumulated_text)} 字符")

            # 解析文案
            parsed_copywriting = self._parse_copywriting(accumulated_text)

            # 发送完成事件
            yield {
                "event": "complete",
                "data": {
                    "raw": accumulated_text,
                    "title": parsed_copywriting["title"],
                    "titles": parsed_copywriting["titles"],
                    "content": parsed_copywriting["content"],
                    "tags": parsed_copywriting["tags"]
                }
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"文案生成失败: {error_msg}")

            # 发送错误事件
            yield {
                "event": "error",
                "data": {
                    "error": error_msg
                }
            }

    def _build_prompt(self, topic: str, outline: Dict[str, Any]) -> str:
        """构建文案生成 prompt"""
        # 提取大纲概要
        outline_summary = self._extract_outline_summary(outline)

        # 填充模板
        prompt = self.prompt_template.format(
            topic=topic,
            outline=outline_summary
        )

        return prompt


def get_copywriting_service() -> CopywritingService:
    """
    获取文案生成服务实例
    每次调用都创建新实例以确保配置是最新的
    """
    return CopywritingService()
