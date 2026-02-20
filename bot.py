import feedparser
import requests
import html
import json
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = "YOUR_TOKEN"
CHAT_ID = "-1003508880606"

# ---- TEST DATE ----
TARGET_DATE = datetime(2026, 2, 20).date()

# -------- RSS FEEDS --------
FEEDS = {
    "EY-Experience": "https://rss.app/feeds/ArdGwF1NJ5lTBKyI.xml",
    "EY-New": "https://rss.app/feeds/5zPz95dx36JeAAfP.xml",
    "Deloitte_USI": "https://rss.app/feeds/NmutfEwPtt7tEwvt.xml"
}


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False
    })

    print("Telegram:", r.status_code)
    time.sleep(2)


# -------- CHECK DATE --------
def is_target_date(date_string):
    try:
        dt = datetime.fromisoformat(date_string.replace("Z",""))
        return dt.date() == TARGET_DATE
    except:
        return False


# -------- RSS --------
def check_rss(company, url):
    feed = feedparser.parse(url)

    for entry in feed.entries:
        if not hasattr(entry, "published_parsed"):
            continue

        post_date = datetime(*entry.published_parsed[:6]).date()

        if post_date != TARGET_DATE:
            continue

        message = f"""🏢 {company} Hiring!

🧑‍💼 {html.unescape(entry.title)}

Apply Here:
{entry.link}

#Jobs #MNCJobs #{company}
"""
        send(message)


# -------- ORACLE --------
def fetch_oracle(company, site):
    offset = 0

    while True:
        url = f"https://ejgk.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber={site},facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,offset={offset},locationId=300000000296042,sortBy=POSTING_DATES_DESC"

        r = requests.get(url)
        data = r.json()
        items = data.get("items", [])

        if not items:
            break

        for job in items:
            posted = job.get("PostedDate") or job.get("CreationDate")
            if not posted or not is_target_date(posted):
                continue

            title = job.get("Title", "No Title")
            job_id = job.get("Id")
            location = job.get("PrimaryLocation", {}).get("LocationName", "India")

            link = f"https://ejgk.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/{site}/job/{job_id}"

            message = f"""🏢 {company} Hiring!

🧑‍💼 {title} - {location}

Apply Here:
{link}

#Jobs #MNCJobs #{company}
"""
            send(message)

        offset += 25


# -------- PWC CAMPUS --------
def fetch_pwc_campus():
    url = "https://www.pwc.com/gx/en/careers/job-results.shorturl.json?currentUrl=https%3A%2F%2Fwww.pwc.com%2Fgx%2Fen%2Fcareers%2Fjob-results.html%3Fwdcountry%3DIND%26wdjobsite%3DGlobal_Campus_Careers%26flds%3Djobreqid%2Ctitle%2Clocation%2Clos%2Cspecialism%2Cgrade%2Cindustry%2Cregion%2Capply%2Cjobsite%2Ciso"

    data = requests.get(url).json()

    for job in data.get("data", []):
        date = job.get("postedDate")
        if not date or not is_target_date(date):
            continue

        title = job.get("title")
        link = job.get("apply")

        message = f"""🏢 PwC Hiring!

🧑‍💼 {title}

Apply Here:
{link}

#Jobs #MNCJobs PwC
"""
        send(message)


# -------- RUN ALL --------

print("Checking RSS...")
for company, url in FEEDS.items():
    check_rss(company, url)

print("Checking Oracle APIs...")
fetch_oracle("KPMG", "CX_1")
fetch_oracle("KPMG-Alt", "CX_3")
fetch_oracle("KPMG-Global", "CX_3001")

print("Checking PwC Campus...")
fetch_pwc_campus()

print("TEST RUN COMPLETE")