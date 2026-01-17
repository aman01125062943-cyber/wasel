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
        # -> Navigate to the correct login or home page URL to start the onboarding process for WhatsApp sessions.
        await page.goto('http://localhost:3001/', timeout=10000)
        await asyncio.sleep(3)
        

        # -> Click on the login link to proceed with user authentication.
        frame = context.pages[-1]
        # Click on the 'دخول' (Login) link to go to the login page
        elem = frame.locator('xpath=html/body/header/div/nav/a[4]').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Input username and password, then click the login button to authenticate.
        frame = context.pages[-1]
        # Input username/email
        elem = frame.locator('xpath=html/body/div/form/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('aman01125062943@gmail.com')
        

        frame = context.pages[-1]
        # Input password
        elem = frame.locator('xpath=html/body/div/form/div[2]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('1994')
        

        frame = context.pages[-1]
        # Click login button to submit credentials
        elem = frame.locator('xpath=html/body/div/form/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Click on the 'جلساتي' (My Sessions) section to navigate to WhatsApp sessions management.
        frame = context.pages[-1]
        # Click on 'جلساتي' (My Sessions) to manage WhatsApp sessions
        elem = frame.locator('xpath=html/body/div[2]/aside/nav/div[2]').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Click on 'إضافة جلسة جديدة' (Add New Session) button to create a new WhatsApp session and generate QR code.
        frame = context.pages[-1]
        # Click on 'إضافة جلسة جديدة' (Add New Session) to create a new WhatsApp session
        elem = frame.locator('xpath=html/body/div[2]/main/div[8]/div/div[2]/button[2]').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Fill in the session name and phone number fields, then click the 'إنشاء وربط الجلسة' (Create and Link Session) button to generate the QR code for scanning.
        frame = context.pages[-1]
        # Input session name
        elem = frame.locator('xpath=html/body/div[11]/div/form/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('Test Session 1')
        

        frame = context.pages[-1]
        # Input phone number
        elem = frame.locator('xpath=html/body/div[11]/div/form/div[2]/div/div[2]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('123456789')
        

        frame = context.pages[-1]
        # Click 'إنشاء وربط الجلسة' (Create and Link Session) button to generate QR code
        elem = frame.locator('xpath=html/body/div[11]/div/form/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Click the 'ربط' (Link) button for the created session to generate and display the QR code for scanning with WhatsApp app.
        frame = context.pages[-1]
        # Click 'ربط' (Link) button to generate QR code for the session
        elem = frame.locator('xpath=html/body/div[2]/main/div[8]/div[3]/table/tbody/tr/td[7]/div/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # --> Assertions to verify final state
        frame = context.pages[-1]
        try:
            await expect(frame.locator('text=Session Connected Successfully').first).to_be_visible(timeout=1000)
        except AssertionError:
            raise AssertionError("Test case failed: The WhatsApp session did not connect successfully or the connection status is not displayed correctly as required by the test plan.")
        await asyncio.sleep(5)
    
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
            
asyncio.run(run_test())
    