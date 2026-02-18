import feedparser
import requests
import html
import json
import os

TOKEN = "YOUR_TOKEN"
CHAT_ID = "-1003508880606"

RSS_URL = "https://rss.app/feeds/urVv1QL6bZI0zoAF.xml"
DB_FILE = "sent_jobs.json"


# --- load sent jobs history ---
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        sent_jobs = set(json.load(f))
else:
    sent_jobs = set()


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    })


feed = feedparser.parse(RSS_URL)

new_found = False

for entry in feed.entries:
    link = entry.link.strip()

    if link in sent_jobs:
        continue

    title = html.unescape(entry.title.strip())

    message = f"""🧑‍💼 NEW JOB ALERT

{title}

Apply Here:
{link}
"""

    send(message)

    sent_jobs.add(link)
    new_found = True
    break   # send only 1 per run (prevents spam)


# save history
with open(DB_FILE, "w") as f:
    json.dump(list(sent_jobs), f)


if not new_found:
    print("No new jobs")
