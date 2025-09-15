from Database import MONGO_URI, MONGO_DB, MONGO_COLLECTION, MONGO_COLLECTION_PROCESSED
from pymongo import MongoClient
import pdb
class process:
    def __init__(self):
        self.database()

    def database(self):
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        self.collection = db[MONGO_COLLECTION]
        self.collection_process = db[MONGO_COLLECTION_PROCESSED]

    def record(self, data, content):
        return {
            "topic": data.get("topic"),
            "title": data.get("title"),
            "subtopic": data.get("subtopic"),
            "content": content
        }

    def main(self):
        list_title = list(self.collection_process.distinct("title"))
        data = self.collection.find({"title": {"$nin": list_title}})
        result = []
        for article in data:
            if 'content' in article and isinstance(article['content'], str):
                parts = article['content'].split("\n")
                for value in parts:
                    value = value.strip()
                    if value:
                        item = self.record(article, value)
                        if len(item['content']) >= 100:
                            result.append(item)
        for data in result:
            self.collection_process.update_one(
                {"content": data["content"]},
                {"$set": data},
                upsert=True
            )
        return result

if __name__=="__main__":
    app = process()
    app.main()