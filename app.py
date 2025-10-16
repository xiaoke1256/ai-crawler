from apscheduler.schedulers.blocking import BlockingScheduler
from .crawler_task import scrape_website
from .comments_task import scrape_all_comments
from .ai_task import label_comments
import datetime
import signal
import sys

# 爬取所有产品
def scrape_products():
    scrape_website("https://category.dangdang.com/cp01.41.05.03.00.00.html")
    print("爬取所有产品任务执行")

def scrape_comments():
    scrape_all_comments()
    print("爬取评论任务执行")

def run_ai():
    label_comments()

# 创建一个调度器实例：BlockingScheduler适用于大多数情况，因为它会阻塞主线程直到所有任务完成。
scheduler = BlockingScheduler()
scheduler.add_job(scrape_products, 'cron', hour=15, minute=29) # 每天15:29执行任务

scheduler.add_job(scrape_comments, 'cron', hour=18, minute=29) # 每天18:29执行任务

scheduler.add_job(label_comments, 'cron', hour=23, minute=29) # 每天23:29执行任务
scheduler.start()

# def signal_handler(sig, frame):
#     print('You pressed Ctrl+C!')
#     sys.exit(0)
#
# signal.signal(signal.SIGINT, signal_handler)
