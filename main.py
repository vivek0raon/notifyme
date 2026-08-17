import asyncio
import json
import os
import datetime
import re
import time
from bs4 import BeautifulSoup
from scraper import fetch_new_job_details, fetch_new_notifications
from calendar_api import add_job_event, add_instant_alert_event, add_notification_event

DATA_DIR = os.getenv("DATA_DIR", ".")
STATE_FILE = os.path.join(DATA_DIR, "state.json")
# To use a shared calendar, replace 'primary' with the specific calendar ID
# e.g., 'your_email@group.calendar.google.com'
CALENDAR_ID = "fbcbe35fb7c1348253a9cc7b88653775bb3743b9720273921af87d230e050dc7@group.calendar.google.com"
NOTIFICATIONS_CALENDAR_ID = "49ba7feb079a98264dccaeb7fe39159df9a3c7d23fcdaaf8e8e018d06e66d801@group.calendar.google.com"

def load_state():
    state = {"processed_jobs": [], "processed_notifications": []}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            # Merge with default structure to prevent key errors
            state.update(data)
    return state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def parse_job_details(html_content):
    """Parse the specific job details page HTML to extract deep info."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    details = {
        "deadline_dt": None,
        "designation": "Software Role",
        "job_type": "Unknown",
        "ug_ctc": "Not specified",
        "pg_ctc": "Not specified",
        "stipend": "Not specified"
    }

    # Extract exact deadline
    # Ends On: <b>17-08-2026 [11:59 PM]</b>
    deadline_match = re.search(r'Ends On:\s*<b>(.*?)</b>', html_content)
    if deadline_match:
        dt_str = deadline_match.group(1).strip() # e.g. "17-08-2026 [11:59 PM]"
        try:
            # Parse format like DD-MM-YYYY [I:M p]
            details["deadline_dt"] = datetime.datetime.strptime(dt_str, "%d-%m-%Y [%I:%M %p]")
        except ValueError as e:
            print(f"Could not parse deadline: {dt_str} - {e}")

    # Extract designation
    designation_td = soup.find("td", text=re.compile("Job Designation", re.I))
    if designation_td and designation_td.find_next_sibling("td"):
        details["designation"] = designation_td.find_next_sibling("td").get_text(strip=True)

    # Extract Type
    type_td = soup.find("td", text=re.compile(r"^Type", re.I))
    if type_td and type_td.find_next_sibling("td"):
        details["job_type"] = type_td.find_next_sibling("td").get_text(strip=True)
        
    # Extract UG/PG CTC and Stipend using regex on raw text
    ug_ctc = re.search(r'UG.*?₹\s*(\d+)', html_content, re.IGNORECASE)
    if ug_ctc: details["ug_ctc"] = f"₹ {ug_ctc.group(1)}"
    
    pg_ctc = re.search(r'PG.*?₹\s*(\d+)', html_content, re.IGNORECASE)
    if pg_ctc: details["pg_ctc"] = f"₹ {pg_ctc.group(1)}"
        
    stipend = re.search(r'For UG <b>₹\s*(\d+)</b>', html_content, re.IGNORECASE)
    if stipend: details["stipend"] = f"₹ {stipend.group(1)}"
    
    return details

async def process_new_jobs(state):
    processed_ids = state["processed_jobs"]
    
    print(f"\n[{datetime.datetime.now()}] Checking for new jobs...")
    try:
        new_jobs = await fetch_new_job_details(processed_ids)
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return

    if not new_jobs:
        print("No new jobs to process.")
        return

    new_jobs_added = 0
    for job in new_jobs:
        company_name = job["company"]
        job_id = job["id"]
        
        details = parse_job_details(job["details_html"])
        deadline_dt = details["deadline_dt"]
        
        if not deadline_dt:
            print(f"Warning: No valid deadline found for {company_name}, using +7 days fallback.")
            deadline_dt = datetime.datetime.now() + datetime.timedelta(days=7)
            
        description = (
            f"**Application deadline for {company_name}**\n\n"
            f"**Designation:** {details['designation']}\n"
            f"**Type:** {details['job_type']}\n"
            f"**UG CTC:** {details['ug_ctc']}\n"
            f"**PG CTC:** {details['pg_ctc']}\n"
            f"**Stipend:** {details['stipend']}\n\n"
            f"Apply at: https://tp.bitmesra.co.in/job/info/{job_id}"
        )
        
        # Fire instant alert right now!
        add_instant_alert_event(company_name, details['designation'], description, calendar_id=CALENDAR_ID)
        
        # Create the actual deadline event in the calendar
        success = add_job_event(company_name, details['designation'], deadline_dt, description, calendar_id=CALENDAR_ID)
        
        if success:
            processed_ids.append(job_id)
            new_jobs_added += 1
        else:
            print(f"Failed to add calendar event for {company_name}")

    if new_jobs_added > 0:
        state["processed_jobs"] = processed_ids
        save_state(state)

async def process_new_notifications(state):
    processed_ids = state["processed_notifications"]
    
    print(f"\n[{datetime.datetime.now()}] Checking for new notifications...")
    try:
        new_notifs = await fetch_new_notifications(processed_ids)
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return

    if not new_notifs:
        print("No new notifications to process.")
        return

    new_notifs_added = 0
    for notif in new_notifs:
        notif_id = notif["id"]
        title = notif["title"]
        notif_type = notif["type"]
        date_str = notif["date"]
        
        # Create the event in the notifications calendar
        success = add_notification_event(title, notif_type, date_str, calendar_id=NOTIFICATIONS_CALENDAR_ID)
        
        if success:
            processed_ids.append(notif_id)
            new_notifs_added += 1
        else:
            print(f"Failed to add notification event for {title}")

    if new_notifs_added > 0:
        state["processed_notifications"] = processed_ids
        save_state(state)

async def main():
    print("Starting TnP Alerts Monitor...")
    while True:
        state = load_state()
        await process_new_jobs(state)
        await process_new_notifications(state)
        print("Sleeping for 15 minutes...")
        await asyncio.sleep(900)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
