from pymongo import MongoClient
from Database import MONGO_URI,MONGO_DB,MONGO_COLLECTION,client_id,client_secret
import praw
from datetime import datetime

class Redit:
    def __init__(self):
        self.connect()
        self.database()
    def database(self):
        client = MongoClient(MONGO_URI)
        db= client[MONGO_DB]
        self.collection = db[MONGO_COLLECTION]
    def connect(self):
        user_agent = "Scraper 1.0 by /u/python_engineer"
        self.redit = praw.Reddit(
            client_id= client_id,
            client_secret= client_secret,
            user_agent = user_agent
        )
    def insertData(self, data):
        product = self.collection.find_one({"title": data["title"], "link": data["link"]})
        if not product:
            self.collection.insert_one(data)
    def group(self):
        subreddits = ["TroChuyenLinhTinh", "VietNamNation", "vozforums", "reviewnganhluat", "vietnamtoday"]
        self.subreddit_names = "+".join(subreddits)
        return self.subreddit_names
    def subcredit(self, group):
        for submision in self.redit.subreddit(group).hot(limit=10):
            title = submision.title
            author = submision.author
            url =submision.url
            link = f"https://www.reddit.com{submision.permalink}"
            img_link = ""
            try:
                if hasattr(submision, "preview") and "images" in submision.preview:
                    img_link = submision.preview["images"][0]["source"]["url"]
            except:
                pass
            content = submision.selftext.strip() if submision.selftext else ""
            date = datetime.now()
            subreddit =submision.subreddit.display_name
            upvotes = submision.score
            comments= submision.num_comments
            video_link = ""
            try:
                if submision.is_video and submision.media and "reddit_video" in submision.media:
                    video_link = submision.media["reddit_video"]["fallback_url"]
            except:
                pass
            data = {
                    'date': date,
                    'author': author,
                    'subreddit': subreddit,
                    'title': title,
                    'content': content.strip() if content else None,
                    'upvotes': upvotes,
                    'comments': comments,
                    'link': link,
                    'image_link': img_link if img_link else None,
                    'video_link': video_link if video_link else None
            }
            
            #self.insertData(data)
            
            print(f"title: {title}")
            print(f"author{author}")
            print(f"subreddit: {subreddit}")
            print(f"Like: {upvotes}")
            print(f"comments: {comments}")
            print(f"link: {link}")
            print(f"img_link: {img_link}")
            print(f"video_link: {video_link}")
            print(f"date: {date}")
            print(f"content: {content}")
            print('*'*100)



if __name__ =='__main__':
    app = Redit()
    data = app.group()
    app.subcredit(data)
