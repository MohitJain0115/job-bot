import feedparser
import requests

TOKEN = "8241752968:AAFUz9YvDc3hrICVBFn7sz5xEH2eh-lkhIY"
CHAT_ID = "1003508880606"

RSS_URL = "https://rss.app/feeds/urVv1QL6bZI0zoAF.xml"

feed = feedparser.parse(RSS_URL)

print("Total jobs found:", len(feed.entries))

for entry in feed.entries[:1]:
    text = f"TEST JOB:\n{entry.title}\n{entry.link}"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": text})
