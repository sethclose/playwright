from playwright.sync_api import sync_playwright
import pandas as pd
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

input_path = 'data/testing/tests'
output_path = 'data/testing/output'
tools.make_folder(output_path)

# Retrieve Test Data and Run Tests
tests = data.get_test_data(input_path)
for test, df_dict in tests.items():

    # Set up logging
    test_name = test[:test.find('.')]
    input_file_path = input_path + '/' + test_name
    log_file_name = test_name + '_' + tools.get_date_stamp() + '_log.txt'

    # Output locations
    tools.make_folder(output_path + '/' + test_name)
    tools.make_folder(output_path + '/' + test_name + '/' + tools.get_date_stamp())
    created_folders = True
    test_output_path = output_path + '/' + test_name + '/' + tools.get_date_stamp()
    output_file_path = test_output_path + '/' + log_file_name

    print(f"Running test: '{test_name}'  '{input_file_path}'  =>  '{output_file_path}'")

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
            page, context = steps.start_page(l=log_file, browser=browser)
            steps.go_to_page(log_file, page, 0)

            # Execute Tests
            for step, step_df in df_dict.items():
                log_file.s(f"Step: {step}")
                steps.do_step(l=log_file, page=page, step=step, step_actions=step_df.to_dict(orient='records'))
                log_file.e()  # Step

            steps.inspect_page(log_file, page)
            steps.stop_page(log_file, browser, context, trace_mode, trace_file)

            log_file.e()  # Play

        log_file.e() # Test
