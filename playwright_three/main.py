# Be sure to first install playwright, xlsxwriter, openpyxl, pandas
from playwright.sync_api import sync_playwright
from datetime import datetime as dt
import time
import steps
import log
import data
from config import Config
import tools

input_path = 'data/testing/Tests'
output_path = 'data/testing/Output'
control_path = 'data/testing/Control'
config_sheet = 'Config'
fields_path = 'data'
fields_file_name = 'field_data.csv'
data.make_folder(output_path)

# Retrieve Test Data - a dictionary of test dataframes as steps holding rows as actions
tests = data.get_test_data(input_path, config_sheet)

# Retrieve Test Control Data - a dictionary of test dataframes as steps holding rows as actions
controls = data.get_control_data(control_path, config_sheet)

# Retrieve Field Data - allows look up of unique element ids by screen, name, and type
fields_df = data.get_field_attributes(fields_path, fields_file_name)

# Run Tests
for test, test_dict in tests.items():

    # Logging
    test_name = test[:test.find('.')]  #.replace("-", "").title().replace(" ", "")
    input_file_path = input_path + '/' + test_name
    log_file_name = test_name + '_' + 'log.txt' # + '_' + tools.get_date_stamp() + '_' + 'log.txt'

    # Configuration
    config = Config(test_dict[config_sheet])

    # Output
    data.make_folder(output_path + '/' + test_name)
    data.make_folder(output_path + '/' + test_name + '/' + tools.get_date_stamp())
    data.make_folder(output_path + '/' + test_name + '/' + tools.get_date_stamp() + '/' + 'screenshots')
    test_output_path = output_path + '/' + test_name + '/' + tools.get_date_stamp()
    output_file_path = test_output_path + '/' + log_file_name
    print(f"Log File: '{output_file_path}'")

    # Notifications
    notifications_file_name = test_name + '_' + 'notifications.txt'
    notifications_file_path = test_output_path + '/' + notifications_file_name
    print(f"Notifications: '{notifications_file_path}'")

    # Test
    print("")
    print(f"Running test: '{test_name}'  '{input_file_path}'  =>  '{output_file_path}' [{dt.now():%H:%M:%S}]")
    print(f"  {config.display()}")
    start_time = time.perf_counter()

    # Start Logging
    with open(output_file_path, 'w', encoding='utf-8') as file:
        log_file = log.Log(file, test_name=test_name, output_path=test_output_path, trace_mode=config.trace_mode, screenshots=config.screenshots)
        log_file.start_file()
        log_file.s(f"Test {test_name}")
        log_file.w(config.display())

        # Start Playwright
        with sync_playwright() as play:
            log_file.s('Play')
            log_file.w("Launching browser")
            if config.browsers[0] == 'Chrome':
                browser = play.chromium.launch(headless=config.headless)
            elif config.browsers[0] == 'Firefox':
                browser = play.firefox.launch(headless=config.headless)
            page, context = steps.start(l=log_file, browser=browser)
            steps.go(log_file, page, 0, config.url)

            # Execute Steps of Test
            step_num = 0
            for step_name, step_df in test_dict.items():
                if step_name != config_sheet:
                    step_num += 1
                    if step_num not in config.skip_steps:
                        print(f"    Running step {step_num}: {step_name:>30}", end="    ")
                        step_df = steps.step(l=log_file, fields=fields_df, page=page, step_name=step_name, step_df=step_df)
                        test_dict[step_name] = step_df
                        print()
            print(f"\n    Completed Steps testing for {test_name} [{time.perf_counter()-start_time:.1f} seconds]")

            print(f"    Comparing Output Workbook to Control for {test_name}")
            data.compare_test_workbooks(log_file, config_sheet, test_name, test_dict, controls, notifications_file_path)

            print(f"    Updating Workbook after all steps in {test_name}")
            data.update_result_workbook(log_file, test_dict)

            if config.inspect:
                print("    Launching Playwright Inspector.  Close the Inspector Window to CONTINUE.")
                steps.inspect(log_file, page)

            print(f"    Stopping Playwright for {test_name} [{time.perf_counter()-start_time:.1f} seconds to complete full test]")
            steps.stop(log_file, browser, context, config.trace_mode, config.trace_file)

            log_file.e()  # Play

        log_file.e() # Test
    print(f"    Completed test: '{test_name}'  '{input_file_path}'  =>  '{output_file_path}' [{time.perf_counter()-start_time:.1f} seconds]")
