import feedparser
import schedule
import time
import json
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)

# موضوعات و منابع RSS
TOPICS = {
    "Artificial Intelligence": ["artificial intelligence", "AI"],
    "Blockchain": ["blockchain", "crypto"]
}
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://www.theguardian.com/technology/rss"
]

# جمع‌آوری اخبار
def collect_news():
    print("Starting news collection...")
    news_data = {topic: [] for topic in TOPICS}
    try:
        for feed_url in RSS_FEEDS:
            print(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                print(f"No entries found for feed: {feed_url}")
                continue
            for entry in feed.entries:
                title = entry.title.lower()
                summary = entry.get("summary", "").lower()
                for topic, keywords in TOPICS.items():
                    if any(keyword.lower() in title or keyword.lower() in summary for keyword in keywords):
                        news_data[topic].append({
                            "title": entry.title,
                            "link": entry.link,
                            "published": entry.get("published", "No date")
                        })
        for topic in news_data:
            news_data[topic] = news_data[topic][:5]
        try:
            with open("news_data.json", "w", encoding="utf-8") as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            print("News collected and saved successfully")
        except Exception as e:
            print(f"Error saving news_data.json: {e}")
        return news_data
    except Exception as e:
        print(f"Error in collect_news: {e}")
        return news_data
# تابع برای بارگذاری اخبار
def load_news():
    print("Loading news_data.json...")
    try:
        with open("news_data.json", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("news_data.json is empty, collecting fresh news")
                return collect_news()
            return json.loads(content)
    except FileNotFoundError:
        print("news_data.json not found, collecting fresh news")
        return collect_news()
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError in news_data.json: {e}, collecting fresh news")
        return collect_news()
    except Exception as e:
        print(f"Unexpected error in load_news: {e}")
        return {topic: [] for topic in TOPICS}
# مسیر اصلی وب‌سایت
@app.route("/")
def index():
    news_data = load_news()
    return render_template("index.html", news_data=news_data, last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"))

# تابع برای آپدیت روزانه
def update_news():
    print("جمع‌آوری اخبار...")
    collect_news()
    print("اخبار آپدیت شد.")

# زمان‌بندی روزانه
schedule.every().day.at("08:00").do(update_news)

# اجرای Flask و زمان‌بندی
if __name__ == "__main__":
    # جمع‌آوری اولیه اخبار
    update_news()
    # اجرای سرور Flask در یک thread جدا
    import threading
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)
    threading.Thread(target=run_schedule, daemon=True).start()
    app.run(debug=True)