from playwright.sync_api import Page
from datetime import datetime
import log


def str_to_list(value: str) -> list:
    """
    convert string to boolean
    :param value: input comma-delimited string
    :return: output list
    """
    return [v.strip() for v in value.split(',')]

def str_to_int_list(value: str) -> list:
    """
    convert string to boolean
    :param value: input comma-delimited string of numbers
    :return: output list of numbers
    """
    return [int(v.strip()) for v in value.split(',')]


def str_to_bool(value: str) -> bool:
    """
    convert string to boolean
    :param value: string input
    :return: boolean output
    """
    if value in ("True", "TRUE", "true", 1.0, 1, True):
        return True
    else:
        return False


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


def get_date_stamp() -> str:
    now = datetime.now()
    date_day = now.strftime("%d")
    date_mon = now.strftime("%b").upper()
    date_year = now.strftime("%Y")
    date_stamp = date_day + date_mon + date_year
    return date_stamp


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


def take_screenshot(l: log.Log, page: Page, file_name: str):
    """
    Takes screenshot from playwright.sync_api
    :param l: Log file object to get config setting
    :param page: playwright page object
    :param file_name: name for .png file
    """
    name = file_name.replace("-", "").replace(".", "").title().replace(" ", "")
    if l.screenshots:
        page.screenshot(path=f"./{l.output_path}/{l.test_name}_{get_date_stamp()}_{name}.png")
