from playwright.sync_api import Page
import pandas as pd
import os
import time
import log
import actions
import tools

DEV21_URL = os.environ.get('DEV21_URL')
AGENT_USER = os.environ.get('AGENT_USER')
AGENT_PASS = os.environ.get('AGENT_PASS')

def start(l: log.Log, browser):
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

def go(l: log.Log, page: Page, sleep: int=0):
    l.s("Go to page")
    page.goto(DEV21_URL)
    time.sleep(sleep)
    l.e()

def step(l: log.Log, page: Page, step_name: str, step_df: pd.DataFrame) -> pd.DataFrame:
    l.s("Step")
    # Initialize Result Columns
    step_df['time'] = ''
    step_df['result'] = ''
    # For each action get result Series back and update step DF
    for index, action in step_df.iterrows():
        if action['override'] == 'skip':
            pass
        else:
            print(f"   {action['field']} ({action['type'][0]})", end="  ")
            returned = actions.act(l, page, action)
            step_df.loc[index] = returned
    # Show all action column indices and values
    for index, action in step_df.iterrows():
        l.w(f"#{index}: {[(i, a) for i, a in action.items()]}")
    tools.take_screenshot(l, page, step_name)
    l.e()
    return step_df

def inspect(l: log.Log, page: Page):
    """Opens Playwright Inspector, rather than closing browser."""
    l.s("inspect_page")
    #tools.page_wait(l, page)
    page.pause()
    l.w("Playwright Inspector is ready.")
    l.e()

def stop(l: log.Log, browser, context, trace_mode: bool, trace_file: str):
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
