from playwright.sync_api import sync_playwright
import time
import random
import threading

def scrape_website(url):
    with sync_playwright() as p:
        # 启动浏览器（无头模式可改为headless=True）
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 导航到目标页面
        page.goto(url)
        print(f"当前页面标题: {page.title()}")

        # 示例：提取页面内容
        #content = page.inner_text("body")
        html = page.inner_html("body")
        # 移除await关键字，使用同步方式获取元素
        productList = page.locator('#search_nature_rg')
        print(f"content: {html[:200]}...")  # 限制输出长度，避免过多内容
        print(f"type of product: {type(productList)}")
        print(f"productList: {productList.count()}")
        #productList.for_each(lambda x: print(x))
        links = page.query_selector_all('#search_nature_rg p.name>a')
        for link in links:
            # 获取链接的文本和href属性
            text = link.text_content()
            href = link.get_attribute('href')
            print(f'Link Text: {text}, URL: {href}')
            thread = threading.Thread(target=scrape_details,args=("https:"+href,))
            thread.start()
            thread.join()

        # 保存数据到CSV
        # with open('output.csv', 'w', newline='', encoding='utf-8') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['链接', '内容摘要'])
        #     for link in links[:10]:  # 限制前10个链接
        #         writer.writerow([link, content[:100]])  # 内容摘要前100字符

        # 关闭资源
        context.close()
        browser.close()

def scrape_details(url):
    random_float = random.uniform(2, 6)
    print(random_float)
    time.sleep(random_float) #延迟2-6秒
    with sync_playwright() as p:
        # 启动浏览器（无头模式可改为headless=True）
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 导航到目标页面
        page.goto(url)
        print(f"当前页面标题: {page.title()}")


        # 示例：提取页面内容
        content = page.inner_text("body")
        html = page.inner_html("body")
        # 移除await关键字，使用同步方式获取元素

        # 保存数据到CSV
        # with open('output.csv', 'w', newline='', encoding='utf-8') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(['链接', '内容摘要'])
        #     for link in links[:10]:  # 限制前10个链接
        #         writer.writerow([link, content[:100]])  # 内容摘要前100字符

        # 关闭资源
        context.close()
        browser.close()

if __name__ == "__main__":
    target_url = "https://category.dangdang.com/cp01.41.05.03.00.00.html"
    scrape_website(target_url)