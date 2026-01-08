from playwright.sync_api import Page
import pandas as pd
import time
import log
import actions
import tools

def start(l: log.Log, browser):
    """
    Starts Playwright session tracing and page context
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

def go(l: log.Log, page: Page, sleep: int=0, url: str=""):
    """
    Go to the target page specified in Test's Config sheet
    :return:
    """
    l.s("Go to page")
    l.w(f"Opening Browser at {url}")
    page.goto(url)
    time.sleep(sleep)
    l.e()

def step(l: log.Log, fields: pd.DataFrame, page: Page, step_name: str, step_df: pd.DataFrame) -> pd.DataFrame:
    """
    This is the main function that executes test steps
    :return: returns the step_df with result columns
    """
    l.s("Step")

    # Print Input Test Data to log
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

                # Terminal Logging - go to next line when steps list gets too long
                message = f"   {action['name']} ({action['type'][0]})"
                terminal_log_message_length += len(message)
                if terminal_log_message_length > 100:
                    print(f"\n                                                      {message}", end="  ")
                    terminal_log_message_length = 0
                else:
                    print(message, end="  ")

                # Setup Log Debugging, if specified
                prev_mode = l.mode
                if action['debug']:
                    time.sleep(1)
                    l.mode = 'debug'
                    print() # New Line for debugging logging
                    l.s("Debugging")

                # Execute Test Action
                result_df = actions.act(l, fields, page, action)

                # End Debugging, if specified
                if action['debug']:
                    l.mode = prev_mode
                    print(f"    Continuing step:{step_name:>30}", end="    ")
                    l.e()

            else: # Skipped
                result_df = action

            step_df.loc[index] = result_df

    # Print Test Data With Results
    for i, action in step_df.iterrows():
        if not action['skip']:
            print_row = ""
            for key, value in action.items():
                if value != "":
                    print_row += f" {key}:{value} *"
            l.w(f"[{i}] {print_row}")

    l.e()
    return step_df

def inspect(l: log.Log, page: Page):
    """Opens Playwright Inspector, rather than closing browser."""
    l.s("inspect_page")
    page.pause()
    l.w("Playwright Inspector is ready.")
    l.e()

def stop(l: log.Log, browser, context, trace_mode: bool, trace_file: str):
    """
    Writes trace file, closes playwright session and closes browser.
    :param l: the log file object
    :param browser: playwright browser object
    :param context: playwright context object
    :param trace_mode: boolean, whether to trace from Config
    :param trace_file: path to put the trace file
    :return:
    """
    l.s("stop_page")
    trace_file = f"./{l.output_path}/{l.test_name}_{trace_file}" #_{tools.get_date_stamp()}_{trace_file}"
    l.w(f"{trace_mode=}")
    l.w(f"{trace_file=}")
    if trace_mode:
        l.w("End Tracing")
        context.tracing.stop(path=trace_file)
    else:
        l.w("No Tracing")
    context.close()
    browser.close()
    l.e()
