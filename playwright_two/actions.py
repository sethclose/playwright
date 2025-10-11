from playwright.sync_api import Page, Locator, expect
from datetime import datetime as dt
import pandas as pd
import time
import log
import config
import tools

def wait_for_page(l: log.Log, page: Page):
    l.s("Wait")

    def spinner():
        # Make Sure Spinner is Gone
        before = time.perf_counter()
        page.locator("#loading-spinner").wait_for(state="hidden")
        time_waited = time.perf_counter() - before
        if time_waited > 1:
            l.w(f"Waited {time_waited:.1f} seconds spinner to stop.")

    def load():
        # Make sure Page is Not Loading
        before = time.perf_counter()
        load_count = 0
        while page.title().find("Loading") != -1:
            load_count += 1
            if load_count == 0:
                l.w(f"Waiting for while page is '{page.title()}'.")
        time_waited = time.perf_counter() - before
        if time_waited > 1:
            l.w(f"Waited {time_waited:.1f} seconds for page to load.")

    def elements():
        # Make Sure all Elements are Loaded
        loaded = False
        wait_seconds = (1/9)
        locators = []
        num = 0
        before = time.perf_counter()
        while not loaded:
            #l.w(f"Waiting for all elements to load.  Current total is {num}.")
            locators += page.get_by_role('textbox').all()
            locators += page.get_by_role('button').all()
            locators += page.get_by_role('radio').all()
            locators = list(set(locators))
            if len(locators) >= num != 0:
                loaded = True
            num = len(locators)
            time.sleep(wait_seconds)
        time_waited = time.perf_counter() - before
        if time_waited > 1:
            l.w(f"Waited {time_waited:.1f} for {num} element(s) to load.")

    def idle():
        # Wait for Network Idle
        before = time.perf_counter()
        page.wait_for_load_state("networkidle")
        time_waited = time.perf_counter() - before
        if time_waited > 1:
            l.w(f"Waited {time_waited:.1f} seconds for network idle.")

    load()
    elements()
    spinner()
    idle()

    l.e()

def get(l: log.Log, c: config.Config, page: Page, locator_type: str, locator_name: str, iteration: int=1):
    """
    Finds the locator of the element specified
    :param l: passed log file object
    :param c: configuration object with platform information
    :param page: playwright page object
    :param locator_type: type of element being done
    :param locator_name: name of element being done
    :param iteration: number of element if multiples
    :return: playwright locator object that was found
    """
    l.s(f"Get Element:  {locator_type}:{locator_name} ({iteration})")
    l.w(f"  Platform: {c.platform}")
    found_by = ""

    # Radio Buttons
    if locator_type == 'radio':
        l.w(f"Getting Radio button choice(s)")
        locators = page.locator(f'input[type="{locator_type}"]').all()
        for loc in locators:
            l.w(f"Locator:  {evaluate_locator(loc)}")
            if locator_name.lower() in loc.get_attribute('fieldref').lower():
                l.w(f"  Locator:  {evaluate_locator(loc)} contains '{locator_name}'")
        locators = [loc for loc in locators if locator_name.lower() in loc.get_attribute('fieldref').lower()]

    # Wildcard Link - Evaluation of disappearing links causes errors in other section
    elif locator_type in ['link', 'a', 'button'] and locator_name == 'ANY':
        l.w("Getting all links by role")
        locators = page.get_by_role('link').all()
        l.w(f"Found {len(locators)} locators.  Looking for iteration #{iteration}.")
        for index, loc in enumerate(locators):
            if loc.is_visible():
                #loc.hover()
                #title = loc.get_attribute("title")
                #l.w(f"hovering over {title} (#{index + 1})")
                #time.sleep(1)
                if index + 1 == iteration:
                    l.w(f"  Selected Locator '{locator_type}' '{locator_name}' #{iteration}.")
                    l.e()
                    found_by = "Wildcard Link Search"
                    return loc

    # Regular Search
    else:
        l.w(f"Getting non-Radio {locator_type} by text")
        locators = page.get_by_text(locator_name).all()
        found_by = "Text"
        l.w(f"'{locator_type}'(s) by {found_by}: {len(locators)}")
        if len(locators) == 1:
            l.w(f"  Found 1 Locator: {locators[0]=}")

        # Special Case for Buttons with Containers (like icons) because FU.DCT
        if len(locators) == 0 and locator_type == 'button':
            l.w(f"\n  Could not find the button.  Check for container.")

            if locator_type == 'button': # and locator_name not in ['Sign In']: # in ['Search', 'Edit']:
                l.w(f"\n  3 Check if {locator_name} button is in container.")
                loc = page.locator(f"dc-action[data-dc-name={locator_name}]")
                if loc is not None:
                    l.w(f"    Got dc-action: {loc}")
                    url = tools.get_url_from_string(str(loc))
                    l.w(f"         URL: {url}")
                    if url.find('onmicrosoft.com') != -1: # This is for sign-on and is okay.
                        # Do not look for an action ref here as it will take a literal minute.
                        l.w(f"Using found onmicrosoft button for actions like sign-in.")
                    else:
                        l.w(f"    Getting Action Reference button because there is were no locators found.")
                        locators = [page.locator(f"button[actionref='{locator_name}']")]
                        l.w(f"      Got: {len(locators)} {loc=}")
                        if url.find('aspx') != -1:  # This is FU.DCT
                            l.w(f"      Ignoring .aspx button")
                            locators = []
                        else:
                            l.w(f"      Found contained button")
                            found_by = "Action Ref"

    l.w(f"Found {len(locators)} locators for {locator_name} by {found_by}.")
    for loc in locators:
        l.w(f"  Locator:  {evaluate_locator(loc)}")
    for index, loc in enumerate(locators):
        l.w(f"    Locator #{index}: {evaluate_locator(loc)}")
        l.w(f"    Looking for iteration: {iteration} (type={type(iteration)}) = {index+1} (type={type(index)})?")
        if index + 1 == iteration:
            l.w(f"    => Selected Locator '{locator_type}' '{locator_name}' #{iteration}.")
            l.e()
            return loc
    l.e()
    return None

def act(l:log.Log, c: config.Config, page: Page, action: pd.Series) -> pd.Series:
    l.s("Action")
    l.w(f"[*]{[f"{i}={a}" for i, a in action.items()]}[*]")

    def override() -> bool:
        return True if pd.notna(action['override']) else False
    def wait() -> bool:
        return True if action['wait'] == 1.0 else False

    # Wait if specified (wait column)
    if wait():
        wait_for_page(l, page)

    # Skip if specified (override column)
    if action['override'] == 'skip':
        l.w(f"Override:  Skip")
    else:
        l.w(f"Execute (No Override)")

        # Get Iteration and Sleep Quantities
        iteration, exception = tools.get_num_value(action['iteration'], int, 1)
        l.w(f"Iteration:  {iteration}  {exception}")
        sleep_time, exception = tools.get_num_value(action['sleep'], int, 0)
        l.w(f"Sleep:  {sleep_time}  {exception}")

        # Allow for manual tab, ugh
        if action['name'] == 'TAB':
            if action['type'] == 'button':
                l.w(f"  Tabbing {iteration} times")
                for i in range(iteration):
                    #l.w(f"    Hitting [Tab]")
                    page.keyboard.press("Tab")
                    #time.sleep(0.05)
                l.w(f"    => Hitting [Enter]")
                page.keyboard.press("Enter")
                return action

        else:

            # Retrieve Locator, when/if available
            l.w(f"Retrieve Locator, when/if available")
            not_ready = True
            not_found = True
            time_start = dt.now()   # Start timing
            max_wait = 10           # Max seconds to try
            ready_count = 0
            loc = get(l=l, c=c, page=page, locator_type=str(action['type']), locator_name=str(action['name']), iteration=int(iteration))
            while not_ready and not_found:
                ready_count += 1
                prev_log_mode = l.mode
                l.mode = "off"
                loc = get(l=l, c=c, page=page, locator_type=str(action['type']), locator_name=str(action['name']), iteration=int(iteration))
                l.mode = prev_log_mode   # okay, start logging again
                seconds = (dt.now()-time_start).seconds + (dt.now()-time_start).microseconds / 1_000_0000
                if loc is not None:
                    not_ready = False
                    l.w(f"Found element in {seconds:.3f} seconds.")
                elif seconds > max_wait:
                    not_found = False
                    l.w(f"Timed Out ({max_wait}) looking for element in {seconds:.1f} seconds.")

            if loc is None:
                l.w(f"Locator Not Found")
                if action['name'] == 'edit' and False:
                    l.w(f"Have Edit locator {loc} from normal process")
                    # edit_button = page.locator(f"dc-action[data-dc-name='{action['name'].lower()}'] button[actionref='{action['name']}']")
                    # edit_button = page.locator('dc-action[data-dc-name="delete"] button[actionref="Delete"]')
                    # if edit_button is not None:
                    #    l.w(f"clicking edit_button")
                    #    edit_button.click()
                    l.w(f"Trying something {'else'}")
                    container = page.locator('dc-action[data-dc-name="edit"]')
                    l.w(f"Got container {container}")
                    expect(container).to_be_attached()
                    l.w(f"Container {container.is_visible()=} {container.is_enabled()=}")
                    edit_button = container.get_by_role("button")#, name="edit")#, exact=True)
                    l.w(f"Edit Button in Container {edit_button.is_visible()=} {edit_button.is_enabled()=}")
                    edit_button.scroll_into_view_if_needed()
                    l.w(f"Edit scrolled into view")
                    # expect(edit_button).to_be_visible(timeout=7000)
                    # expect(edit_button).to_be_enabled()
                    edit_button.click()

            else:
                l.w(f"Locator Was Found")

                # Just override if hover, check, etc
                if override():
                    if action['override'] == 'hover':
                        l.w(f"Overriding with {action['override']}")
                        loc.hover()
                    if action['override'] == 'check':
                        l.w(f"Overriding with {action['override']}")
                        action['result'] = loc.input_value()

                # Execute Action if not override or if debugging action
                if not override() or action['override'] == 'debug':
                    l.w("Executing action")

                    if action['type'] == 'button':
                        l.w(f"Click Button: '{evaluate_locator(loc)}'")
                        loc.click()

                    elif action['type'] == 'a' or action['type'] == 'link':
                        l.w(f"Click Link: '{evaluate_locator(loc)}'")
                        loc.click()

                    elif action['type'] == 'radio':
                        l.w(f"Click Radio: {evaluate_locator(loc)}'")
                        loc.click()
                        l.w(f"Press: 'Tab'")
                        page.keyboard.press("Tab")
                        l.w(f"Iteration: '{iteration}'")
                        choice_count = 1
                        while choice_count < iteration:
                            choice_count += 1
                            l.w(f"Press: 'ArrowUp'")
                            page.keyboard.press("ArrowUp")
                        l.w(f"Press: 'Space'")
                        page.keyboard.press("Space")

                    elif action['type'] == 'checkbox':
                        l.w(f"Check: '{evaluate_locator(loc)}'")
                        loc.check()

                    elif action['type'] == 'textbox':
                        l.w(f"Enter: '{evaluate_locator(loc)}'")

                        # Only enter if value is to change.  May need several attempts.
                        current_value = loc.input_value()
                        test_value = str(action['value'])
                        if current_value != test_value:
                            attempts = 0
                            while current_value != test_value:
                                attempts += 1
                                l.w(f"{action['name']}:  '{current_value}' != '{test_value}'")
                                if current_value != '':
                                    l.w(f"Clear: '{current_value}'")
                                    loc.clear()

                                # DCT textboxes as dropdowns are finicky
                                prev_log_mode = l.mode
                                l.mode = "off"
                                loc_select = get(l=l, c=c, page=page, locator_type='select', locator_name=test_value)
                                l.mode = prev_log_mode
                                if loc_select is not None:
                                    l.w(f"Press keys: '{test_value}'")
                                    loc.press_sequentially(test_value)  # types in one key at a time
                                    time.sleep(1/2)
                                else:
                                    l.w(f"Type: '{test_value}'")
                                    loc.type(test_value) # 'type' as in type on a keyboard
                                loc.press("Tab")

                                # If there was trouble entering this value, nap
                                current_value = loc.input_value()
                                l.w(f"Current value: '{current_value}'")
                                if attempts > 1:
                                    l.w(f"Repeated attempt (#{attempts-1}):  Pausing...")
                                    time.sleep(1/2)

                            l.w(f"Succeeded entry in only {attempts} attempt(s).")
                        else:
                            l.w(f"'{current_value}' already set to '{test_value}'")
                        action['result'] = current_value

                l.w(f"Sleeping for {sleep_time} seconds...") if sleep_time > 0 else None
                time.sleep(sleep_time)

        action['time'] = l.section_seconds()

        if action['result'] != '':
            l.w(f"Result:  {action['result']}")
        else:
            l.w(f"No result returned")
    l.e()
    return action

def evaluate_locator(loc: Locator) -> str:
    """
    Logging tool for gathering information about locator element
    :param loc: playwright locator object of element
    :return: string of locator data to be logged
    """
    try:
        loc_id = "id=" + loc.get_attribute('id') + " " if loc.get_attribute('id') is not None else ""
    except Exception as e:
        return f"INVALID ID: {e}"
    try:
        loc_field = "field=" + loc.get_attribute('fieldref')+ " "  if loc.get_attribute('fieldref') is not None else ""
    except IndexError:
        loc_field = ""
    try:
        loc_text = "text=" + loc.all_inner_texts()[0]+ " "  if loc.all_inner_texts()[0] is not None else ""
    except IndexError:
        loc_text = ""
    loc_nth = "nth=" + get_locator_nth_value(loc)+ " "  if get_locator_nth_value(loc) is not None else ""
    loc_desc = loc_id + loc_field + loc_text + loc_nth
    loc_desc = loc_desc.replace('\r', '').replace('\n', '').strip()
    return loc_desc

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


# These are sometimes used tools

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
    print(f"        Found {len(locators)} locators of {locator_name} by Label.")
    for index, loc in enumerate(locators):
        print(f"            Found locator: '{evaluate_locator(loc)}")
        if index+1 == iteration:
            print(f"            Setting Locator to '{locator_type}' '{locator_name}' directly by Label.")
            print(f"      END get_locator_object '{locator_type}' '{locator_name}' #{iteration}")
            #return loc

    # Look for locator directly by text
    locators = page.get_by_text(locator_name).all()
    print(f"        Found {len(locators)} locators for {locator_name} by Text.")
    for index, loc in enumerate(locators):
        print(f"            Found locator: '{evaluate_locator(loc)}")
        if index+1 == iteration:
            print(f"          Setting Locator to '{locator_type}' '{locator_name}' directly by Text.")
            print(f"      END get_locator_object '{locator_type}' '{locator_name}' #{iteration}")
            #return loc

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
    for loco in locators:
        print(f"LOCATOR:   {evaluate_locator(loco)}")

    found_locator = None
    n = 0
    print(f"        Looking for:  {locator_name=} {locator_type=} {iteration=}")
    for loc in locators:
        print(f"          PRE:  {evaluate_locator(loc)}")
        print(f"            ==> {loc}")
        #print(f"                TEXTS {get_locator_text(loc)}")
        #print(f"             CONTENTS {get_locator_content(loc)}")
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