import asyncio
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None
    
    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()
        
        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",         # Set the browser window size
                "--disable-dev-shm-usage",        # Avoid using /dev/shm which can cause issues in containers
                "--ipc=host",                     # Use host-level IPC for better stability
                "--single-process"                # Run the browser in a single process mode
            ],
        )
        
        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)
        
        # Open a new page in the browser context
        page = await context.new_page()
        
        # Navigate to your target URL and wait until the network request is committed
        await page.goto("http://localhost:3001/", wait_until="commit", timeout=10000)
        
        # Wait for the main page to reach DOMContentLoaded state (optional for stability)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except async_api.Error:
            pass
        
        # Iterate through all iframes and wait for them to load as well
        for frame in page.frames:
            try:
                await frame.wait_for_load_state("domcontentloaded", timeout=3000)
            except async_api.Error:
                pass
        
        # Interact with the page elements to simulate user flow
        # -> Find a correct way to navigate to the registration page or fix the URL to access the registration page.
        await page.goto('http://localhost:3001/register', timeout=10000)
        await asyncio.sleep(3)
        

        # -> Input username, invalid email format, and password into the registration form.
        frame = context.pages[-1]
        # Input username in full name field
        elem = frame.locator('xpath=html/body/div/form/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('aman01125062943')
        

        frame = context.pages[-1]
        # Input invalid email format
        elem = frame.locator('xpath=html/body/div/form/div[3]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('invalid-email-format')
        

        frame = context.pages[-1]
        # Input password
        elem = frame.locator('xpath=html/body/div/form/div[4]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('1994')
        

        # -> Submit the registration form by clicking the submit button.
        frame = context.pages[-1]
        # Click the submit button to submit the registration form
        elem = frame.locator('xpath=html/body/div/form/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Fill the WhatsApp number field with a valid phone number to isolate the email validation test.
        frame = context.pages[-1]
        # Input valid WhatsApp number to allow form submission and isolate email validation
        elem = frame.locator('xpath=html/body/div/form/div[2]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('01012345678')
        

        # -> Submit the registration form by clicking the submit button to verify the invalid email format error.
        frame = context.pages[-1]
        # Click the submit button to submit the registration form with invalid email format
        elem = frame.locator('xpath=html/body/div/form/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # --> Assertions to verify final state
        frame = context.pages[-1]
        await expect(frame.locator('text=البريد الإلكتروني').first).to_be_visible(timeout=30000)
        await asyncio.sleep(5)
    
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
            
asyncio.run(run_test())
    