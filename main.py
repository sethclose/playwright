from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
import time
import comps

sync_mode = True
async_mode = False
headless_mode = False
trace_mode = True

def sync_main():
    with sync_playwright() as p:
        print('Starting Run')
        browser = p.chromium.launch(headless=headless_mode)

        print("  Running")
        page, context = comps.start_page(browser, trace_mode=trace_mode)
        comps.goto_brm(page)
        page.screenshot(path="./log/screenshots/login.png")

        # Test Cases
        if  comps.is_login(page):
            comps.log_in(page, 10)

            #comps.start_quote(page)

            #comps.start_quote_new_party(page)
            #comps.new_quote_party(page)

            comps.open_existing_quote(page)

            #comps.start_quote_old_party(page)
            #comps.finish_named_insured(page)

            #comps.underwriting_questions(page)

            #comps.dwelling_information(page)
            #comps.dwelling_information_360(page)

            #comps.rate_summary(page)
            #comps.payment_details(page)

            #comps.log_out(page)

        print("  Finished")

        page.pause()
        comps.stop_page(browser, context, trace_mode)
        print('Finished Run')

if sync_mode:
    sync_main()



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
if async_mode:
    asyncio.run(async_main())
