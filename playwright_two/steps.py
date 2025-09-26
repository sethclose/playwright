from playwright.sync_api import Page
import os
import time
import log.logging as logging
import data
import locus
import tools

DEV21_URL = os.environ.get('DEV21_URL')
AGENT_USER = os.environ.get('AGENT_USER')
AGENT_PASS = os.environ.get('AGENT_PASS')

def start_page(l: logging.Log, browser):
    """
    Starts Playwright session
    :param l: Log file object
    :param browser: Playwright browser object
    """
    l.s("start_page")
    context = browser.new_context(viewport=None)
    if l.trace_mode:
        l.w("Start Tracing")
        context.tracing.start(screenshots=l.screenshots, snapshots=True, sources=True)
    else:
        l.w("Not Tracing")
    page = browser.new_page()
    tools.take_ss(l, page, "start_page")
    l.e()
    return page, context

def go_to_page(l: logging.Log, page: Page, sleep: int=0):
    l.s("go_to_page")
    page.goto(DEV21_URL)
    time.sleep(sleep)
    page.screenshot(path=f"./log/screenshots/{'go_to_page'}.png")
    tools.take_ss(l, page, "go_to_page")
    l.e()

def is_login(l: logging.Log, page: Page, sleep: int=0):
    l.s("is_login")
    tools.page_wait(l, page)
    page_title_correct = "Sign in"
    try:
        assert page.title() == page_title_correct
        l.w(f"    {page.title()} page found.")
    except AssertionError:
        l.w(f"    '{page.title()}' did not match expected: '{page_title_correct}'.")
        return False
    time.sleep(sleep)
    tools.take_ss(l, page, "is_login")
    l.e()
    return True

def log_in(l: logging.Log, page: Page, sleep: int=0):
    l.s("log_in")
    tools.page_wait(l, page)
    #l.w(f"{AGENT_USER=}:{AGENT_PASS=}")
    page.locator("#signInName").fill(AGENT_USER)
    page.locator("#password").fill(AGENT_PASS)
    page.locator("#next").click()  # Sign in
    time.sleep(sleep)
    tools.take_ss(l, page, "log_in")
    l.e()

def start_quote(l: logging.Log, page: Page):
    l.s("start_quote")
    # Do each field in Quote Term
    for item in data.xlsx_rows('seth_test', 'new_quote', 'Quote', 'Term'):
        l.w(f"*** {item['screen']} * {item['section']} * {item['type']} * {item['field']} * {item['value']} ***")
        locus.do_loc(l, page, locator_type=item['type'], locator_name=item['field'], iteration=item['iteration'], value=item['value'], sleep=item['sleep'])
    l.e()

def customer_search(l: logging.Log, page: Page):
    l.s("customer_search")
    tools.page_wait(l, page)
    for item in data.xlsx_rows('seth_test', 'new_quote', 'Quote', 'Customer Search'):
        l.w(f"*** {item['screen']} * {item['section']} * {item['type']} * {item['field']} * {item['value']} ***")
        locus.do_loc(l, page, locator_type=item['type'], locator_name=item['field'], iteration=item['iteration'], value=item['value'], sleep=item['sleep'])
    #locus.do_loc(l, page, 'button', 'Search', iteration=3, sleep=3)
    tools.take_ss(l, page, "customer_search")
    l.e()

def log_out(l: logging.Log, page: Page, sleep: int=0):
    l.s("log_out")
    tools.page_wait(l, page)
    page.locator("#action_0").click() # => top right
    time.sleep(sleep)
    tools.take_ss(l, page, "log_out")
    l.e()

def inspect_page(l: logging.Log, page: Page):
    """Opens Playwright Inspector, rather than closing browser."""
    l.s("inspect_page")
    tools.page_wait(l, page)
    page.pause()
    l.w("Playwright Inspector is ready.")
    l.e()

def stop_page(l: logging.Log, browser, context, trace_mode: bool, trace_file: str):
    l.s("stop_page")
    if trace_mode:
        l.w("End Tracing")
        context.tracing.stop(path=trace_file)
    else:
        l.w("No Tracing")
        l.w(f"{trace_mode=}")
        l.w(f"{trace_file=}")
    context.close()
    browser.close()
    l.e()
