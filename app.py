from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import signal
import sys

def task():
    print("任务执行")

# 创建一个调度器实例：BlockingScheduler适用于大多数情况，因为它会阻塞主线程直到所有任务完成。
scheduler = BlockingScheduler()
scheduler.add_job(task, 'cron', hour=15, minute=29) # 每10秒执行一次任务
scheduler.start()

# def signal_handler(sig, frame):
#     print('You pressed Ctrl+C!')
#     sys.exit(0)
#
# signal.signal(signal.SIGINT, signal_handler)
