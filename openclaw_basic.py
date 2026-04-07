# openclaw_basic.py
from openclaw import Claw, Session, Task
import asyncio

async def extract_healthcare_data():
    """Extract data from multiple healthcare portals simultaneously"""
    
    # Create a Claw instance (manages multiple sessions)
    claw = Claw(
        max_concurrent=3,  # Run 3 portals at once
        headless=False,
        user_data_dir="./browser_profiles"  # Persist logins
    )
    
    # Define portals to scrape
    portals = [
        {
            "name": "EMR System A",
            "url": "https://demo.emr-a.com",
            "username": "admin",
            "password": "pass123"
        },
        {
            "name": "Scheduling Portal B", 
            "url": "https://demo.scheduling-b.com",
            "username": "scheduler",
            "password": "schedule456"
        },
        {
            "name": "Billing System C",
            "url": "https://demo.billing-c.com",
            "username": "biller",
            "password": "bill789"
        }
    ]
    
    # Define extraction task
    @Task(interval=3600)  # Run every hour
    async def extract_appointments(session: Session):
        """Extract today's appointments from a portal"""
        page = session.page
        
        # Login (handled automatically by session persistence)
        await page.goto(session.config["url"])
        
        # Extract data
        appointments = await page.locator(".appointment-row").all_text_contents()
        
        return {
            "portal": session.config["name"],
            "appointments": appointments,
            "count": len(appointments)
        }
    
    # Run all portals concurrently
    results = await claw.run(portals, extract_appointments)
    
    return results

# Run
if __name__ == "__main__":
    results = asyncio.run(extract_healthcare_data())
    print(results)