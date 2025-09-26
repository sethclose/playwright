import pandas as pd
import log.logging as logging
from playwright.sync_api import sync_playwright
import steps

# Config
config_df = pd.read_csv("data/config.csv", index_col=0)
config_df.head()
headless = True if config_df.loc["headless"].value == "TRUE" else False
trace_mode = True if config_df.loc["trace_mode"].value == "TRUE" else False
trace_file = config_df.loc["trace_file"].value
screenshots = True if config_df.loc["screenshots"].value == "TRUE" else False

# Logging
log_file_name = 'log/log.txt'
with open(log_file_name, 'w', encoding='utf-8') as file:
    log_file = logging.Log(file, log_file_name, trace_mode, screenshots)
    log_file.start_file()
    log_file.s('playwright')

    with sync_playwright() as play:
        log_file.s('main')

        log_file.w("Launching browser")
        browser = play.chromium.launch(headless=headless)

        page, context = steps.start_page(l=log_file, browser=browser)
        steps.go_to_page(log_file, page, 0)

        if steps.is_login(log_file, page, 0):

            steps.log_in(log_file, page, 0)

            steps.start_quote(log_file, page)
            steps.customer_search(log_file, page)

            #steps.log_out(log_file, page, 0)

        log_file.e() # sync
        steps.inspect_page(log_file, page)
        steps.stop_page(log_file, browser, context, trace_mode, trace_file)

    log_file.e() # playwright

