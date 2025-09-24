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
    def group(self):
        subreddits = ["TroChuyenLinhTinh", "VietNamNation", "vozforums", "reviewnganhluat", "vietnamtoday"]
        self.subreddit_names = "+".join(subreddits)
        return self.subreddit_names
    def subcredit(self, group):
        for submission in self.redit.subreddit(group).hot(limit=100):
            title = submission.title
            author = submission.author.name
            link = f"https://www.reddit.com{submission.permalink}"
            img_link = ""
            try:
                if hasattr(submission, "preview") and "images" in submission.preview:
                    img_link = submission.preview["images"][0]["source"]["url"]
            except:
                pass
            content = submission.selftext.strip() if submission.selftext else ""
            date = datetime.fromtimestamp(submission.created_utc)
            subreddit =submission.subreddit.display_name
            upvotes = submission.score
            comments= submission.num_comments
            video_link = ""
            try:
                if submission.is_video and submission.media and "reddit_video" in submission.media:
                    video_link = submission.media["reddit_video"]["fallback_url"]
            except:
                pass
            data = {
                    "date": date,
                    "author": author,
                    "subreddit": subreddit,
                    "title": title,
                    "content": content.strip() if content else None,
                    "upvotes": upvotes,
                    "comments": comments,
                    "link": link,
                    "image_link": img_link if img_link else None,
                    "video_link": video_link if video_link else None
            }
            self.collection.update_one(
                {"link": link},
                {"$set": data},
                upsert=True
            )
if __name__ =='__main__':
    app = Redit()
    data = app.group()
    app.subcredit(data)