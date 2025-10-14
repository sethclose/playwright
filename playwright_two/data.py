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
            print(f"Test File #{n}:  {file_path}")
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
                        df['wait'] = df['wait'].fillna("").apply(tools.str_to_bool).astype(bool)
                        df['sleep'] = df['sleep'].fillna(0)
                        df['eval'] = df['eval'].fillna("").apply(tools.str_to_bool).astype(bool)
                        df['debug'] = df['debug'].fillna("").apply(tools.str_to_bool).astype(bool)
                        df['skip'] = df['skip'].fillna("").apply(tools.str_to_bool).astype(bool)

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
    file_name = f'{l.test_name}_{tools.get_date_stamp()}_result.xlsx'
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
