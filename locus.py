from playwright.sync_api import Page, Locator
import time

def get_locators_all(page: Page, locator_types: list, search_types: list, locator_name: str) -> list:
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

def get_locator_object(page: Page, locator_type: str, locator_name: str, iteration: int=1) -> Locator:
    print(f"      START get_locator_object '{locator_type}' '{locator_name}' #{iteration}")

    # Look for locator directly by label
    locators = page.get_by_label(locator_name).all()
    print(f"        Found {len(locators)} locators for {locator_name} by label.")
    for index, loc in enumerate(locators):
        print(f"            Found locator: '{evaluate_locator(loc)}")
        if index+1 == iteration:
            print(f"            Setting Locator to '{locator_type}' '{locator_name}' directly by Label.")
            print(f"      END get_locator_object '{locator_type}' '{locator_name}' #{iteration}")
            return loc

    # Look for locator directly by text
    locators = page.get_by_text(locator_name).all()
    print(f"        Found {len(locators)} locators for {locator_name} by text.")
    for index, loc in enumerate(locators):
        print(f"            Found locator: '{evaluate_locator(loc)}")
        if index+1 == iteration:
            print(f"          Setting Locator to '{locator_type}' '{locator_name}' directly by Text.")
            print(f"      END get_locator_object '{locator_type}' '{locator_name}' #{iteration}")
            return loc

    search_types = []
    if locator_type == 'textbox':
        search_types = ['role']
    elif locator_type == "button":
        search_types = ['loc']
    elif locator_type == "a":
        search_types = ['text', 'loc', 'input']
    elif locator_type == "radio":
        search_types = ['input', 'text', 'role', 'loc']
    elif locator_type == "checkbox":
        search_types = ['role', 'loc']
    else:
        print(f"        Unhandled locator_type: {locator_type}.")
    locators = get_locators_all(page, [locator_type], search_types, locator_name)

    found_locator = None
    n = 0
    print(f"        Looking for:  {locator_name=} {locator_type=} {iteration=}")
    for loc in locators:
        if False:
            print(f"          PRE:  {evaluate_locator(loc)}")
            print(f"            ==> {loc}")
            print(f"                TEXTS {get_locator_text(loc)}")
            print(f"             CONTENTS {get_locator_content(loc)}")
            print(f"                   ID {loc.get_attribute("id")}")
            print(f"                FIELD {loc.get_attribute('fieldref')}")
            print(f"                CLASS {loc.get_attribute('class')}")
            print(f"                TITLE {loc.get_attribute('title')}")
        if locator_name in [loc.get_attribute("id"),
                            loc.get_attribute('fieldref'),
                            loc.all_inner_texts()[0],
                            loc.all_text_contents()[0]]:
            n += 1
            print(f"        Match:  {evaluate_locator(loc)}")
            if n == iteration: # or found_locator is None:
                print(f"          Setting Locator to '{locator_type}' {evaluate_locator(loc)}")
                found_locator = loc
        if found_locator is not None:
            break

    print(f"      END get_locator_object '{locator_type}' '{locator_name}' #{iteration}")
    return found_locator

def do_locator(page: Page, locator_type: str, locator_name: str, iteration: int=1,
               locator_value: str = 'CLICK', sleep_time: int=0,
               do_clear: bool=True, do_tab: bool=True) -> Locator:
    print(f"    START do_locator '{locator_type}' {locator_name} {locator_value} #{iteration}")
    loc = get_locator_object(page, locator_type, locator_name, iteration)
    if loc is not None:
        if locator_value == "CLICK":
            print(f"      Clicking on {evaluate_locator(loc)}")
            loc.click()
        elif locator_value == "CHECK":
            print(f"      Checking {evaluate_locator(loc)}")
            loc.check()
        elif locator_type == "radio":
            print(f"      Checking {evaluate_locator(loc)}")
            loc.check()
        else:
            print(f"      Typing {locator_value} into {evaluate_locator(loc)}")
            loc.clear() if do_clear else None
            loc.type(locator_value)
        time.sleep(sleep_time)
        if do_tab:
            print(f"      Tabbing from {evaluate_locator(loc)}")
            page.keyboard.press("Tab")
            time.sleep(sleep_time)
        return loc
    else:
        print(f'      Could not find locator:  Ignoring {locator_type} {locator_name}')
    print(f"    END do_locator '{locator_type}' {locator_name} {locator_value} #{iteration}")
    return []

def do_locator_radio(page: Page, locator_type: str, locator_name: str, iteration: int=1, sleep_time: int=0,) -> Locator:

    loc = get_locator_object(page, locator_type, locator_name, iteration=1)
    print(f"clicking loc")
    loc.click()
    print(f"tabbing")
    page.keyboard.press("Tab")

    choice_count = 1
    while choice_count < iteration:
        choice_count += 1
        print(f"clicking arrow up")
        page.keyboard.press("ArrowUp")

    print(f"hitting space")
    page.keyboard.press("Space")

    time.sleep(sleep_time)

    return loc

def evaluate_locator(loc: Locator) -> str:
    loc_id = "id=" + loc.get_attribute('id') + " " if loc.get_attribute('id') is not None else ""
    loc_field = "field=" + loc.get_attribute('fieldref')+ " "  if loc.get_attribute('fieldref') is not None else ""
    loc_text = "text=" + loc.all_inner_texts()[0]+ " "  if loc.all_inner_texts()[0] is not None else ""
    loc_nth = "nth=" + get_locator_nth_value(loc)+ " "  if get_locator_nth_value(loc) is not None else ""
    loc_total = loc_id + loc_field + loc_text + loc_nth
    loc_total = loc_total.replace('\r', '').replace('\n', '').strip()
    return loc_total

def get_locator_nth_value(loc: Locator) -> str:
    nth_index = str(loc).find("nth=")
    nth_value = str(loc)[nth_index + 4:nth_index + 6]
    nth_value = nth_value.replace("'", "")
    return nth_value

def get_locator_text(loc: Locator) -> str:
    texts = "TEXTS: "
    for text in loc.all_inner_texts():
        texts += " " + text
    return texts

def get_locator_content(loc: Locator) -> str:
    contents = "CONTENTS: "
    for content in loc.all_inner_texts():
        contents += " " + content
    return contents