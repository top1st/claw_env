# openclaw_healthcare.py
"""
OpenClaw integration for multi-portal healthcare automation
Matches job requirements: "OpenClaw or equivalent automation tools"
"""

import asyncio
import pandas as pd
from datetime import datetime
from typing import Dict, List

try:
    from openclaw import Claw, Session, Task, SessionPool
    OPENCLAW_AVAILABLE = True
except ImportError:
    print("⚠️ OpenClaw not installed. Install with: pip install openclaw")
    OPENCLAW_AVAILABLE = False

class HealthcarePortalAutomation:
    """
    Multi-portal healthcare data extraction using OpenClaw
    Handles: EMR, Scheduling, Billing, Reporting systems
    """
    
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.claw = None
        
    async def initialize(self):
        """Initialize OpenClaw with session persistence"""
        self.claw = Claw(
            max_concurrent=self.max_concurrent,
            headless=False,  # Set True for production
            user_data_dir="./healthcare_sessions",  # Persist cookies
            default_timeout=30000,
            retry_attempts=3
        )
        
    async def create_healthcare_sessions(self):
        """Create sessions for different healthcare portals"""
        
        portals = [
            {
                "id": "emr_main",
                "name": "Primary EMR System",
                "url": "https://demo.healthcare-emr.com",
                "login_selector": "#login-form",
                "username_selector": "#username",
                "password_selector": "#password",
                "submit_selector": "button[type='submit']",
                "dashboard_selector": ".dashboard"
            },
            {
                "id": "scheduling",
                "name": "Appointment Scheduler",
                "url": "https://demo.scheduler.com",
                "login_selector": "form.auth",
                "username_selector": "input[name='user']",
                "password_selector": "input[name='pass']",
                "submit_selector": "#login-btn",
                "dashboard_selector": ".calendar-view"
            },
            {
                "id": "billing",
                "name": "Billing System",
                "url": "https://demo.billing.com",
                "login_selector": ".login-panel",
                "username_selector": "#email",
                "password_selector": "#password",
                "submit_selector": ".submit-btn",
                "dashboard_selector": ".claims-dashboard"
            }
        ]
        
        sessions = []
        for portal in portals:
            session = Session(
                id=portal["id"],
                config=portal,
                login_flow=self.healthcare_login_flow
            )
            sessions.append(session)
        
        return sessions
    
    async def healthcare_login_flow(self, session: Session):
        """Custom login flow for healthcare portals (handles MFA, redirects)"""
        page = session.page
        config = session.config
        
        print(f"🔐 Logging into {config['name']}...")
        
        # Navigate to login page
        await page.goto(config["url"])
        
        # Wait for login form
        await page.wait_for_selector(config["login_selector"], timeout=10000)
        
        # Fill credentials (in production, use env vars)
        await page.fill(config["username_selector"], "healthcare_user")
        await page.fill(config["password_selector"], "secure_password")
        
        # Click login
        await page.click(config["submit_selector"])
        
        # Wait for dashboard (indicates successful login)
        await page.wait_for_selector(config["dashboard_selector"], timeout=15000)
        
        # Handle possible MFA prompt
        if await page.locator("#mfa-input").count() > 0:
            print("📱 MFA required - waiting for manual input...")
            await page.wait_for_selector(".dashboard", timeout=60000)
        
        print(f"✅ Logged into {config['name']}")
        
        # Take screenshot for audit
        await page.screenshot(path=f"sessions/{config['id']}_dashboard.png")
        
        return True
    
    @Task(interval=1800)  # Run every 30 minutes
    async def extract_patient_appointments(self, session: Session):
        """Extract today's appointments from scheduling portal"""
        page = session.page
        config = session.config
        
        if config["id"] != "scheduling":
            return None
        
        print(f"📅 Extracting appointments from {config['name']}...")
        
        # Navigate to today's schedule
        await page.click("a:has-text('Today')")
        await page.wait_for_load_state("networkidle")
        
        # Extract appointment data
        appointments = []
        rows = await page.locator(".appointment-row").all()
        
        for row in rows:
            cells = await row.locator("td").all_text_contents()
            if len(cells) >= 4:
                appointments.append({
                    "time": cells[0],
                    "patient": cells[1],
                    "provider": cells[2],
                    "reason": cells[3],
                    "portal": config["name"],
                    "extracted_at": datetime.now().isoformat()
                })
        
        print(f"   Found {len(appointments)} appointments")
        return appointments
    
    @Task(priority=1)  # High priority - runs first
    async def check_system_status(self, session: Session):
        """Health check for each portal"""
        page = session.page
        config = session.config
        
        # Check if system is responsive
        start_time = datetime.now()
        await page.reload()
        load_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "portal": config["name"],
            "status": "healthy" if load_time < 5 else "slow",
            "load_time_seconds": load_time,
            "last_check": datetime.now().isoformat()
        }
    
    async def run_multi_portal_extraction(self):
        """Run all portals concurrently"""
        print("\n" + "="*60)
        print("🦞 OPENCLAW MULTI-PORTAL HEALTHCARE EXTRACTION")
        print("="*60)
        
        # Create sessions
        sessions = await self.create_healthcare_sessions()
        
        # Define tasks for each session
        tasks = [
            self.check_system_status(session) for session in sessions
        ] + [
            self.extract_patient_appointments(session) for session in sessions
        ]
        
        # Run all tasks concurrently across all sessions
        results = await self.claw.run_concurrent(sessions, tasks)
        
        # Combine results
        all_appointments = []
        for result in results:
            if result and isinstance(result, list):
                all_appointments.extend(result)
        
        # Save to Excel
        if all_appointments:
            df = pd.DataFrame(all_appointments)
            df.to_excel("openclaw_appointments.xlsx", index=False)
            print(f"\n📁 Saved {len(all_appointments)} appointments to openclaw_appointments.xlsx")
        
        # Save status report
        status_report = [r for r in results if r and isinstance(r, dict) and "status" in r]
        if status_report:
            pd.DataFrame(status_report).to_excel("portal_status.xlsx", index=False)
        
        return results
    
    async def close(self):
        """Clean up sessions"""
        if self.claw:
            await self.claw.close()

# ============ RUN ============
async def main():
    automation = HealthcarePortalAutomation(max_concurrent=3)
    
    try:
        await automation.initialize()
        results = await automation.run_multi_portal_extraction()
        print("\n✅ OpenClaw automation complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        await automation.close()

if __name__ == "__main__":
    if OPENCLAW_AVAILABLE:
        asyncio.run(main())
    else:
        print("\n💡 To use OpenClaw:")
        print("   pip install openclaw")
        print("   Or use the Playwright alternative below")
        