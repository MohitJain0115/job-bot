import feedparser
import requests
import html

# --- YOUR BOT DETAILS ---
TOKEN = "8241752968:AAEM38E7zxFlU9bEw1i4z8B8kxDW2a9pMvc"
CHAT_ID = "-1003508880606"   # IMPORTANT: keep -100

RSS_URL = "https://rss.app/feeds/urVv1QL6bZI0zoAF.xml"


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    })
    print("Telegram response:", r.text)


# --- Read RSS ---
feed = feedparser.parse(RSS_URL)
print("Total jobs found:", len(feed.entries))

# --- Force send FIRST job ---
if len(feed.entries) == 0:
    send("❌ RSS working but no jobs found")
else:
    entry = feed.entries[0]

    title = html.unescape(entry.title.strip())
    link = entry.link.strip()

    message = f"""🧑‍💼 NEW JOB ALERT

{title}

Apply Here:
{link}
"""

    send(message)
