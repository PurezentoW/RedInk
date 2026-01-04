"""
大纲生成相关 API 路由

包含功能：
- 生成大纲（支持图片上传）
- 流式生成大纲（SSE）
"""

import time
import base64
import json
import logging
from flask import Blueprint, request, jsonify, Response
from backend.services.outline import get_outline_service
from .utils import log_request, log_error

logger = logging.getLogger(__name__)


def create_outline_blueprint():
    """创建大纲路由蓝图（工厂函数，支持多次调用）"""
    outline_bp = Blueprint('outline', __name__)

    @outline_bp.route('/outline/stream', methods=['POST'])
    def generate_outline_stream():
        """
        流式生成大纲（SSE）

        请求格式：
        1. multipart/form-data（带图片文件）
           - topic: 主题文本
           - images: 图片文件列表

        2. application/json（无图片或 base64 图片）
           - topic: 主题文本
           - images: base64 编码的图片数组（可选）

        返回：SSE 事件流
        - progress: 开始生成
        - text: 文本块（打字机效果）
        - complete: 生成完成
        - error: 错误
        """
        start_time = time.time()

        try:
            # 解析请求数据
            topic, images, use_search = _parse_outline_request()

            log_request('/outline/stream', {'topic': topic, 'images': images, 'use_search': use_search})

            # 验证必填参数
            if not topic:
                logger.warning("流式大纲生成请求缺少 topic 参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：topic 不能为空。\n请提供要生成图文的主题内容。"
                }), 400

            # 调用大纲生成服务
            logger.info(f"🔄 开始流式生成大纲，主题: {topic[:50]}...")
            outline_service = get_outline_service()

            def generate():
                """SSE 事件生成器"""
                for event in outline_service.generate_outline_stream(topic, images, use_search):
                    event_type = event["event"]
                    event_data = event["data"]

                    # 格式化为 SSE 格式
                    yield f"event: {event_type}\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            # 返回 SSE 流
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                }
            )

        except Exception as e:
            log_error('/outline/stream', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"流式大纲生成异常。\n错误详情: {error_msg}\n建议：检查后端日志获取更多信息"
            }), 500

    @outline_bp.route('/outline', methods=['POST'])
    def generate_outline():
        """
        生成大纲（支持图片上传）

        请求格式：
        1. multipart/form-data（带图片文件）
           - topic: 主题文本
           - images: 图片文件列表

        2. application/json（无图片或 base64 图片）
           - topic: 主题文本
           - images: base64 编码的图片数组（可选）

        返回：
        - success: 是否成功
        - outline: 原始大纲文本
        - pages: 解析后的页面列表
        """
        start_time = time.time()

        try:
            # 解析请求数据
            topic, images, use_search = _parse_outline_request()

            log_request('/outline', {'topic': topic, 'images': images, 'use_search': use_search})

            # 验证必填参数
            if not topic:
                logger.warning("大纲生成请求缺少 topic 参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：topic 不能为空。\n请提供要生成图文的主题内容。"
                }), 400

            # 调用大纲生成服务
            logger.info(f"🔄 开始生成大纲，主题: {topic[:50]}...")
            outline_service = get_outline_service()
            result = outline_service.generate_outline(topic, images if images else None, use_search)

            # 记录结果
            elapsed = time.time() - start_time
            if result["success"]:
                logger.info(f"✅ 大纲生成成功，耗时 {elapsed:.2f}s，共 {len(result.get('pages', []))} 页")
                return jsonify(result), 200
            else:
                logger.error(f"❌ 大纲生成失败: {result.get('error', '未知错误')}")
                return jsonify(result), 500

        except Exception as e:
            log_error('/outline', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"大纲生成异常。\n错误详情: {error_msg}\n建议：检查后端日志获取更多信息"
            }), 500

    @outline_bp.route('/copywriting/stream', methods=['POST'])
    def generate_copywriting_stream():
        """
        流式生成文案（SSE）

        请求格式：
        - application/json
          - topic: 原始主题
          - outline: 大纲数据 {raw, pages}

        返回：SSE 事件流
        - progress: 开始生成
        - text: 文本块（打字机效果）
        - complete: 生成完成（包含 title, content, tags）
        - error: 错误
        """
        try:
            data = request.get_json()
            topic = data.get('topic')
            outline = data.get('outline')

            if not topic or not outline:
                logger.warning("文案生成请求缺少必要参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：topic 和 outline 不能为空"
                }), 400

            log_request('/copywriting/stream', {'topic': topic})

            logger.info(f"🔄 开始流式生成文案，主题: {topic[:50]}...")

            from backend.services.copywriting import get_copywriting_service
            copywriting_service = get_copywriting_service()

            def generate():
                """SSE 事件生成器"""
                for event in copywriting_service.generate_copywriting_stream(
                    topic=topic,
                    outline=outline
                ):
                    event_type = event["event"]
                    event_data = event["data"]

                    # 格式化为 SSE 格式
                    yield f"event: {event_type}\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            # 返回 SSE 流
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                }
            )

        except Exception as e:
            log_error('/copywriting/stream', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"文案生成异常。\n错误详情: {error_msg}\n建议：检查后端日志获取更多信息"
            }), 500

    @outline_bp.route('/outline/modify/stream', methods=['POST'])
    def modify_outline_stream():
        """
        流式修改大纲（SSE）

        请求格式：
        - application/json
          - topic: 原始主题
          - current_outline: {raw: str, pages: []}
          - instruction: 修改指令

        返回：SSE 事件流
        - progress: 开始修改
        - text: 文本块（打字机效果）
        - complete: 修改完成
        - error: 错误
        """
        start_time = time.time()

        try:
            # 解析请求数据
            data = request.get_json()

            if not data:
                logger.warning("大纲修改请求缺少JSON数据")
                return jsonify({
                    "success": False,
                    "error": "参数错误：请求体不能为空。\n请提供topic、current_outline和instruction参数。"
                }), 400

            topic = data.get('topic')
            current_outline = data.get('current_outline')
            instruction = data.get('instruction')

            # 验证必填参数
            if not topic:
                logger.warning("大纲修改请求缺少 topic 参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：topic 不能为空。"
                }), 400

            if not current_outline:
                logger.warning("大纲修改请求缺少 current_outline 参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：current_outline 不能为空。"
                }), 400

            if not instruction:
                logger.warning("大纲修改请求缺少 instruction 参数")
                return jsonify({
                    "success": False,
                    "error": "参数错误：instruction 不能为空。"
                }), 400

            log_request('/outline/modify/stream', {
                'topic': topic,
                'instruction': instruction,
                'current_pages': len(current_outline.get('pages', []))
            })

            # 调用大纲修改服务
            logger.info(f"🔄 开始流式修改大纲，主题: {topic[:50]}..., 指令: {instruction[:50]}...")
            from backend.services.outline_modify import get_outline_modify_service
            modify_service = get_outline_modify_service()

            def generate():
                """SSE 事件生成器"""
                for event in modify_service.modify_outline_stream(topic, current_outline, instruction):
                    event_type = event["event"]
                    event_data = event["data"]

                    # 格式化为 SSE 格式
                    yield f"event: {event_type}\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            # 返回 SSE 流
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no',
                }
            )

        except Exception as e:
            log_error('/outline/modify/stream', e)
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"大纲修改异常。\n错误详情: {error_msg}\n建议：检查后端日志获取更多信息"
            }), 500

    return outline_bp


def _parse_outline_request():
    """
    解析大纲生成请求

    支持两种格式：
    1. multipart/form-data - 用于文件上传
    2. application/json - 用于 base64 图片

    返回：
        tuple: (topic, images, use_search) - 主题、图片列表和是否使用搜索
    """
    # 检查是否是 multipart/form-data（带图片文件）
    if request.content_type and 'multipart/form-data' in request.content_type:
        topic = request.form.get('topic')
        images = []
        use_search = request.form.get('use_search', 'false').lower() == 'true'

        # 获取上传的图片文件
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    image_data = file.read()
                    images.append(image_data)

        return topic, images, use_search

    # JSON 请求（无图片或 base64 图片）
    data = request.get_json()
    topic = data.get('topic')
    images = []
    use_search = data.get('use_search', False)

    # 支持 base64 格式的图片
    images_base64 = data.get('images', [])
    if images_base64:
        for img_b64 in images_base64:
            # 移除可能的 data URL 前缀
            if ',' in img_b64:
                img_b64 = img_b64.split(',')[1]
            images.append(base64.b64decode(img_b64))

    return topic, images, use_search
