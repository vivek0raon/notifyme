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
        await page.goto("https://tp.bitmesra.co.in/")
        await page.wait_for_load_state("networkidle")
        
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
            await page.goto(f"https://tp.bitmesra.co.in/job/info/{job['id']}")
            await page.wait_for_load_state("networkidle")
            job["details_html"] = await page.content()
            
        await browser.close()
        return new_jobs

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        asyncio.run(setup_login())
    else:
        # For testing
        jobs = asyncio.run(fetch_new_job_details([]))
        print(f"Fetched {len(jobs)} jobs.")
