from playwright.sync_api import Page
from datetime import datetime
import pandas as pd
import log

def get_date_stamp() -> str:
    now = datetime.now()
    date_day = now.strftime("%d")
    date_mon = now.strftime("%b").upper()
    date_year = now.strftime("%Y")
    date_stamp = date_day + date_mon + date_year
    return date_stamp

def take_screenshot(l: log.Log, page: Page, file_name: str):
    name = file_name.replace("/", " ").replace(".", " ").title().replace("  ", " ")
    if l.screenshots:
        l.screenshot_count += 1
        page.screenshot(path=f"./{l.output_path}/screenshots/{l.screenshot_count} {name}.png")

def str_to_list(value: str) -> list:
    return [v.strip() for v in value.split(',')]

def str_to_int_list(value: str) -> list:
    if pd.isna(value) or pd.isnull(value):
        return []
    elif type(value) == int:
        return [value]
    else:
        return [int(v.strip()) for v in value.split(',')]

def string_to_bool(value: str) -> bool:
    if pd.notna(value):
        if value in ("True", "TRUE", "true", 1.0, 1, True):
            return True
    return False

def get_num_value(value, type_code, default) -> tuple:
    error = ""
    try:
        output = type_code(value)
    except ValueError as e:
        output = default
        error = e.args[0]
    return output, error

def replace_chars(value: str) -> str:
    output = value
    remove_list = [" ", "-"]
    for char in remove_list:
        output = output.replace(char, "")
    return output


def get_url_from_string(text: str) -> str:
    start = text.find("http")
    if start == -1:
        return ""
    text = text[start:]
    end = text.find("'")
    if end == -1:
        return ""
    text = text[:end]
    return text
