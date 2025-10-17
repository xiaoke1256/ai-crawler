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

# 类似以下查询语句
# db.sales.aggregate([
#     {
#         $group: {
#             _id: "$product_id",  // 分组依据
#             totalQuantity: { $sum: "$quantity" }  // 计算每个产品的总销售量
#         }
#     }
# ]);

def statistics():
    # 定义聚合查询
    pipeline = [
        {
            "$group": {
                "_id": "$sku",  # 分组依据是sku字段
                "total_count": {"$sum": 1},  # 总评论数
                "positive_count": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$emotion", "positive"]},
                            1,
                            0
                        ]
                    }
                },
            }
        },
        {
            "$sort": { "total_count": -1 }
        }
    ]

    # 执行聚合查询
    result = commentsCollection.aggregate(pipeline)
    return result

if __name__ == "__main__":
    result = statistics()
    for doc in result:
        print(doc)


