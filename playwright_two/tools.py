from playwright.sync_api import Page
import log.logging as log
import timeit

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
                #l_i.w(f"Called {count*100} times for page to be ready ({num} elements).")
            else:
                old_num = num
    wait_time = timeit.timeit(lambda: await_elements(wait_page), number=1)
    l.w(f"Waited {wait_time:.1f} seconds for page to be ready.")

def take_ss(l: log.Log, page: Page, file_name: str):
    """
    Takes screenshot from playwright.sync_api
    :param l: Log file object to get config setting
    :param page: playwright page object
    :param file_name: name for .png file
    """
    if l.screenshots:
        page.screenshot(path=f"./log/screenshots/{file_name}.png")
