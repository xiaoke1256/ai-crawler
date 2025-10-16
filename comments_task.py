from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import random
import threading
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_PATH = os.path.join(WEB_DIR, "cookie.json")

# 连接MongoDB
client = MongoClient(MONGODB_URI)
db = client['crawler']
productsCollection = db['products']
commentsCollection = db['comments']

current_time = datetime.now()

#print(f"products: {data_list}")
def scrape_all_comments():
    with sync_playwright() as p:
        products = productsCollection.find(
            {"$or": [
                {"fetch_comments_time": {"$exists": False}},
                {"fetch_comments_time": {"$lt": current_time}}
            ]}
        )
        data_list = list(products)

        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=COOKIE_PATH)

        for data in data_list:
            #todo: 随机休眠一段时间
            try:
                print(f"开始爬取: {data['href']}")
                scrape_comments(context, data['href'], data['sku'])
            except Exception as e:
                print(f"错误: {e}")

        context.close()
        browser.close()


def scrape_comments(context,url,sku):
    if(url.startswith('//')):
        url = "https:"+url
    page = context.new_page()

    # 导航到目标页面
    page.goto(url)
    #page.wait_for_load_state('networkidle')
    print(f"当前页面标题: {page.title()}")

    tab = page.query_selector('#comment_tab')
    #tab.scroll_into_view_if_needed()
    page.evaluate('''() => {
           const element = document.querySelector('#comment_tab');
           element.scrollIntoView({ behavior: 'auto', block: 'center' });
           element.click();
       }''')

    #print("滚动完成")

    #模拟点击评论条数按钮
    tab.click()
    print("点击评论完成")
    #点击后等待评论显示出来
    time.sleep(10/1000)
    print('点击了评论条数')
    #page.locator("#comment_num_tab").scroll_into_view_if_needed()
    #page.wait_for_selector('#comment_num_tab')


    #commentsList = []

    #点击好评
    page.click('#comment_num_tab span[data-type="2"]')
    time.sleep(1 / 1000)
    page.wait_for_selector('#comment_list')

    # 提取评论的文本
    comments =page.query_selector_all('#comment_list div.describe_detail a')
    for comment in comments:
        href = comment.get_attribute('href')
        comment_text = comment.text_content()
        print(f'href: {href}')
        print(f'评论文本: {comment_text.strip()}')
        commentObject = {
            "href": href,
            "sku": sku,
            "text": comment_text.strip()
        }
        commentsCollection.update_one({"href": href}, {"$set":{"update_time": current_time,**commentObject},
                                                      "$setOnInsert": {"create_time": current_time}}, upsert=True)

    # 点击中评
    page.click('#comment_num_tab span[data-type="3"]')
    time.sleep(1 / 1000)
    page.wait_for_selector('#comment_list')

    # 提取评论的文本
    comments = page.query_selector_all('#comment_list div.describe_detail a')
    for comment in comments:
        href = comment.get_attribute('href')
        print(f'href: {href}')
        comment_text = comment.text_content()
        print(f'评论文本: {comment_text.strip()}')
        commentObject = {
            "href": href,
            "sku": sku,
            "text": comment_text.strip()
        }
        commentsCollection.update_one({"href": href}, {"$set": {"update_time": current_time, **commentObject},
                                                       "$setOnInsert": {"create_time": current_time}}, upsert=True)

    # 点击差评
    page.click('#comment_num_tab span[data-type="4"]')
    time.sleep(1 / 1000)
    page.wait_for_selector('#comment_list')

    # 提取评论的文本
    comments = page.query_selector_all('#comment_list div.describe_detail a')
    for comment in comments:
        href = comment.get_attribute('href')
        print(f'href: {href}')
        comment_text = comment.text_content()
        print(f'评论文本: {comment_text.strip()}')
        commentObject = {
            "href": href,
            "sku": sku,
            "text": comment_text.strip()
        }
        commentsCollection.update_one({"href": href}, {"$set": {"update_time": current_time, **commentObject},
                                                       "$setOnInsert": {"create_time": current_time}}, upsert=True)

    productsCollection.update_one({"sku":sku}, {"$set":{"fetch_comments_time":current_time}})

if __name__ == "__main__":
    scrape_all_comments()
