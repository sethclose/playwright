from playwright.sync_api import Page
from datetime import datetime
import os
import log

def get_date_stamp() -> str:
    now = datetime.now()
    date_day = now.strftime("%d")
    date_mon = now.strftime("%b").upper()
    date_year = now.strftime("%Y")
    date_stamp = date_day + date_mon + date_year
    return date_stamp

def replace_chars(value: str) -> str:
    output = value
    remove_list = [" ", "-"]
    for char in remove_list:
        output = output.replace(char, "")
    return output

def take_screenshot(l: log.Log, page: Page, file_name: str):
    """
    Takes screenshot from playwright.sync_api
    :param l: Log file object to get config setting
    :param page: playwright page object
    :param file_name: name for .png file
    """
    name = file_name.replace("-", ""). replace(".", "").title().replace(" ", "")
    if l.screenshots:
        page.screenshot(path=f"./{l.output_path}/{l.test_name}_{get_date_stamp()}_{name}.png")