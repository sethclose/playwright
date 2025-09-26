from playwright.sync_api import Page, Locator
import time
from datetime import datetime as dt
import log.logging as log

def get_loc(l: log.Log, page: Page, locator_type: str, locator_name: str, iteration: int=1):
    """
    Finds the locator of the element specified
    :param l: passed log file object
    :param page: playwright page object
    :param locator_type: type of element being done
    :param locator_name: name of element being done
    :param iteration: number of element if multiples
    :return: playwright locator object that was found
    """
    l.s("FIND")
    locators = page.get_by_text(locator_name).all()
    l.w(f"Found {len(locators)} locators for {locator_name} by Text.")
    for index, loc in enumerate(locators):
        #l.w(f"  Found locator #{index}: {evaluate_locator(loc)}")
        #l.w(f"  Looking for iteration: {iteration} (type={type(iteration)}) = {index + 1} (type={type(index)})?")
        if index + 1 == iteration:
            l.w(f"  Selected Locator '{locator_type}' '{locator_name}' #{iteration}.")
            l.e()
            return loc
    l.e()
    return None

def do_loc(l: log.Log, page: Page, locator_type: str, locator_name: str, iteration: int=1,
           value: str="", sleep: float=0):
    """
    Executes the action on the locator element specified by `locator_name`.
    :param l: passed log file object
    :param page: playwright page object
    :param locator_type: type of element being done
    :param locator_name: name of element being done
    :param iteration: number of element if multiples
    :param value: value of element to be entered
    :param sleep: seconds to wait after doing
    :return: locator: playwright locator object
    """
    l.s("DO")
    not_ready = True
    not_found = True
    wait_start = dt.now()
    max_wait = 10
    while not_ready and not_found:
        l.on = False # Don't log these attempts.
        loc = get_loc(l=l, page=page, locator_type=locator_type, locator_name=locator_name, iteration=iteration)
        l.on = True
        seconds = (dt.now() - wait_start).seconds + (dt.now() - wait_start).microseconds / 1000000
        if loc is not None:
            not_ready = False
            l.w(f"Found element in {seconds:.3f} seconds.")
        elif seconds > max_wait:
            not_found = False
            l.w(f"Timed Out looking for element in {seconds:.1f} seconds.")
    loc = get_loc(l=l, page=page, locator_type=locator_type, locator_name=locator_name, iteration=iteration)
    if loc is None:
        l.w(f"Locator Not Found")
    else:
        if locator_type == 'button':
            l.w(f"Click: '{evaluate_locator(loc)}'")
            loc.click()
        elif locator_type == 'radio':
            l.w(f"Check: '{evaluate_locator(loc)}'")
            loc.check()
        elif locator_type == 'checkbox':
            l.w(f"Check: '{evaluate_locator(loc)}'")
            loc.check()
        elif locator_type == 'textbox':

            # Only enter if value is to change.  May need several attempts.
            current_value = loc.input_value()
            test_value = str(value)
            if current_value != test_value:
                attempts = 0
                while current_value != test_value:
                    attempts += 1
                    l.w(f"{locator_name}:  '{current_value}' != '{test_value}'")
                    if current_value != '':
                        l.w(f"Clear: '{current_value}'")
                        loc.clear()

                    # DCT textboxes as dropdowns are finicky
                    l.on = False
                    loc_select = get_loc(l=l, page=page, locator_type='select', locator_name=test_value)
                    l.on = True
                    if loc_select is not None:
                        l.w(f"Press: '{test_value}'")
                        loc.press_sequentially(test_value)  # types in one key at a time
                        time.sleep(1/2)
                    else:
                        l.w(f"Type: '{test_value}'")
                        loc.type(test_value) # 'type' as in type on a keyboard

                    # Tab out
                    l.w(f"Press:  Tab")
                    page.keyboard.press("Tab")

                    # If there was trouble entering this value, sleep a second...
                    current_value = loc.input_value()
                    l.w(f"Current value: '{current_value}'")
                    if attempts > 1:
                        l.w(f"Repeated attempt (#{attempts-1}):  Pausing...")
                        time.sleep(1/2)

                l.w(f"Succeeded entry in only {attempts} attempt(s).")
            else:
                l.w(f"'{current_value}' already set to '{test_value}'")
        time.sleep(sleep)
    l.e()
    return loc

def evaluate_locator(loc: Locator) -> str:
    """
    Logging tool for gathering information about locator element
    :param loc: playwright locator object of element
    :return: string of locator data to be logged
    """
    loc_id = "id=" + loc.get_attribute('id') + " " if loc.get_attribute('id') is not None else ""
    loc_field = "field=" + loc.get_attribute('fieldref')+ " "  if loc.get_attribute('fieldref') is not None else ""
    loc_text = "text=" + loc.all_inner_texts()[0]+ " "  if loc.all_inner_texts()[0] is not None else ""
    loc_nth = "nth=" + get_locator_nth_value(loc)+ " "  if get_locator_nth_value(loc) is not None else ""
    loc_total = loc_id + loc_field + loc_text + loc_nth
    loc_total = loc_total.replace('\r', '').replace('\n', '').strip()
    return loc_total

def get_locator_nth_value(loc: Locator) -> str:
    """
    Retrieves the nth value of a locator element (debugging tool)
    :param loc: playwright locator object
    :return: value of attribute "nth"
    """
    nth_index = str(loc).find("nth=")
    nth_value = str(loc)[nth_index + 4:nth_index + 6]
    nth_value = nth_value.replace("'", "")
    return nth_value

def get_locators_all(page: Page, locator_types: list, search_types: list, locator_name: str) -> list:
    """
    Finds any and all locators on the page (debugging tool)
    :param page: playwright page object
    :param locator_types: types of locators being sought
    :param search_types: types of search to perform
    :param locator_name: descriptor of sought locator
    :return:
    """
    locators = []
    for locator_type in locator_types:
        print(f'      LOOKING for {locator_type}')
        for search_type in search_types:
            print(f'      SEARCHING by {search_type}')
            if 'loc' == search_type:
                pre_count = len(locators)
                temp_locators = page.locator(locator_type).all()
                locators += temp_locators
                locators = list(set(locators))
                add_count = len(locators) - pre_count
                print(f'        Added {add_count} locators for {locator_type} via loc method')
            if 'role' == search_type:
                pre_count = len(locators)
                temp_locators = page.get_by_role(locator_type).all()
                locators += temp_locators
                locators = list(set(locators))
                add_count = len(locators) - pre_count
                print(f'        Added {add_count} locators for {locator_type} via role method')
            if 'text' == search_type:
                pre_count = len(locators)
                temp_locators = page.get_by_text(locator_name).all()
                locators += temp_locators
                locators = list(set(locators))
                add_count = len(locators) - pre_count
                print(f'        Added {add_count} locators for {locator_type} via text method')
            if 'label' == search_type:
                pre_count = len(locators)
                temp_locators = page.get_by_label(locator_name).all()
                print(f"        BY LABEL:  {temp_locators=}")
                locators += temp_locators
                locators = list(set(locators))
                add_count = len(locators) - pre_count
                print(f'        Added {add_count} locators for {locator_type} via label method')
            if 'input' == search_type:
                pre_count = len(locators)
                locator_list = page.locator(f'input[type="{locator_type}"]')
                temp_locators = [locator_list.nth(i) for i in range(locator_list.count())]
                locators += temp_locators
                locators = list(set(locators))
                add_count = len(locators) - pre_count
                print(f'        Added {add_count} locators for {locator_type} via input method')
    locators = list(set(locators))
    print(f'        Total {len(locators)} locators for {locator_types}')
    locators = sorted(locators, key=lambda loc_key: (loc_key.get_attribute('id') is None, loc_key.get_attribute('id'),
                                                     loc_key.get_attribute('fieldref') is None, loc_key.get_attribute('fieldref'),
                                                     #loc_key.all_inner_texts()[0] is None, loc_key.all_inner_texts()[0],
                                                     get_locator_nth_value(loc_key) is None, get_locator_nth_value(loc_key)))
    return locators
