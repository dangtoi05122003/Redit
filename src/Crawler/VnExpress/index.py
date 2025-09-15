from selenium import webdriver
from selenium.webdriver.common.by import By
from config import setup
from time import sleep
from Database import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from pymongo import MongoClient

class VnExpress():
    def __init__(self):
        option = setup()
        self.driver = webdriver.Chrome(options=option)
        self.database()

    def website(self):
        self.driver.get("https://vnexpress.net/")

    def database(self):
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        self.collection = db[MONGO_COLLECTION]

    def topics(self):
        topics = self.driver.find_elements(By.CSS_SELECTOR, 'ul.parent > li > a')
        topic_list = []
        label = ["VnE-GO","Góc nhìn", "Ý kiến", "Tâm sự", "Tất cả"]
        for t in topics:
            name = t.text.strip()
            link = t.get_attribute("href")
            if name and link and name not in label:
                topic_list.append((name, link))
        print(topic_list)
        return topic_list

    def subtopics(self, topics):
        topic_list = []
        for name, link in topics:
            print(f"\n{name} -> {link}")
            self.driver.get(link)
            try:
                subtopics = self.driver.find_elements(By.CSS_SELECTOR, 'ul.ul-nav-folder > li > a')
                for subtopic in subtopics:
                    subtopic_name = subtopic.text.strip()
                    subtopic_link = subtopic.get_attribute("href")
                    if subtopic_name and subtopic_link:
                        print(f"{subtopic_name} {subtopic_link}")
                        topic_list.append((name, link, subtopic_link, subtopic_name))
            except Exception as e:
                print(f"Error {name}: {e}")
        return topic_list

    def Information(self, article):
        title, link, description = "", "", ""
        try:
            title_news = article.find_element(By.CSS_SELECTOR, "h2.title-news a, h3.title-news a")
            title = title_news.text.strip()
            link = title_news.get_attribute("href")
        except:
            pass
        try:
            description = article.find_element(By.CSS_SELECTOR, "p.description a").text.strip()
        except:
            pass
        return {
            "title": title,
            "url": link,
            "description": description,
        }

    def detail(self, url):
        try:
            self.driver.get(url)
            content_text = self.driver.find_element(By.CSS_SELECTOR, "article.fck_detail").text
            try:
                date = self.driver.find_element(By.CSS_SELECTOR, "span.date").text
            except:
                date = ""
            return {
                "date": date,
                "text": content_text
            }
        except:
            return {"date": "", "text": ""}
        
    def product(self, topic_list):
        for name, link, subtopic_link, subtopic_name in topic_list:
            print(f"\n{name} / {subtopic_name} : {subtopic_link}")
            self.driver.get(subtopic_link)
            try:
                sleep(2)
                articles = self.driver.find_elements(By.CSS_SELECTOR, "article.item-news, article.article-item, article.article-new")
                if not articles:
                    print("Error articles")
                    continue
                all_links = []
                for article in articles:
                    data = self.Information(article)
                    if data["title"] and data["url"]:
                        all_links.append(data)
                for data in all_links:
                    try:
                        Search = self.collection.find_one({"title": data["title"],"topic": name,"subtopic": subtopic_name})
                        if Search:
                            continue
                        detail_content = self.detail(data["url"])
                        data["content"] = detail_content["text"]
                        data["date"] = detail_content["date"]
                        data["topic"] = name
                        data["subtopic"] = subtopic_name
                        self.collection.update_one(
                            {"title": data["title"], "topic": name, "subtopic": subtopic_name},
                            {"$set": data},
                            upsert=True
                        )
                        print(f"{data['title']} - {data['url']}")
                    except Exception as e:
                        print("Error:", e)
                        continue
                print("."*100)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    app = VnExpress()
    try:
        app.website()
        topic = app.topics()
        topics1 = app.subtopics(topic)
        app.product(topics1)
    finally:
        app.driver.quit()