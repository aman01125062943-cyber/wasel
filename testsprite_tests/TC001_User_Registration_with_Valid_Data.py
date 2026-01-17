import asyncio
import uuid
from playwright import async_api
from playwright.async_api import expect


async def run_test():
    pw = None
    browser = None
    context = None

    try:
        pw = await async_api.async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        context.set_default_timeout(15000)

        page = await context.new_page()

        unique = uuid.uuid4().hex[:8]
        name = f"Aman Tester {unique}"
        phone = f"010{int(unique, 16) % 100000000:08d}"
        email = f"test_{unique}@example.com"
        password = "TestPassword123!"

        await page.goto("http://localhost:3001/register", wait_until="domcontentloaded", timeout=30000)

        await page.locator('input[name="name"]').fill(name)
        await page.locator('input[name="phone"]').fill(phone)
        checkbox = page.locator('input[name="isWhatsapp"]')
        if await checkbox.count() > 0:
            if not await checkbox.is_checked():
                await checkbox.check()
        await page.locator('input[name="email"]').fill(email)
        await page.locator('input[name="password"]').fill(password)

        await page.locator('form[action="/register"] button[type="submit"]').click()

        await page.wait_for_url("**/dashboard**", timeout=30000)
        await expect(page.locator(f"text=مرحباً، {name}").first).to_be_visible(timeout=30000)
        await asyncio.sleep(1)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()


asyncio.run(run_test())
asyncio.run(run_test())
    
