"""URL 和域名工具函数"""
from urllib.parse import urlparse
from typing import Optional


# 常见网站域名到名称的映射
DOMAIN_TO_NAME = {
    # 中文网站
    'zhihu.com': '知乎',
    'bilibili.com': '哔哩哔哩',
    'weibo.com': '微博',
    'toutiao.com': '今日头条',
    'csdn.net': 'CSDN',
    'jianshu.com': '简书',
    'juejin.cn': '掘金',
    'segmentfault.com': 'SegmentFault',
    'github.com': 'GitHub',
    'gitee.com': 'Gitee',
    'baidu.com': '百度',
    'mp.weixin.qq.com': '微信公众号',
    'weixin.qq.com': '微信',

    # 国际网站
    'google.com': 'Google',
    'youtube.com': 'YouTube',
    'wikipedia.org': '维基百科',
    'reddit.com': 'Reddit',
    'medium.com': 'Medium',
    'stackoverflow.com': 'Stack Overflow',
    'github.com': 'GitHub',
    'twitter.com': 'X (Twitter)',
    'x.com': 'X (Twitter)',
    'linkedin.com': 'LinkedIn',
    'quora.com': 'Quora',

    # 新闻媒体
    'people.com.cn': '人民网',
    'xinhuanet.com': '新华网',
    'cctv.com': '央视网',
    'ifeng.com': '凤凰网',
    'sina.com.cn': '新浪网',
    '163.com': '网易',
    'qq.com': '腾讯网',
    'sohu.com': '搜狐',
    'thepaper.cn': '澎湃新闻',

    # 电商平台
    'taobao.com': '淘宝',
    'tmall.com': '天猫',
    'jd.com': '京东',
    'pinduoduo.com': '拼多多',
    'douyin.com': '抖音',
    'kuaishou.com': '快手',

    # 技术社区
    'cnblogs.com': '博客园',
    'oschina.net': 'OSChina',
    'infoq.cn': 'InfoQ',
    '51cto.com': '51CTO',

    # 其他
    'douban.com': '豆瓣',
    'zhihuishu.com': '知乎',
}


def extract_domain(url: str) -> Optional[str]:
    """从 URL 中提取域名

    Args:
        url: 完整的 URL 地址

    Returns:
        域名，如 'zhihu.com'，如果解析失败返回 None

    Examples:
        >>> extract_domain('https://www.zhihu.com/question/123')
        'zhihu.com'
        >>> extract_domain('https://bilibili.com/video/123')
        'bilibili.com'
        >>> extract_domain('https://m.douban.com/')
        'douban.com'
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # 移除常见的子域名前缀
        prefixes_to_remove = ['www.', 'm.', 'mobile.', 'wap.']
        for prefix in prefixes_to_remove:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
                break

        # 移除端口号
        if ':' in domain:
            domain = domain.split(':')[0]

        return domain
    except Exception:
        return None


def get_website_name(url: str, fallback: bool = True) -> str:
    """从 URL 中提取网站名称

    Args:
        url: 完整的 URL 地址
        fallback: 如果找不到映射，是否返回域名作为备选

    Returns:
        网站名称，如 '知乎'、'哔哩哔哩'

    Examples:
        >>> get_website_name('https://www.zhihu.com/question/123')
        '知乎'
        >>> get_website_name('https://example.com/page')
        'example.com'
    """
    domain = extract_domain(url)

    if not domain:
        return '未知来源'

    # 查找映射
    if domain in DOMAIN_TO_NAME:
        return DOMAIN_TO_NAME[domain]

    # 如果没有映射，返回域名（带 fallback）或直接返回
    if fallback:
        return domain
    else:
        return '未知来源'


def get_website_favicon_url(url: str) -> str:
    """获取网站 favicon 的 URL（使用 Google 服务）

    Args:
        url: 网站 URL

    Returns:
        favicon URL
    """
    domain = extract_domain(url)
    if not domain:
        return ''

    return f'https://www.google.com/s2/favicons?domain={domain}&sz=32'
