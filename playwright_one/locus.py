from playwright.sync_api import Page, Locator
import time

def search_locators(page: Page, locator_types: list) -> list:
    print(f"    Finding {locator_types} locators")
    locators = []
    for locator_type in locator_types:
        locators = locators + page.locator(locator_type).all()
        locators = locators + page.get_by_role(locator_type).all()
        locators = locators + page.get_by_text(locator_type).all()
    #locators = list(set([loc for loc in locators if loc.get_attribute('id') is not None]))
    locators = [loc for loc in locators if loc.get_attribute('id') is not None]
    locators = [loc for loc in locators if loc.get_attribute('id')[-3:] != 'err']
    locator_ids = [loc.get_attribute('id') for loc in locators]
    locators = [loc for i, loc in enumerate(locators) if loc.get_attribute('id') not in locator_ids[:i]]
    locators.sort(key=lambda loc: loc.get_attribute('id'))
    for loc in locators:
        print(f"      {loc.get_attribute('id')}   field={loc.get_attribute('fieldref')}   text={loc.all_inner_texts()[0]}")
        #print(f"        => {loc}")
    return locators

def search_locators_old(page, locator_type: str = "button", search_type: str = "locator"):
    print(f"    Finding '{locator_type}' by {search_type}")
    locators = page.locator(locator_type).all() # a, button
    if search_type == "role":
        locators = page.get_by_role(locator_type).all()
    if search_type == "text":
        locators = page.get_by_text(locator_type).all()
    if search_type == "label":
        locators = page.get_by_label(locator_type).all()
    for i, loc in enumerate(locators):
        descriptors = []
        if loc.get_attribute('id') is not None:
            descriptors.append("id="+loc.get_attribute('id'))
        if loc.get_attribute('fieldref') is not None != "":
            descriptors.append("field="+loc.get_attribute('fieldref'))
        if loc.all_inner_texts()[0] is not None and loc.all_inner_texts()[0] != "":
            descriptors.append("text="+loc.all_inner_texts()[0])
        if loc.all_text_contents()[0] is not None and loc.all_text_contents()[0] != "":
            descriptors.append("content="+loc.all_text_contents()[0])
        if len(descriptors) > 0:
            if loc.get_attribute('id') is not None:
                print(f"      {locator_type} by {search_type} #{i}: {descriptors}")


def get_locator_object(page: Page, locator_type: str, locator_name: str, nth: int=1) -> Locator:
    print(f"    Finding {locator_type} {locator_name} #{nth}")
    if locator_type == "textbox":
        locators = page.get_by_role(locator_type).all()
        print(f"      Found {len(locators)} locator options by role method")
    else:
        locators = page.locator(locator_type).all()
        print(f"      Found {len(locators)} locator options by locator method")
    #page.get_by_text(), page.get_by_label() might be useful
    found_locator = None
    n = 0
    for loc in locators:
        if locator_name in [loc.get_attribute('fieldref'), loc.all_inner_texts()[0], loc.all_text_contents()[0]]:
            n += 1
            #print(f"        '{locator_name}' '{locator_type}' {nth=} {n=}:  id={loc.get_attribute("id")}")
            if n == nth:
                print(f"      Setting Locator to {loc.get_attribute("id")}")
                found_locator = loc
    return found_locator

def do_locator(page: Page, locator_type: str, locator_name: str, nth: int=1,
               value: str = 'CLICK', sleep_time: int=0,
               do_clear: bool=True, do_tab: bool=True) -> None:
    loc = get_locator_object(page, locator_type, locator_name, nth)
    if value == "CLICK":
        loc.click()
    else:
        loc.clear() if do_clear else None
        time.sleep(sleep_time)
        loc.type(value)
    time.sleep(sleep_time)
    page.keyboard.press("Tab") if do_tab else None




