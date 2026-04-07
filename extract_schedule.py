from playwright.sync_api import sync_playwright
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed
from datetime import datetime

class StaffScheduleScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
    
    def login(self):
        """Login to OrangeHRM demo"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        
        print("🔐 Logging in...")
        self.page.goto("https://opensource-demo.orangehrmlive.com/")
        self.page.fill('input[name="username"]', "Admin")
        self.page.fill('input[name="password"]', "admin123")
        self.page.click('button[type="submit"]')
        
        # Wait for dashboard to load
        self.page.wait_for_selector("h6:has-text('Dashboard')", timeout=10000)
        print("✅ Login successful")
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def navigate_to_schedule(self):
        """Navigate to employee schedule view"""
        print("📅 Navigating to schedule...")
        
        # Click on "PIM" (Personnel Info Management - like patient/employee registry)
        self.page.click('a[href*="viewEmployeeList"]')
        self.page.wait_for_load_state("networkidle")
        
        # In real healthcare: you'd click "Appointments" or "Schedule"
        # Here we'll extract employee list as a proxy for "staff schedule"
        self.page.click('a[href*="viewEmployeeList"]')  # Ensure we're on list view
        
        print("✅ On employee/staff list")
    
    def extract_staff_data(self):
        """Extract table data - pattern identical to patient/appointment lists"""
        print("📊 Extracting data...")
        
        # Wait for table to load
        self.page.wait_for_selector(".oxd-table-body", timeout=10000)
        
        # Get all rows
        rows = self.page.locator(".oxd-table-card").all()
        staff_data = []
        
        for row in rows[:10]:  # First 10 rows for demo
            cells = row.locator(".oxd-table-cell").all_text_contents()
            
            # Typical healthcare fields we extract
            record = {
                "employee_id": cells[0] if len(cells) > 0 else "",
                "full_name": cells[1] if len(cells) > 1 else "",
                "job_title": cells[2] if len(cells) > 2 else "",
                "employment_status": cells[3] if len(cells) > 3 else "",
                "sub_unit": cells[4] if len(cells) > 4 else "",
                "extracted_at": datetime.now().isoformat()
            }
            staff_data.append(record)
        
        print(f"✅ Extracted {len(staff_data)} records")
        return staff_data
    
    def save_to_excel(self, data, filename="staff_schedule.xlsx"):
        """Save extracted data to Excel (report generation)"""
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"📁 Saved to {filename}")
        return filename
    
    def generate_html_report(self, data, filename="schedule_report.html"):
        """Generate a clean HTML dashboard (for non-technical stakeholders)"""
        html = f"""
        <html>
        <head><title>Staff Schedule Report</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
        </style>
        </head>
        <body>
        <h1>Healthcare Staff Schedule</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table>
            <tr><th>ID</th><th>Name</th><th>Role</th><th>Status</th><th>Unit</th></tr>
        """
        for record in data:
            html += f"""
                <tr>
                    <td>{record['employee_id']}</td>
                    <td>{record['full_name']}</td>
                    <td>{record['job_title']}</td>
                    <td>{record['employment_status']}</td>
                    <td>{record['sub_unit']}</td>
                </tr>
            """
        html += "</table></body></html>"
        
        with open(filename, "w") as f:
            f.write(html)
        print(f"📄 HTML report saved: {filename}")
    
    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

# ============ RUN THE SCRIPT ============
if __name__ == "__main__":
    scraper = StaffScheduleScraper(headless=False)  # Set True for background run
    try:
        scraper.login()
        scraper.navigate_to_schedule()
        staff = scraper.extract_staff_data()
        scraper.save_to_excel(staff)
        scraper.generate_html_report(staff)
        print("\n🎉 Automation complete! Check staff_schedule.xlsx and schedule_report.html")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()
        