import pandas as pd
import os
import tools

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
                #print(df)
            xls_dfs_dict[file] = df_dict
    return xls_dfs_dict

# Create test_result_df
output_path = 'data/testing/output'
tools.make_folder(output_path)
date_stamp = tools.get_date_stamp()
test_df_dict = get_test_data()
#print(test_df_dict)
for test_file_name, df_dict in test_df_dict.items():
    test_name = test_file_name[:test_file_name.find('.')]
    print(test_name)
    print(df_dict)
    path = f'{output_path}/{test_name}/{date_stamp}'
    tools.make_folder(f"{output_path}/{test_name}")
    tools.make_folder(f"{output_path}/{test_name}/{tools.get_date_stamp()}")
    file_name = f'{test_name}_{date_stamp}_result.xlsx'
    # Make Test DF and Save
    with pd.ExcelWriter(f'{path}/{file_name}', engine='openpyxl') as writer:
        for step_name, df in df_dict.items():
            print(step_name)
            print(df)
            df.to_excel(writer, sheet_name=step_name, index=False)
