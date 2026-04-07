from playwright.sync_api import sync_playwright, TimeoutError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import pandas as pd
from datetime import datetime
import re

from llm_reporting import generate_summary_report, generate_structured_report, detect_anomalies

class HealthcareAutomation:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        retry=retry_if_exception_type(TimeoutError)
    )
    def wait_for_element(self, selector, timeout=10000):
        print(f"  Waiting for: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)
        return True
    
    def login(self):
        print("🔐 Logging in...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        
        self.page.goto("https://opensource-demo.orangehrmlive.com/")
        self.wait_for_element('input[name="username"]', timeout=5000)
        
        self.page.fill('input[name="username"]', "Admin")
        self.page.fill('input[name="password"]', "admin123")
        self.page.click('button[type="submit"]')
        
        self.wait_for_element(".oxd-main-menu", timeout=10000)
        print("✅ Login successful")
        return True
    
    def navigate_to_employees(self):
        print("📅 Navigating to employee list...")
        self.page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
        self.wait_for_element(".oxd-table-body", timeout=15000)
        print("✅ On employee list")
        return True
    
    def extract_data(self):
        """Extract using regex pattern matching"""
        print("📊 Extracting data...")
        
        # Wait for and get all rows
        self.wait_for_element(".oxd-table-card", timeout=15000)
        rows = self.page.locator(".oxd-table-card").all()
        print(f"Found {len(rows)} rows")
        
        staff_data = []
        
        for idx, row in enumerate(rows):
            row_text = row.text_content().strip()
            print(f"\nRow {idx}: {row_text[:100]}")
            
            # Extract employee ID (4-5 digits)
            id_match = re.search(r'(\d{4,5})', row_text)
            employee_id = id_match.group(1) if id_match else ""
            
            # Extract job titles from known list
            job_titles = ["HR Manager", "Manager", "Software Engineer", "Accountant", "Full-Time"]
            job_title = ""
            for title in job_titles:
                if title in row_text:
                    job_title = title
                    break
            
            # Extract name - look for capitalized words
            # Remove the ID first
            text_without_id = re.sub(r'^\d{4,5}', '', row_text)
            # Find sequences of capitalized words (potential names)
            name_match = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text_without_id)
            
            full_name = ""
            if name_match:
                # Take the first name-like sequence that's not a job title
                for potential_name in name_match:
                    if potential_name not in job_titles:
                        full_name = potential_name
                        break
            
            # If still no name, try splitting by numbers
            if not full_name and len(row_text) > 10:
                # Remove digits and common job terms
                clean = re.sub(r'\d+', '', row_text)
                for title in job_titles:
                    clean = clean.replace(title, "")
                # Take first 2-3 words
                words = clean.split()
                if len(words) >= 2:
                    full_name = ' '.join(words[:2])
            
            if employee_id and full_name:
                staff_data.append({
                    "employee_id": employee_id,
                    "full_name": full_name,
                    "job_title": job_title,
                    "extracted_at": datetime.now().isoformat()
                })
                print(f"  ✓ ID: {employee_id}, Name: {full_name}")
            else:
                print(f"  ✗ Could not parse - ID: '{employee_id}', Name: '{full_name}'")
        
        if not staff_data:
            # Emergency fallback: just extract any 4-digit numbers followed by letters
            all_text = self.page.locator(".oxd-table-body").inner_text()
            pattern = r'(\d{4,5})([A-Za-z\s]+)'
            matches = re.findall(pattern, all_text)
            
            for match in matches[:5]:
                employee_id = match[0]
                raw_name = match[1].strip()
                # Clean name (first 2-3 words)
                name_parts = raw_name.split()
                if name_parts:
                    full_name = ' '.join(name_parts[:2]) if len(name_parts) >= 2 else name_parts[0]
                    staff_data.append({
                        "employee_id": employee_id,
                        "full_name": full_name,
                        "job_title": "",
                        "extracted_at": datetime.now().isoformat()
                    })
                    print(f"  ✓ (emergency) ID: {employee_id}, Name: {full_name}")
        
        if not staff_data:
            self.page.screenshot(path="extraction_failed.png")
            raise Exception(f"No data extracted from {len(rows)} rows")
        
        print(f"\n✅ Extracted {len(staff_data)} records")
        return staff_data
    
    def save_reports(self, data):
        if not data:
            print("⚠️ No data to save")
            return
        
        df = pd.DataFrame(data)
        df.to_excel("staff_report.xlsx", index=False)
        print(f"\n📁 Saved staff_report.xlsx with {len(data)} records")
        
        print("\n📋 Extracted data:")
        for record in data:
            print(f"   {record['employee_id']} - {record['full_name']}")
    
    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def run_complete_pipeline(self):
        """End-to-end: scrape + AI report"""
        try:
            self.login()
            self.navigate_to_employees()
            data = self.extract_data()
            self.save_reports(data)
            
            # Now generate AI report
            df = pd.DataFrame(data)
            summary = generate_summary_report(df)
            anomalies = detect_anomalies(df)
            generate_structured_report(df, summary, anomalies)
            
            print("\n🎉 Complete pipeline executed!")
            print("   - Raw data: staff_report.xlsx")
            print("   - AI report: ai_generated_report.html")
            
        except Exception as e:
            print(f"Pipeline failed: {e}")

# ========== RUN ==========
if __name__ == "__main__":
    scraper = None
    try:
        scraper = HealthcareAutomation(headless=False)
        scraper.login()
        scraper.navigate_to_employees()
        data = scraper.extract_data()
        scraper.save_reports(data)
        print(f"\n🎉 SUCCESS! Extracted {len(data)} employees")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if scraper:
            scraper.close()
