import feedparser
import requests
import html
import json
import os
import time
from datetime import datetime

TOKEN = "YOUR_TOKEN"
CHAT_ID = "-1003508880606"
DB_FILE = "sent_jobs.json"

# ---------------- RSS COMPANIES ----------------
FEEDS = {
    "EY-Experience": "https://rss.app/feeds/ArdGwF1NJ5lTBKyI.xml",
    "EY-New": "https://rss.app/feeds/5zPz95dx36JeAAfP.xml",
    "Deloitte_USI": "https://rss.app/feeds/NmutfEwPtt7tEwvt.xml"
}

# ---------------- ORACLE APIs ----------------
ORACLE_APIS = {
    "KPMG": "https://ejgk.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_1,locationId=300000000296042,limit=25,sortBy=POSTING_DATES_DESC",

    "Company2": "https://ejgk.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_3001,locationId=300000000296042,limit=25,sortBy=POSTING_DATES_DESC"
}

# ---------------- PWC API ----------------
PWC_API = "https://www.pwc.com/gx/en/careers/job-results.shorturl.json?currentUrl=https%3A%2F%2Fwww.pwc.com%2Fgx%2Fen%2Fcareers%2Fjob-results.html%3Fwdcountry%3DIND%26wdjobsite%3DGlobal_Campus_Careers"

# ---------------- Load DB ----------------
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        sent_jobs = set(json.load(f))
else:
    sent_jobs = set()

# ---------------- SAFE REQUEST ----------------
def safe_get(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=25)
        if r.status_code == 200:
            return r
        else:
            print("Bad status:", r.status_code, url)
            return None
    except Exception as e:
        print("FAILED:", url)
        print(e)
        return None

# ---------------- TELEGRAM SEND ----------------
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": msg,
            "disable_web_page_preview": False
        }, timeout=20)

        print("Telegram:", r.status_code)

    except Exception as e:
        print("Telegram Error:", e)

    time.sleep(2)

# =========================================================
# RSS FEEDS
# =========================================================
def check_rss():
    print("\n--- Checking RSS Feeds ---")

    for company, RSS_URL in FEEDS.items():
        print("Checking", company)

        feed = feedparser.parse(RSS_URL)

        for entry in feed.entries:
            link = entry.link.strip()

            if link in sent_jobs:
                continue

            title = html.unescape(entry.title.strip())

            message = f"""🏢 {company} Hiring!

🧑‍💼 {title}

Apply Here:
{link}

#Jobs #{company}
"""
            send(message)
            sent_jobs.add(link)

# =========================================================
# ORACLE CLOUD APIs (KPMG etc)
# =========================================================
def check_oracle():
    print("\n--- Checking Oracle APIs ---")

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    for company, url in ORACLE_APIS.items():
        print("Checking", company)

        r = safe_get(url, headers)
        if not r:
            continue

        try:
            data = r.json()
        except:
            continue

        jobs = data.get("items", [])

        for job in jobs:
            title = job.get("Title", "Job Opening")
            jobid = job.get("Id")

            link = f"https://ejgk.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{jobid}"

            if link in sent_jobs:
                continue

            message = f"""🏢 {company} Hiring!

🧑‍💼 {title}

Apply Here:
{link}

#Jobs #{company}
"""
            send(message)
            sent_jobs.add(link)

# =========================================================
# PWC
# =========================================================
def check_pwc():
    print("\n--- Checking PwC ---")

    r = safe_get(PWC_API)
    if not r:
        return

    try:
        data = r.json()
    except:
        return

    jobs = data.get("data", [])

    for job in jobs:
        title = job.get("title", "Job Opening")
        link = job.get("applyUrl")

        if not link or link in sent_jobs:
            continue

        message = f"""🏢 PwC Hiring!

🧑‍💼 {title}

Apply Here:
{link}

#Jobs #PwC
"""
        send(message)
        sent_jobs.add(link)

# =========================================================
# RUN ALL
# =========================================================
check_rss()
check_oracle()
check_pwc()

# Save DB
with open(DB_FILE, "w") as f:
    json.dump(list(sent_jobs), f)

print("\nFinished successfully")