from playwright.sync_api import Page
import pandas as pd
import time
import log
import locus
import tools

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

def go(l: log.Log, page: Page, sleep: int=0, url: str="google.com"):
    l.s("Go to page")
    page.goto(url)
    time.sleep(sleep)
    l.e()

def step(l: log.Log, fields: pd.DataFrame, page: Page, step_name: str, step_df: pd.DataFrame) -> pd.DataFrame:
    l.s("Step")

    # Before
    for i, action in step_df.iterrows():
        if not action['skip']:
            print_row = ""
            for key, value in action.items():
                if value != "":
                    print_row += f" {key}:{value} *"
            l.w(f"[{i}] {print_row}")

    # Instantiate Result columns in Action Series
    step_df['time'] = ''
    step_df['previous'] = ''
    step_df['result'] = ''
    step_df['element'] = ''

    # Perform Action with debugging
    terminal_log_message_length = 0
    for index, action in step_df.iterrows():

            if not action['skip']:

                # Terminal Logging
                message = f"   {action['name']} ({action['type'][0]})"
                terminal_log_message_length += len(message)
                if terminal_log_message_length > 100:
                    print(f"\n                                                      {message}", end="  ")
                    terminal_log_message_length = 0
                else:
                    print(message, end="  ")

                # Setup Debugging, if specified
                prev_mode = l.mode
                if action['debug']:
                    time.sleep(1)
                    l.mode = 'debug'
                    print()
                    l.s("Debugging")

                # Execute Test Action
                result_df = locus.act(l, fields, page, action)

                # End Debugging, if specified
                if action['debug']:
                    l.e()
                    l.mode = prev_mode
                    print(f"    Continuing step:{step_name:>30}", end="    ")

            else: # Skipped
                result_df = action

            step_df.loc[index] = result_df

    # With Result Data
    for i, action in step_df.iterrows():
        if not action['skip']:
            print_row = ""
            for key, value in action.items():
                if value != "":
                    print_row += f" {key}:{value} *"
            l.w(f"[{i}] {print_row}")

    # Screenshoot # THIS SHOULD REALLY BE TRIGGERED BY STEP ACTIONS
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
