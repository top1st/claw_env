from playwright.sync_api import sync_playwright

def test_login_and_extract():
    with sync_playwright() as p:
        # Launch browser (visible so you can watch)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 1. Navigate to the test site
        page.goto("https://the-internet.herokuapp.com/login")
        
        # 2. Take a screenshot before login
        page.screenshot(path="before_login.png")
        
        # 3. Fill in username and password
        page.fill("#username", "tomsmith")
        page.fill("#password", "SuperSecretPassword!")
        
        # 4. Click the login button
        page.click("button[type='submit']")
        
        # 5. Wait for page to load
        page.wait_for_load_state("networkidle")
        
        # 6. Extract success message
        success_text = page.locator(".flash.success").text_content()
        print(f"Login result: {success_text}")
        
        # 7. Take screenshot after login
        page.screenshot(path="after_login.png")
        
        # 8. Extract all text from the page
        all_text = page.locator("body").inner_text()
        print("\n--- Page text sample ---")
        print(all_text[:500])  # first 500 chars
        
        browser.close()
        return success_text

if __name__ == "__main__":
    result = test_login_and_extract()
    print(f"\n✅ Test completed: {result}")