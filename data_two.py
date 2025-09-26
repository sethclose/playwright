import os
import glob
import openpyxl
import pandas as pd

directory_path = 'data' # Replace with your actual directory
excel_files = glob.glob(os.path.join(directory_path, '*.xls*'))
for file in excel_files:
    if file.find("~$") == -1:
        print(f"  => {file}")
    else:
        print(f"  X> {file}")
        excel_files.remove(file)
print(f"Found {len(excel_files)} xls file(s)")

all_dataframes = {} # Dictionary to store DataFrames from each file
for file_path in excel_files:
    try:
        # Read all sheets into a dictionary of DataFrames
        dfs = pd.read_excel(file_path, sheet_name=None)
        all_dataframes[os.path.basename(file_path)] = dfs
        print(f"Successfully loaded data from: {os.path.basename(file_path)}")
        first_sheet_name = list(dfs.keys())[0]
        df_first_sheet = dfs[first_sheet_name]
        print(f"First sheet name: {first_sheet_name}")
        print(f"{dfs.keys()}")
        for key, df in dfs.items():
            print(f"sheet:  {key}")  #:\n{df}")

    except Exception as e:
        print(f"Error loading data from {os.path.basename(file_path)}: {e}")

for file_path in excel_files:
    try:
        workbook = openpyxl.load_workbook(file_path)
        print(f"Successfully opened workbook: {os.path.basename(file_path)}")
        # You can now work with the workbook object, e.g.,
        # sheet = workbook.active
        # print(f"Active sheet name: {sheet.title}")
    except Exception as e:
        print(f"Error opening {os.path.basename(file_path)}: {e}")