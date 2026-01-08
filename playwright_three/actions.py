from time import perf_counter
from playwright.sync_api import Page, Locator
import pandas as pd
import time
import log
import tools

def wait_for_page(l: log.Log, page: Page, screen: str):
    l.s("Wait")

    def has_title():
        # Make Sure Page Title matches Screen name from Test
        ready = False
        total_wait = 12  # Seconds maximum
        time_waited = 0
        pause_time = 1/4
        start_time = perf_counter()
        while not ready:
            time_waited = perf_counter() - start_time
            try:
                page_title = page.title()
            except Exception as e:
                l.w(f"  page.title() exception:  {str(e)[:79]}")
            else:
                l.w(f"  {page_title=} {screen=}")
                if page_title == screen or screen == "":
                    if screen == "":
                        l.w(f"  {page_title}, but screen is not specified in test")
                    else:
                        l.w(f"  Page is ready: {page_title}")
                    ready = True
            finally:
                time.sleep(pause_time)
                if total_wait < perf_counter() - start_time:
                    break
        if time_waited > 0.1:
            l.w(f"Waited {time_waited:.1f} second(s) for page title to load.")
        return ready

    def spinner():
        # Make Sure Spinner is Gone
        before = time.perf_counter()
        page.locator("#loading-spinner").wait_for(state="hidden")
        time_waited = time.perf_counter() - before
        if time_waited > 0.1:
            l.w(f"Waited {time_waited:.1f} seconds spinner to stop.")

    def elements():
        # Make Sure all Elements are Loaded
        loaded = False
        wait_seconds = (1/4)
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
        if time_waited > 0.1:
            l.w(f"Waited {time_waited:.1f} for {num} element(s) to load.")

    def load():
        # Make sure Page is Not Loading
        before = time.perf_counter()
        load_count = 0
        while page.title().find("Loading") != -1:
            load_count += 1
            if load_count == 0:
                l.w(f"Waiting for while page is '{page.title()}'.")
        time_waited = time.perf_counter() - before
        if time_waited > 0.1:
            l.w(f"Waited {time_waited:.1f} seconds for page to load.")

    def idle():
        # Wait for Network Idle
        before = time.perf_counter()
        page.wait_for_load_state("networkidle")
        time_waited = time.perf_counter() - before
        if time_waited > 0.1:
            l.w(f"Waited {time_waited:.1f} seconds for network idle.")

    if has_title():
        spinner()
        load()
        elements()
        idle()

    l.e()

def act(l:log.Log, fields: pd.DataFrame, page: Page, action: pd.Series) -> pd.Series:
    l.s(f"Act")

    # Start timer for action['time'] result
    start_time = time.perf_counter()

    # Skip if specified
    if action['skip']:
        l.w(f"Skipping Action")

    # Execute Action (not skipped)
    else:

        # Test Step Action (print row)
        print_row = "*"
        for key, value in action.items():
            if value != "":
                print_row += f" {key}:{value} *"
        l.w(f"{print_row}")

        # Wait if specified in Test
        wait_for_page(l, page, action['screen']) if action['wait'] else None

        # Screenshot Before
        if action['pics'] in ('before', 'both'):
            name = action['screen'] + '_' if action['screen'] != "" else ""
            name += action['name'] + '_' + 'before'
            tools.take_screenshot(l, page, name)

        # Find element to act upon, unless mere key stroke
        if action['type'] != "key":

            # Initialize Enabled Element variables
            element = None
            element_enabled = False
            method = None
            element_condition = None

            # Because playwright locator.is_enabled() crashes
            def enabled(loc: Locator) -> bool:
                max_time = 1  # seconds
                try:
                    loc.is_enabled(timeout=max_time*1000)
                except Exception as ex:
                    l.w(f"    exception:  {str(ex)[:80]}") if False else ""
                    return False
                else:
                    return True

            # Credit Card?
            cc_fields = ('Enter card number', 'Month', 'Year', 'Security Code', 'Submit Payment')
            is_cc = action['screen'] == "Issue Policy" and action['name'] in cc_fields
            is_not_cc = not is_cc
            if is_cc:
                l.w(f"This is a Credit Card field and must be handled differently.")

            # XactWare 360?
            is_360 = action['screen'] == "Replacement Cost" and action['name'] != "Return To Policy"
            is_not_360 = not is_360
            if is_360:
                l.w(f"This is an XactWare field and must be handled differently.")

            # FIND ELEMENT to act upon

            # First try Test Attribute and Value - these are explicit user overrides
            if action['attribute'] != "" and is_not_360 and is_not_cc:
                l.w(f"Trying Test Attribute and Value")
                if action['attribute'] == "id":
                    element_condition = f"#{action['name']}"
                else:
                    element_condition = f"[{action['attribute']}='{action['name']}']"
                element = page.locator(element_condition).nth((action['iteration']-1))
                l.w(f"{element_condition=}")
                element_enabled = enabled(element)
                l.w(f"  {element.get_attribute(action['attribute'])=} {element.get_attribute("id")=} "
                    f"  {element.get_attribute("title")=} {element.get_attribute(action['name'])=} ")
                l.w(f"Element {element_condition} enabled?  {element_enabled}")
                if element_enabled:
                    method = element_condition + f".nth={action['iteration']-1}"
            else:
                l.w(f"No Test Attribute Specified")

            # Try Field Reference Lookup Condition - main method when not overridden
            field = None
            if not element_enabled:
                l.w(f"Field Reference Lookup")

                # Find Unique Field Reference
                fields_subset = fields[(fields['screen'] == action['screen']) & (fields['prompt'] == action['name'])]
                if len(fields_subset) >= 1:
                    l.w(f"Found Unique Field Reference(s)")
                    field = fields_subset.iloc[0]
                elif len(fields_subset) == 0:
                    l.w(f"No Matching Field References")
                else: # There should be only one row, so we just take the first above [0]
                      # action['iteration'] is only to determine which element to take among those the field ref returned
                    l.w(f"Multiple Matching Field References")
                    row_count = 0
                    for i, f in fields_subset.iterrows():
                        row_count += 1
                        print_row = ""
                        for key, value in f.items():
                            print_row += f" {key}:{value} *"
                        l.w(f"  Field Reference:  [{i}] {print_row}")
                        attribute_1_display = f"{f['attribute_1']}={f['value_1']}"
                        attribute_2_display = f"{f['attribute_2']}={f['value_2']}" if f['attribute_2'] != "" else ""
                        l.w(f"  Field:  {attribute_1_display}  {attribute_2_display}")
                        if row_count == action['iteration']:
                            l.w(f"    Field:  {attribute_1_display}  {attribute_2_display}")
                            field = f
                            break

                # Found Field Reference
                if field is not None:

                    if is_not_360 and is_not_cc:
                        l.w(f"Trying field reference element conditions")
                        element_conditions = []
                        if field['attribute_1'] == "id" and field['value_1'] != "":
                            #element_conditions.append(f"[#{field['value_1']}]")
                            element_conditions.append(f"#{field['value_1']}")
                        if field['attribute_1'] != "id":
                            element_conditions.append(f"[{field['attribute_1']}='{field['value_1']}']")
                        if field['attribute_2'] != "":
                            element_conditions.append(f"[{field['attribute_2']}='{field['value_2']}']")
                        for element_condition in element_conditions:
                            element = page.locator(element_condition).nth(action['iteration']-1)
                            element_enabled = enabled(element)
                            l.w(f"Element {element_condition} enabled?  {element_enabled}")
                            if element_enabled:
                                method = element_condition + f".nth={action['iteration']-1}"
                                break
                    elif is_360 or is_cc:
                        l.w(f"Found field reference to process Xact 360 or Credit Card field")

                else:
                    l.w(f"Did not find a unique Field Reference")

            # Try Test Name and Value by Role - in case no field ref exists:  diff the output xlsx
            if not element_enabled and is_not_360 and is_not_cc:
                l.w(f"Name and Value by Role Element Conditions")
                element_condition = f"['{action['type']}', name='{action['name']})'])"
                element = page.get_by_role(action['type'], name=action['name']).nth(action['iteration']-1)
                element_enabled = enabled(element)
                l.w(f"Element {element_condition} enabled?  {element_enabled}")
                if element_enabled:
                    method = element_condition + f".nth={action['iteration']-1}"

            # PROCESS ELEMENT

            # Was Element Found?
            if element_enabled:

                l.w(f"Element found by {method}")
                action['element'] = method

                # BUTTON
                if action['type'] == 'button':
                    l.w("Clicking Button")
                    element.click()

                # LINK
                if action['type'] == 'link':
                    l.w("Clicking Link")
                    element.click()

                # TEXTBOX
                if action['type'] == "textbox":
                    l.w(f"Textbox initial value: {element.input_value()}")
                    action['previous'] = element.input_value()
                    if not action['eval']: # Not just checking on the value
                        entered = False
                        while not entered and element.input_value() != action['value']:
                            if element.input_value() != "" and action['value'] != "":
                                l.w(f"Clearing Value:  '{element.input_value()}'")
                                element.clear()
                            element.press_sequentially(action['value'])
                            l.w(f"Value is set to: {element.input_value()}")
                            if element.input_value() == action['value']:
                                entered = True
                                page.keyboard.press("Tab")
                        if not entered:
                            l.w(f"Element {action['name']} already set to correct value.")
                    action['result'] = element.input_value()

                # RADIO
                if action['type'] == 'radio':
                    l.w("Radio Button")
                    action['previous'] = element.is_checked()
                    if not action['eval']:
                        # Updating Value, not just checking value
                        if element.is_checked():
                            l.w(f"Element is already checked.")
                        else:
                            while not element.is_checked():
                                l.w("Checking Radio Button")
                                element_enabled = enabled(element)
                                if not element_enabled:
                                    l.w("  Element is now disabled.")
                                    if method is not None:
                                        l.w(f"  Method is not None:  {method}, Re-Locating by {element_condition}")
                                        if method.find("get_by_role") == -1:
                                            element = page.locator(element_condition)
                                        else:
                                            element = page.get_by_role(action['type'], name=action['name']).nth(action['iteration']-1)
                                        element_enabled = enabled(element)
                                        l.w(f"Element {element_condition} enabled?  {element_enabled}")
                                    else:
                                        l.w(f"No locator method found.")
                                if element_enabled:
                                    l.w(f"Element enabled:  Checking")
                                    element.check()
                                    page.keyboard.press("Tab")
                                else:
                                    l.w(f"Something went terribly wrong.")

                    action['result'] = element.is_checked()

                # CHECKBOX
                if action['type'] == 'checkbox':
                    action['previous'] = element.is_checked()
                    if action['eval']:
                        # Just checking the value
                        action['result'] = element.is_checked()
                    else:
                        # Checking the box
                        check_box = tools.string_to_bool(action['value'])
                        if check_box:
                            # Make sure box is checked
                            if element.is_checked():
                                l.w("Box already checked")
                            else:
                                l.w("Checking box")
                                while not element.is_checked():
                                    element.check()
                        else:
                            # Uncheck Box
                            if not element.is_checked():
                                l.w("Box already unchecked")
                            else:
                                l.w("Unchecking box")
                                while element.is_checked():
                                    element.uncheck()
                        page.keyboard.press("Tab")
                        l.w(f"Box checked? {element.is_checked()}")
                        action['result'] = element.is_checked()

            elif is_360 or is_cc:

                # For Credit Card, we need to start by navigating to the first field.
                if action['name'] == 'Enter card number':
                    l.w("Setting up Credit Card entry")
                    for i in range(2):
                        page.keyboard.press("Tab")
                    for i in range(6):
                        page.keyboard.press("Shift+Tab")

                # Field to Find
                l.w(f"Looking for element {field['attribute_1']} equal to {field['value_1']}")
                tab_count = 0
                tab_max = 35 if is_360 else 5
                success = False
                while True:
                    try:
                        if is_cc:
                            iframe_frame = page.query_selector("iframe[title='undefined']").content_frame()
                        else:
                            iframe_frame = page.query_selector("iframe[title='Xact Value']").content_frame()
                    except Exception as e:
                        l.w(f"Failed to get iframe:  {str(e)[:79]}")
                        break
                    else:
                        l.w("Getting JavaScript Handle")
                        xact_handle = iframe_frame.evaluate_handle("document.activeElement")
                        if not xact_handle.as_element():
                            l.w("Element Handle does not represent an element.")
                            break
                        else:
                            #l.w("Got Element from JavaScript Handle.")
                            element = xact_handle.as_element()
                            if element.get_attribute(field['attribute_1']) == field['value_1']:
                                l.w(f"Found {field['attribute_1']} = "
                                    f"{element.get_attribute(field['attribute_1'])} "
                                    f"at element #{tab_count}")
                                success = True
                                break
                            else:
                                #l.w(f"    Tabbing {tab_count}")
                                tab_key = 'Tab' if is_not_360 or action['name'] != 'Continue' else 'Shift+Tab'
                                page.keyboard.press(key=tab_key)
                                tab_count += 1
                                time.sleep(0.1)
                            if tab_count > tab_max:
                                l.w(f"  Could not find {action['name']}")
                                break

                # Search Complete:  did it work?
                l.w(f"Successfully found {action['type']} {action['name']}?  {success}")
                if success:

                    # Process Element
                    if is_360:
                        # Button
                        if action['type'] == "button":
                            l.w(f"Pressing Button [{action['name']}]")
                            page.keyboard.press(key='Enter')
                        # Text
                        if action['type'] == "textbox":
                            l.w(f"Choosing XactWare Option [{action['value']}]")
                            page.keyboard.type(action['value'])
                            page.keyboard.press(key='ArrowDown')
                            page.keyboard.press(key='Enter')
                            page.keyboard.press(key='Tab')

                    elif is_cc:
                        # Button
                        if action['type'] == "button":
                            l.w(f"Pressing Button [{action['name']}]")
                            page.keyboard.press(key='Enter')
                        # Text
                        if action['type'] == "textbox":
                            l.w(f"Entering Credit Card value [{action['value']}]")
                            page.keyboard.type(action['value'])

            else:
                l.w(f"Did Not Find Element")

        else:
            # Key Press Action, sadly needed
            l.w(f"Key Action:  {action['name']}")
            if action['name'] == 'Value':
                l.w(f"  Typing Value:  {action['value']}")
                page.keyboard.type(action['value'])
            else:
                l.w(f"  Pressing Key:  {action['name']}")
                page.keyboard.press(key=action['name'])

        # Update result Time
        action['time'] = round(time.perf_counter() - start_time, 3)

        # After Screenshot
        if action['pics'] in ('after', 'both'):
            name = action['screen'] + '_' if action['screen'] != "" else ""
            name += action['name'] + '_' + 'after'
            tools.take_screenshot(l, page, name)

        # Sleep
        if action['sleep'] > 0:
            l.w(f"Sleeping {action['sleep']} second(s)")
            time.sleep(action['sleep'])

    l.e()
    return action