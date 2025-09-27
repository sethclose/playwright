from playwright.sync_api import Page
from datetime import datetime
import timeit
import os
import log

def make_folder(folder_name:str):
    try:
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")
    except FileNotFoundError:
        print("Error: The path to the new folder does not exist.")

def get_date_stamp() -> str:
    now = datetime.now()
    date_day = now.strftime("%d")
    date_mon = now.strftime("%b").upper()
    date_year = now.strftime("%Y")
    date_stamp = date_day + date_mon + date_year
    return date_stamp

def take_ss(l: log.Log, page: Page, file_name: str):
    """
    Takes screenshot from playwright.sync_api
    :param l: Log file object to get config setting
    :param page: playwright page object
    :param file_name: name for .png file
    """
    if l.screenshots:
        page.screenshot(path=f"./{l.output_path}/{l.test_name}_{get_date_stamp()}_{file_name}.png")

def page_wait(l: log.Log, wait_page: Page):
    def await_elements(await_page: Page, element: str=None):
        not_ready = True
        old_num = 0
        count = 0
        while not_ready:
            count += 1
            if element is None:
                timeit.timeit(lambda: await_page.get_by_role('textbox').all(), number=100)
            else:
                timeit.timeit(lambda: await_page.get_by_text(element).all(), number=25)
            num = len(await_page.get_by_role('textbox').all())
            if num >= old_num != 0:
                not_ready = False
                l_i.w(f"Called {count*100} times for page to be ready ({num} elements).")
            else:
                old_num = num
    wait_time = timeit.timeit(lambda: await_elements(wait_page), number=1)
    l.w(f"Waited {wait_time:.1f} seconds for page to be ready.")

