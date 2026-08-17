import asyncio
from playwright.async_api import async_playwright
import json
import os

DATA_DIR = os.getenv("DATA_DIR", ".")
AUTH_FILE = os.path.join(DATA_DIR, "auth.json")

async def setup_login():
    """Run this function once to log in manually and save the session."""
    print("Opening browser for manual login...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://tp.bitmesra.co.in/login.html")
        print("Please log in. The script will wait until you navigate away from the login page.")
        
        # Wait until the URL is no longer the login page
        try:
            await page.wait_for_url(lambda url: "login.html" not in url, timeout=120000)
            print("Login detected!")
            
            # Save the authentication state
            await context.storage_state(path=AUTH_FILE)
            print(f"Session saved to {AUTH_FILE}")
        except Exception as e:
            print(f"Timeout or error: {e}")
        
        await browser.close()

from bs4 import BeautifulSoup

async def fetch_new_job_details(processed_ids):
    """Fetch the dashboard, find new jobs, and get their detail pages."""
    if not os.path.exists(AUTH_FILE):
        print(f"Auth file {AUTH_FILE} not found. Please run setup_login first.")
        return []

    new_jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_FILE)
        page = await context.new_page()
        
        print("Navigating to TnP portal dashboard...")
        await page.goto("https://tp.bitmesra.co.in/", timeout=60000)
        await page.wait_for_load_state("domcontentloaded")
        
        dashboard_content = await page.content()
        soup = BeautifulSoup(dashboard_content, "html.parser")
        table = soup.find("table", id="job-listings")
        
        if not table or not table.find("tbody"):
            print("Could not find job listings table.")
            await browser.close()
            return []

        # Find all new job IDs
        for row in table.find("tbody").find_all("tr"):
            columns = row.find_all("td")
            if len(columns) < 4: continue
            
            company_name = columns[0].get_text(strip=True)
            info_link = columns[3].find("a", href=lambda href: href and "job/info/" in href)
            if not info_link: continue
            
            job_id = info_link["href"].split("job/info/")[-1]
            if job_id not in processed_ids:
                print(f"Discovered new job: {company_name}")
                new_jobs.append({"id": job_id, "company": company_name})

        # Fetch details for each new job
        for job in new_jobs:
            print(f"Fetching details for {job['company']}...")
            await page.goto(f"https://tp.bitmesra.co.in/job/info/{job['id']}", timeout=60000)
            await page.wait_for_load_state("domcontentloaded")
            job["details_html"] = await page.content()
            
        await browser.close()
        return new_jobs

async def fetch_new_notifications(processed_ids):
    """Fetch the dashboard and find new notifications."""
    if not os.path.exists(AUTH_FILE):
        return []

    new_notifications = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_FILE)
        page = await context.new_page()
        
        print("Navigating to TnP portal dashboard for notifications...")
        await page.goto("https://tp.bitmesra.co.in/", timeout=60000)
        await page.wait_for_load_state("domcontentloaded")
        
        dashboard_content = await page.content()
        soup = BeautifulSoup(dashboard_content, "html.parser")
        
        # The notification table doesn't have a specific ID, but it's a dataTable inside the Notification Details section
        tables = soup.find_all("table", class_="dataTable")
        if not tables:
            await browser.close()
            return []

        # Find the notification table by checking for the 'Notification Details' header
        notif_table = None
        for table in tables:
            if "Notification Details" in table.get_text():
                notif_table = table
                break
                
        if not notif_table or not notif_table.find("tbody"):
            await browser.close()
            return []

        for row in notif_table.find("tbody").find_all("tr")[:10]:
            link = row.find("a", href=lambda href: href and "newsupdates/" in href)
            if not link:
                continue
                
            notif_id = link["href"].split("newsupdates/")[-1]
            title = link.get_text(strip=True)
            
            # Extract type (e.g. Job, News, Event)
            type_tag = row.find("b", class_="text-secondary")
            notif_type = type_tag.get_text(strip=True) if type_tag else "Update"
            
            # Extract date
            date_td = row.find_all("td")[-1]
            date_str = date_td.get_text(strip=True) if date_td else ""
            
            if notif_id not in processed_ids:
                print(f"Discovered new notification: {title}")
                new_notifications.append({
                    "id": notif_id,
                    "title": title,
                    "type": notif_type,
                    "date": date_str
                })

        await browser.close()
        return new_notifications

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        asyncio.run(setup_login())
    else:
        # For testing
        jobs = asyncio.run(fetch_new_job_details([]))
        print(f"Fetched {len(jobs)} jobs.")
