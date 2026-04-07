from playwright.sync_api import sync_playwright
import json

# Pattern 1: Save/load authentication state (so you don't login every time)
def save_logged_in_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Login once
        page.goto("https://the-internet.herokuapp.com/login")
        page.fill("#username", "tomsmith")
        page.fill("#password", "SuperSecretPassword!")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        
        # Save cookies & localStorage
        context.storage_state(path="auth.json")
        browser.close()
        print("✅ Auth state saved")

# Pattern 2: Use saved state for subsequent runs
def use_saved_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()
        page.goto("https://the-internet.herokuapp.com/secure")
        print(f"Logged in as: {page.locator("h2").text_content()}")
        browser.close()

# Pattern 3: Extract HTML table to structured data
def extract_table():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/tables")
        
        # Get all rows from table #1
        rows = page.locator("#table1 tbody tr").all()
        table_data = []
        
        for row in rows:
            cells = row.locator("td").all_text_contents()
            table_data.append({
                "last_name": cells[0],
                "first_name": cells[1],
                "email": cells[2],
                "due": cells[3]
            })
        
        print(json.dumps(table_data, indent=2))
        browser.close()

# Pattern 4: Wait for dynamic content (critical for slow medical portals)
def wait_for_dynamic_content():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
        page.click("#start button")
        
        # Wait for specific element to appear
        page.wait_for_selector("#finish h4", timeout=10000)
        result = page.locator("#finish h4").text_content()
        print(f"Dynamic result: {result}")
        browser.close()

def download_pdf_report():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Set up download handling
        with page.expect_download() as download_info:
            page.click("#generate_pdf_button")
        
        download = download_info.value
        download.save_as("reports/patient_report.pdf")
        print(f"✅ PDF saved: {download.suggested_filename}")

from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def flaky_operation(page):
    # Some portal element that sometimes fails
    page.click("button:has-text('Submit')", timeout=5000)
    return page.locator(".success-message").text_content()


if __name__ == "__main__":
    save_logged_in_state()
    use_saved_state()
    extract_table()
    wait_for_dynamic_content()
