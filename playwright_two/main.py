import time

from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime as dt
import steps
import log
import data
import tools

# Config
config_df = pd.read_csv("data/config.csv", index_col=0)
config_df.head()
headless = True if config_df.loc["headless"].value == "TRUE" else False
trace_mode = True if config_df.loc["trace_mode"].value == "TRUE" else False
trace_file = config_df.loc["trace_file"].value
screenshots = True if config_df.loc["screenshots"].value == "TRUE" else False

input_path = 'data/testing/active'
output_path = 'data/testing/output'
data.make_folder(output_path)

# Retrieve Test Data and Run Tests
tests = data.get_test_data(input_path)
for test, test_dict in tests.items():

    # Set up logging
    test_name = test[:test.find('.')].replace("-", "").title().replace(" ", "")
    input_file_path = input_path + '/' + test_name
    log_file_name = test_name + '_' + tools.get_date_stamp() + '_log.txt'

    # Output locations
    data.make_folder(output_path + '/' + test_name)
    data.make_folder(output_path + '/' + test_name + '/' + tools.get_date_stamp())
    test_output_path = output_path + '/' + test_name + '/' + tools.get_date_stamp()
    output_file_path = test_output_path + '/' + log_file_name

    print(f"Running test: '{test_name}'  '{input_file_path}'  =>  '{output_file_path}' [{dt.now():%H:%M:%S}]")
    start_time = time.perf_counter()

    # Start Logging
    with open(output_file_path, 'w', encoding='utf-8') as file:
        log_file = log.Log(file, test_name=test_name, output_path=test_output_path, trace_mode=trace_mode, screenshots=screenshots)
        log_file.start_file()
        log_file.s(f"Test {test_name}")

        # Start Playwright
        with sync_playwright() as play:
            log_file.s('Play')
            log_file.w("Launching browser")
            browser = play.chromium.launch(headless=headless)
            page, context = steps.start(l=log_file, browser=browser)
            steps.go(log_file, page, 0)

            # Execute Tests for Step
            for step_name, step_df in test_dict.items():
                print(f"    Running step:{step_name:>30}", end="    ")
                step_df = steps.step(l=log_file, page=page, step_name=step_name, step_df=step_df)
                test_dict[step_name] = step_df
                print("")

            print(f"Completed application testing for {test_name} [{time.perf_counter() - start_time:.1f} seconds]")

            print(f"Updating Workbook after all steps in {test_name}")
            data.update_result_workbook(log_file, test_dict)

            print("Launching Playwright Inspector.  CLOSE the Inspector Window to CONTINUE.")
            steps.inspect(log_file, page)

            print(f"Stopping Playwright for {test_name} [{time.perf_counter()-start_time:.1f} seconds to complete full test]")
            steps.stop(log_file, browser, context, trace_mode, trace_file)

            log_file.e()  # Play

        log_file.e() # Test
    print(f"Completed test: '{test_name}'  '{input_file_path}'  =>  '{output_file_path}' [{time.perf_counter()-start_time:.1f} seconds]")