from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
import time
import pytest.test_brm as pt

# Playwright + Python: Framework for Automation Web Testing | Installation & Demo (JoanMedia)
# https://www.youtube.com/watch?v=FK_5SQPq6nY [playwright]

sync_mode = True
async_mode = False
headless_mode = False
trace_mode = True


def sync_main():
    with sync_playwright() as p:
        print('Starting Run')
        browser = p.chromium.launch(headless=headless_mode)

        print("  Running")
        page, context = pt.start_page(browser, trace_mode=trace_mode)
        pt.goto_brm(page)
        page.screenshot(path="./screenshot_brm.png")

        # Test Cases
        if  pt.is_login(page):
            pt.log_in(page, 10)
            pt.start_new_quote(page)
            pt.all_locators(page)
            #pt.start_quote(page)
            #pt.log_out(page)

        print("  Finished")

        page.pause()
        pt.stop_page(browser, context, trace_mode)
        print('Finished Run')


async def async_main():
    print("Starting Async Run")
    async with async_playwright() as p_async:
        browser_async = await p_async.chromium.launch(headless=headless_mode)
        page_async = await browser_async.new_page()
        await page_async.goto("https://uwd125.duckcreekondemand.com/Policy/express.aspx")
        time.sleep(10)
        print(f"  {await page_async.title()}")
        await page_async.screenshot(path="./screenshot_brm.png")
        await page_async.pause()
        await browser_async.close()
    print("Finished Async Run")


if sync_mode:
    sync_main()

if async_mode:
    asyncio.run(async_main())
