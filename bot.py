import feedparser
import requests
import html
import json
import os
import time
from bs4 import BeautifulSoup

TOKEN = "8241752968:AAEM38E7zxFlU9bEw1i4z8B8kxDW2a9pMvc"
CHAT_ID = "-1003508880606"
DB_FILE = "sent_jobs.json"


# ---------------- RSS COMPANIES ----------------
FEEDS = {
    "EY-Experience": "https://rss.app/feeds/ArdGwF1NJ5lTBKyI.xml",
    "EY-New": "https://rss.app/feeds/5zPz95dx36JeAAfP.xml",
    "Deloitte_USI": "https://rss.app/feeds/NmutfEwPtt7tEwvt.xml"
}


# ---------------- API COMPANIES ----------------
ORACLE_APIS = {
    "KPMG": "https://ejgk.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_1,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,locationId=300000000296042,sortBy=POSTING_DATES_DESC",

    "KPMG-Alt": "https://ejgk.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_3001,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,locationId=300000000296042,sortBy=POSTING_DATES_DESC"
}

PWC_API = "https://www.pwc.com/gx/en/careers/job-results.shorturl.json?currentUrl=https%3A%2F%2Fwww.pwc.com%2Fgx%2Fen%2Fcareers%2Fjob-results.html%3Fwdcountry%3DIND%26wdjobsite%3DGlobal_Campus_Careers%26flds%3Djobreqid%2Ctitle%2Clocation%2Clos%2Cspecialism%2Cgrade%2Cindustry%2Cregion%2Capply%2Cjobsite%2Ciso"


# ---------------- LOAD HISTORY ----------------
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        sent_jobs = set(json.load(f))
else:
    sent_jobs = set()


# ---------------- TELEGRAM SEND ----------------
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_web_page_preview": False
            },
            timeout=20
        )
        time.sleep(1.5)  # anti spam
    except:
        print("Telegram send failed")


# ---------------- RSS SCANNER ----------------
def scan_rss():
    global sent_jobs

    for company, url in FEEDS.items():
        print("Checking RSS:", company)

        try:
            feed = feedparser.parse(url)
        except:
            continue

        for entry in feed.entries:
            link = entry.link.strip()
            if link in sent_jobs:
                continue

            title = html.unescape(entry.title.strip())

            message = f"""🏢 {company} Hiring

🧑‍💼 {title}

🔗 Apply:
{link}

#Jobs #Hiring #{company}
"""

            send(message)
            sent_jobs.add(link)


# ---------------- ORACLE API SCANNER ----------------
def scan_oracle():
    global sent_jobs

    for company, url in ORACLE_APIS.items():
        print("Checking API:", company)

        try:
            data = requests.get(url, timeout=25).json()
        except:
            continue

        jobs = data.get("items", [])

        for job in jobs:
            title = job.get("Title")
            job_id = str(job.get("Id"))
            link = f"https://ejgk.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{job_id}"

            if link in sent_jobs:
                continue

            location = ""
            try:
                location = job["PrimaryLocation"]["LocationName"]
            except:
                pass

            message = f"""🏢 {company} Hiring

🧑‍💼 {title}
📍 {location}

🔗 Apply:
{link}

#Jobs #{company}
"""

            send(message)
            sent_jobs.add(link)


# ---------------- PWC SCANNER ----------------
def scan_pwc():
    global sent_jobs

    print("Checking PwC")

    try:
        data = requests.get(PWC_API, timeout=25).json()
    except:
        return

    jobs = data.get("data", [])

    for job in jobs:
        title = BeautifulSoup(job.get("title", ""), "html.parser").text
        link = job.get("apply")

        if not link or link in sent_jobs:
            continue

        location = job.get("location", "India")

        message = f"""🏢 PwC Hiring

🧑‍💼 {title}
📍 {location}

🔗 Apply:
{link}

#Jobs #PwC
"""

        send(message)
        sent_jobs.add(link)


# ---------------- RUN ALL ----------------
scan_rss()
scan_oracle()
scan_pwc()


# ---------------- SAVE HISTORY ----------------
with open(DB_FILE, "w") as f:
    json.dump(list(sent_jobs), f)

print("Run complete")