from playwright.sync_api import sync_playwright
import csv


def scrape_website(url):
    with sync_playwright() as p:
        # 启动浏览器（无头模式可改为headless=True）
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 导航到目标页面
        page.goto(url)
        print(f"当前页面标题: {page.title()}")

        # 示例：抓取所有链接
        links = page.eval_on_selector_all(
            "a",
            "elements => elements.map(e => e.href)"
        )

        # 示例：提取页面内容
        content = page.inner_text("body")

        # 保存数据到CSV
        with open('output.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['链接', '内容摘要'])
            for link in links[:10]:  # 限制前10个链接
                writer.writerow([link, content[:100]])  # 内容摘要前100字符

        # 关闭资源
        context.close()
        browser.close()


if __name__ == "__main__":
    target_url = "https://book.dangdang.com/children"  # 替换为目标网站
    scrape_website(target_url)