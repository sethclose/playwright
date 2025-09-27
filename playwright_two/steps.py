from playwright.sync_api import Page
import os
import time
import log
import actions
import tools

DEV21_URL = os.environ.get('DEV21_URL')
AGENT_USER = os.environ.get('AGENT_USER')
AGENT_PASS = os.environ.get('AGENT_PASS')

def start_page(l: log.Log, browser):
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
    page = context.new_page()
    l.e()
    return page, context

def go_to_page(l: log.Log, page: Page, sleep: int=0):
    l.s("go_to_page")
    page.goto(DEV21_URL)
    time.sleep(sleep)
    l.e()

def do_step(l: log.Log, page: Page, step: str, step_actions: list):
    l.s("Do Step")
    for item in step_actions:
        #l.w(f"[*] {item['screen']} * {item['section']} * {item['type']} * {item['field']} * {item['value']}  * {item['iteration']} * {item['sleep']} [*]")
        actions.do_loc(l, page, locator_type=item['type'], locator_name=item['field'], iteration=item['iteration'], value=item['value'], sleep=item['sleep'])
    l.e()
    tools.take_ss(l, page, step)
    pass

def inspect_page(l: log.Log, page: Page):
    """Opens Playwright Inspector, rather than closing browser."""
    l.s("inspect_page")
    #tools.page_wait(l, page)
    page.pause()
    l.w("Playwright Inspector is ready.")
    l.e()

def stop_page(l: log.Log, browser, context, trace_mode: bool, trace_file: str):
    l.s("stop_page")
    output_file = f"./{l.output_path}/{l.test_name}_{tools.get_date_stamp()}_{trace_file}"
    l.w(f"{trace_mode=}")
    l.w(f"{output_file=}")
    if trace_mode:
        l.w("End Tracing")
        context.tracing.stop(path=output_file)
    else:
        l.w("No Tracing")
    context.close()
    browser.close()
    l.e()
