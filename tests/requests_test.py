import requests
from bs4 import BeautifulSoup


def fetch_url(url, headers=None, timeout=10):
    """
    发送HTTP请求并返回响应内容
    :param url: 目标URL
    :param headers: 自定义请求头
    :param timeout: 超时时间(秒)
    :return: 网页内容或None
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(
            url,
            headers=headers if headers else default_headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None


def parse_html(html, selector='h2 a'):
    """
    解析HTML内容提取目标元素
    :param html: HTML内容
    :param selector: CSS选择器
    :return: 提取结果列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    return [element.text.strip() for element in soup.select(selector)]


if __name__ == '__main__':
    # 示例：抓取CSDN博客标题
    target_url = 'https://book.dangdang.com/children'
    html_content = fetch_url(target_url)

    print(html_content)

    if html_content:
        titles = parse_html(html_content)
        for idx, title in enumerate(titles[:5], 1):
            print(f"{idx}. {title}")