import pandas as pd
import os
import openpyxl

# From an XLSX File
print("")
def xlsx_rows(file_name:str, sheet: str, screen:str='*', section:str='*'):
    file_loc = f"data/{file_name}.xlsx"
    df_file = pd.read_excel(file_loc, sheet_name=sheet)
    #print(df_file)
    screen_condition = df_file["screen"] == screen if screen != '*' else df_file["screen"] != "NO"
    section_condition = df_file["section"] == section if section != '*' else df_file["section"] != "NO"
    df_rows = df_file.loc[screen_condition & section_condition]
    df_dict = df_rows.to_dict(orient='records')
    return df_dict
file_name = 'seth_test'
sheet = 'new_quote'
screen = 'Quote'
section = 'Term'
print(f"  {file_name=}, {sheet=}, {screen=}, {section=}")
for item in xlsx_rows(file_name, 'new_quote', 'Quote', 'Term'):
    print(f"  {item['screen']}, {item['section']}, {item['type']}, {item['sleep']}, {item['iteration']}, {item['field']}, {item['value']}")

# Find all XLSX Files
def find_all_files(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file[file.find(".")+1:] == 'xlsx' and file.find("~$") == -1: # Ignore non-xlsx, temp files
                file_paths.append(os.path.join(root, file))

    return file_paths
search_dir = "data"  # Replace with your desired directory path
paths = find_all_files(search_dir)
for file_path in paths:
    print(file_path)

# Find all Sheets in XLSX Files
for file_path in paths:
    try:
        file_path = str(file_path.replace("\\", "/"))
        print(f"Sheets in '{file_path}':")
        workbook = openpyxl.load_workbook(filename=file_path)
        sheet_names = workbook.sheetnames
        for sheet_name in sheet_names:
            for item in xlsx_rows(file_path, sheet_name, '*', '*'):
                print(
                    f"  {item['screen']}, {item['section']}, {item['type']}, {item['sleep']}, {item['iteration']}, {item['field']}, {item['value']}")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")



# From a CSV File
#print("")
def csv_rows(file_name:str, screen:str, section:str):
    file_loc = f"data/{file_name}.csv"
    df_file = pd.read_csv(file_loc)
    df_rows = df_file.loc[(df_file["screen"] == screen) & (df_file["section"] == section)]
    df_dict = df_rows.to_dict(orient='records')
    return df_dict
file_name = 'start_quote'
screen = 'Quote'
section = 'Term'
#print(f"  {file_name=}, {screen=}, {section=}")
for item in csv_rows('start_quote', 'Quote', 'Term'):
    #print(f"  {item['screen']}, {item['section']}, {item['type']}, {item['sleep']}, {item['iteration']}, {item['field']}, {item['value']}")
    pass
#print("")
