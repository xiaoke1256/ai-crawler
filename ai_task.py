import time
from datetime import datetime
import random
import threading
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from ai.sentiment_analysis_cn import analyze_sentiment

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_PATH = os.path.join(WEB_DIR, "cookie.json")

# 连接MongoDB
client = MongoClient(MONGODB_URI)
db = client['crawler']
commentsCollection = db['comments']

def label_comments():
    # 获取未打标签的评论
    comments = commentsCollection.find({"emotion": {"$exists": False}})
    for comment in comments:
        print(f"开始打标签: {comment['text']}")
        # 模拟打标签
        #time.sleep(random.uniform(1, 3))
        result = analyze_sentiment(comment['text'])
        print(f"情感分析结果: {result}")
        emotion = ""
        # 输出主要情感
        if result["positive"] > result["negative"] and result["positive"] > result["neutral"]:
            emotion = 'positive'
        elif result["negative"] > result["positive"] and result["negative"] > result["neutral"]:
            emotion = 'negative'
        else:
            emotion = 'neutrality'
        # 更新标签
        commentsCollection.update_one({"_id": comment["_id"]}, {"$set": {"emotion": emotion}})

if __name__ == "__main__":
    label_comments()