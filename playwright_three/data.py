import pandas as pd
import os
import tools
import log

# Create a new folder (output for new tests)
def make_folder(folder_name:str):
    try:
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        #print(f"Folder '{folder_name}' already exists.")
        pass
    except FileNotFoundError:
        print(f"Error:  Folder '{folder_name}' could not be created.")

# Get Test Data
def get_test_data(dir_path: str, config_name: str) -> dict:
    xls_files = os.listdir(dir_path)
    xls_dfs_dict = {}
    for n, file in enumerate(xls_files):
        if file.find(".xls") >= 0 and file.find("~$") == -1:
            file_path = f"{dir_path}/{file}"
            print(f"Test File #{n+1}:  {file_path}")
            df_dict = pd.read_excel(file_path, sheet_name=None, na_values='', keep_default_na=False)
            skip_steps = []
            step_num = 0
            for step, df in df_dict.items():

                # Config Sheet
                if step == config_name:
                    skip_steps = df[df['name']=='skip_steps'].iloc[0]['value']
                    skip_steps = tools.str_to_int_list(skip_steps)

                else:
                # Not the Config Sheet

                    step_num += 1
                    if step_num not in skip_steps:

                        #print(f"\nStep: {step} Initial Values:")
                        #row_count = 0
                        #for i, action in df.iterrows():
                        #    row_count += 1
                        #    print_row = ""
                        #    for key, value in action.items():
                        #        print_row += f" {key}:{value} *"
                        #    print(f"[{i}] {print_row}")

                        # Missing values and Column Types
                        df.dropna(subset=['type', 'name'], inplace=True)
                        df['screen'] = df['screen'].fillna("").astype(str)
                        df['value'] = df['value'].fillna("").astype(str)
                        df['iteration'] = df['iteration'].fillna(1).astype(int)
                        df['attribute'] = df['attribute'].fillna("")
                        df['wait'] = df['wait'].apply(tools.string_to_bool)
                        df['eval'] = df['eval'].apply(tools.string_to_bool)
                        df['debug'] = df['debug'].apply(tools.string_to_bool)
                        df['skip'] = df['skip'].apply(tools.string_to_bool)
                        df['pics'] = df['pics'].fillna("")
                        df['sleep'] = df['sleep'].fillna(0)

                        #print(f"Step: {step} Updated Values:")
                        #for i, action in df.iterrows():
                        #    print_row = ""
                        #    for key, value in action.items():
                        #        print_row += f" {key}:{value} *"
                        #    print(f"[{i}] {print_row}")
                        #
                        #dropped_row_count = row_count - len(df)
                        #if dropped_row_count > 0:
                        #    print(f"    Dropped {dropped_row_count-len(df)} rows(s) missing type or field values.")

            xls_dfs_dict[file] = df_dict
    return xls_dfs_dict

# Get Test Data
def get_control_data(dir_path: str, config_name: str) -> dict:
    xls_files = os.listdir(dir_path)
    xls_dfs_dict = {}
    for n, file in enumerate(xls_files):
        if file.find(".xls") >= 0 and file.find("~$") == -1:
            file_path = f"{dir_path}/{file}"
            #print(f"Control File #{n+1}:  {file_path}")
            df_dict = pd.read_excel(file_path, sheet_name=None, na_values='', keep_default_na=False)
            skip_steps = []
            step_num = 0
            for step, df in df_dict.items():

                # Config Sheet
                if step == config_name:
                    skip_steps = df[df['name']=='skip_steps'].iloc[0]['value']
                    skip_steps = tools.str_to_int_list(skip_steps)

                else:
                # Not the Config Sheet

                    step_num += 1
                    if step_num not in skip_steps:

                        #print(f"\nStep: {step} Initial Values:")
                        #row_count = 0
                        #for i, action in df.iterrows():
                        #    row_count += 1
                        #    print_row = ""
                        #    for key, value in action.items():
                        #        print_row += f" {key}:{value} *"
                        #    print(f"[{i}] {print_row}")

                        # Missing values and Column Types
                        df.dropna(subset=['type', 'name'], inplace=True)
                        df['screen'] = df['screen'].fillna("").astype(str)
                        df['value'] = df['value'].fillna("").astype(str)
                        df['iteration'] = df['iteration'].fillna(1).astype(int)
                        df['attribute'] = df['attribute'].fillna("")
                        df['wait'] = df['wait'].apply(tools.string_to_bool)
                        df['eval'] = df['eval'].apply(tools.string_to_bool)
                        df['debug'] = df['debug'].apply(tools.string_to_bool)
                        df['skip'] = df['skip'].apply(tools.string_to_bool)
                        df['pics'] = df['pics'].fillna("")
                        df['sleep'] = df['sleep'].fillna(0)

                        df['previous'] = df['previous'].fillna("")
                        df['result'] = df['result'].fillna("")
                        df['time'] = df['time'].fillna("")

                        #print(f"Step: {step} Updated Values:")
                        #for i, action in df.iterrows():
                        #    print_row = ""
                        #    for key, value in action.items():
                        #        print_row += f" {key}:{value} *"
                        #    print(f"[{i}] {print_row}")
                        #
                        #dropped_row_count = row_count - len(df)
                        #if dropped_row_count > 0:
                        #    print(f"    Dropped {dropped_row_count-len(df)} rows(s) missing type or field values.")

            xls_dfs_dict[file] = df_dict
    return xls_dfs_dict

def get_field_attributes(dir_path: str, file_name: str) -> pd.DataFrame:
    file_path = f"{dir_path}/{file_name}"
    print(f"Retrieving field data from '{file_path}'")
    df_fields = pd.read_csv(file_path, keep_default_na=False)
    #print(f"  Field DataFrame.head():\n {df_fields.head()}")
    row_count = 0
    for i, field in df_fields.iterrows():
        row_count += 1
        print_row = ""
        for key, value in field.items():
            print_row += f" {key}:{value} *"
        #print(f"[{i}] {print_row}")
    return df_fields


def write_output_workbook(l: log.Log, df_dict: dict):
    l.s('Write output workbook')
    file_name = f'{l.test_name}_result.xlsx' # _{tools.get_date_stamp()}_result.xlsx'
    with pd.ExcelWriter(f'{l.output_path}/{file_name}', engine='xlsxwriter') as writer:
        for step_name, df in df_dict.items():
            l.w(f"'{step_name}' output data saving to '{l.output_path}/{file_name}' sheet '{step_name}'")
            df.to_excel(writer, sheet_name=step_name, index=False)
            # Fit column widths
            worksheet = writer.sheets[step_name]
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2  # Add a little padding
                worksheet.set_column(i, i, max_len)
    l.e()

def update_result_workbook(l: log.Log, test_dict: dict):
    l.s('Update output workbook')
    l.w(f"Updating Workbook after all steps in {l.test_name}")
    try:
        write_output_workbook(l, test_dict)
    except PermissionError:
        input(f"\nDo you - by any chance - have the {l.test_name} result workbook open?  ")
        try:
            write_output_workbook(l, test_dict)
            print(f"Thanks, Updated Workbook {l.test_name}", end="...  ")
        except PermissionError:
            try_count = 0
            success = False
            prompts = [f"It's the {l.test_name} result workbook.  Hit enter when it's closed.",
                       f"Whatever you did - it didn't work. Try again.",
                       f"I'm beginning to doubt whether you want it updated.  Try harder."]
            while try_count < 3 and success is False:
                input(prompts[try_count])
                try_count += 1
                try:
                    write_output_workbook(l, test_dict)
                    success = True
                except PermissionError:
                    success = False
            if success:
                print(f"Thanks, Updated Workbook {l.test_name}", end="...  ")
            else:
                print("No soup for you!")
    l.e()

def compare_test_workbooks(l: log.Log, config_sheet: str, test_name: str, test_dict: dict, controls: dict, file_path: str):
    l.s(f"Compare Test '{test_name}' to Control")

    l.w(f"Opening '{file_path}'")
    with open(file_path, 'w', encoding='utf-8') as file:

        for control_file_name, control_steps_dict in controls.items():
            #l.w(f"  File:'{control_file_name}'")
            control_test_name = control_file_name[:control_file_name.find('.')]
            if control_test_name == test_name:
                l.w(f"  Matched Test: '{control_test_name}'")
                for step_name, test_df in test_dict.items():
                    if step_name != config_sheet:
                        #l.w(f"    Test Step:'{step_name}'")
                        for control_step_name, control_df in control_steps_dict.items():
                            #l.w(f"      Control Step:'{control_step_name}'")
                            if step_name == control_step_name:
                                l.w(f"        Matched Step: '{control_step_name}'")
                                for test_action_index, test_action in test_df.iterrows():
                                    #l.w(f"          Test Action: {test_action_index} - {test_action['screen']} - {test_action['type']} - {test_action['name']}")
                                    for control_action_index, control_action in control_df.iterrows():
                                        if test_action_index == control_action_index:
                                            l.w(f"            Matched Action: {control_action_index} - {control_action['screen']} - {control_action['type']} - {control_action['name']}")
                                            l.w(f"                 test results - {test_action['previous']} - {test_action['result']} - {test_action['time']}")
                                            l.w(f"              control results - {control_action['previous']} - {control_action['result']} - {control_action['time']}")

                                            # Previous Value Result Difference
                                            if test_action['previous'] != control_action['previous']:
                                                l.w(f"                   diff previous    {step_name}   {control_action['screen']}   {control_action['type']}   {control_action['name']}:  {test_action['previous']} != {control_action['previous']}")
                                                file.write(f"Step:{step_name}   Screen:{control_action['screen']}   Action:{control_action['name']}:  Previous Change:{test_action['previous']} != {control_action['previous']} \n")

                                            # New Value Result Difference
                                            if test_action['result'] != control_action['result']:
                                                l.w(f"                   diff results     {step_name}   {control_action['screen']}   {control_action['type']}   {control_action['name']}:  {test_action['result']} != {control_action['result']}")
                                                file.write(f"Step:{step_name}   Screen:{control_action['screen']}   Action:{control_action['name']}:  Result Change: '{test_action['result']}' != '{control_action['result']}' \n")

                                            # Time Difference
                                            if test_action['time'] != "":
                                                test_time = float(test_action['time'])
                                                if control_action['time'] != "":
                                                    control_time = float(control_action['time'])
                                                    max_time_percent_change = 75 # Percent
                                                    time_percent_change = 100 * (test_time - control_time) / control_time
                                                    time_direction = None
                                                    if (time_percent_change > max_time_percent_change and time_percent_change > 0) or (-time_percent_change > max_time_percent_change and time_percent_change < 0):
                                                        file.write(f"Step:{step_name}   Screen:{control_action['screen']}   Action:{control_action['name']}:  Time Change: {time_percent_change:.1f}% \n")


                    else:
                        l.w(f"    Skipping Config Step")

    l.e()