import pandas as pd
import os
import tools
import log
import xlsxwriter # You don't need it imported, but formatting won't work if it's not installed.

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
test_dir = 'data/testing/tests'
def get_test_data(dir_path: str = test_dir) -> dict:
    #dir_path = 'data/testing/tests'  # Replace with your actual directory
    #print(f"dir_path: {dir_path}")
    xls_files = os.listdir(dir_path)
    xls_dfs_dict = {}
    for file in xls_files:
        if file.find(".xls") >= 0 and file.find("~$") == -1:
            file_path = f"{dir_path}/{file}"
            #print(f"{file_path=}")
            df_dict = pd.read_excel(file_path, sheet_name=None)
            for key, df in df_dict.items():
                #print(f"\nkey: {key}\n df: {type(df)}")
                df.dropna(subset=['type', 'iteration', 'field'], inplace=True)
                # print(df)
            xls_dfs_dict[file] = df_dict
    return xls_dfs_dict

def write_output_workbook(l: log.Log, df_dict: dict):
    l.s('Write output workbook')
    file_name = f'{l.test_name}_{tools.get_date_stamp()}_result.xlsx'
    with pd.ExcelWriter(f'{l.output_path}/{file_name}', engine='xlsxwriter') as writer:
        for step_name, df in df_dict.items():
            l.w(f"'{step_name}' output data saved to '{l.output_path}/{file_name}' sheet '{step_name}'")
            df.to_excel(writer, sheet_name=step_name, index=False)
            # Fit column widths
            workbook = writer.book
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
    except PermissionError as e:
        input(f"\nDo you - by any chance - have the {l.test_name} result workbook open?  ")
        try:
            write_output_workbook(l, test_dict)
            print(f"Thanks, Updated Workbook {l.test_name}", end="...  ")
        except PermissionError as e:
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
                except PermissionError as e:
                    success = False
            if success:
                print(f"Thanks, Updated Workbook {l.test_name}", end="...  ")
            else:
                print("No soup for you!")
    l.e()
