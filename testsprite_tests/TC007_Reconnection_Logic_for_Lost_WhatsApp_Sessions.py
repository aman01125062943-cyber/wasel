import asyncio
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None
    
    try:
        pw = await async_api.async_playwright().start()
        
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )
        
        context = await browser.new_context()
        context.set_default_timeout(5000)
        
        page = await context.new_page()
        
        await page.goto("http://localhost:3001/", wait_until="commit", timeout=10000)
        
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except async_api.Error:
            pass
        
        for frame in page.frames:
            try:
                await frame.wait_for_load_state("domcontentloaded", timeout=3000)
            except async_api.Error:
                pass
        
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        await page.goto('http://localhost:3001/', timeout=10000)
        await asyncio.sleep(3)

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/header/div/nav/a[4]').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/form/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('aman01125062943@gmail.com')

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/form/div[2]/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('1994')

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div/form/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)

        frame = context.pages[-1]
        elem = frame.locator('xpath=html/body/div[2]/aside/nav/div[2]').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)

        await expect(page.locator('text=جلسات واتساب').first).to_be_visible(timeout=30000)

        async with page.expect_response(lambda r: "/api/whatsapp/list" in r.url and r.request.method == "GET") as resp_info:
            await page.evaluate("reconnectAllSessions()")
        resp = await resp_info.value
        assert resp.status == 200
        sessions = await resp.json()
        assert isinstance(sessions, list)

        await asyncio.sleep(5)
    
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
            
asyncio.run(run_test())
    
