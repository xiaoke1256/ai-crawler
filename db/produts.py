import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

# 连接MongoDB
client = MongoClient(MONGODB_URI)
db = client['crawler']
productsCollection = db['products']

def get_product_by_sku(sku):
    productObj = productsCollection.find_one({"sku":sku})
    if productObj:
        productObj['_id'] = str(productObj['_id'])
    return productObj

if __name__ == "__main__":
    sku = "29356484"
    product = get_product_by_sku(sku)
    print(product)
