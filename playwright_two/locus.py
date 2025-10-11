#from time import perf_counter
#from openpyxl.pivot.table import Location
from playwright.sync_api import Page, Locator
#from datetime import datetime as dt
import pandas as pd
import time
import log
import tools
from tools import str_to_bool

def wait_for_page(l: log.Log, page: Page):
    l.s("Wait")

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

    spinner()
    load()
    elements()
    idle()

    l.e()

def act(l:log.Log, fields: pd.DataFrame, page: Page, action: pd.Series) -> pd.Series:
    l.s(f"Execute")

    # Start timer for action['time'] result
    start_time = time.perf_counter()

    # Skip if specified (override column)
    if action['override'] == 'skip':
        l.w(f"Skipping Action")

    # Execute Action (not skipped)
    else:

        # The Action
        print_row = "*"
        for key, value in action.items():
            if value != "":
                print_row += f" {key}:{value} *"
        l.w(f"{print_row}")

        # Wait
        wait_for_page(l, page) if str_to_bool(action['wait']) else None

        # Retrieve Enabled Element
        element = None
        element_enabled = False
        method = None
        element_condition = None

        # Because playwright locator.is_enabled() crashes
        def enabled(loc: Locator) -> bool:
            max_time = 1  # seconds
            try:
                loc.is_enabled(timeout=max_time*1000)
            except Exception as e:
                return False
            else:
                return True

        # FIND ELEMENT

        # First try Test Attribute and Value - these are explicit user overrides
        if action["attribute"] != "":
            l.w(f"Trying Test Attribute and Value")
            if action["attribute"] == "id":
                element_condition = f"#{action["name"]}"
            else:
                element_condition = f"[{action["attribute"]}='{action["name"]}']"
            element = page.locator(element_condition).nth((action["iteration"]-1))
            l.w(f"{element_condition=}")
            element_enabled = enabled(element)
            l.w(f"  {element.get_attribute(action["attribute"])=} {element.get_attribute("id")=} {element.get_attribute("dc-data-name")=}")
            l.w(f"  {element.get_attribute(action["name"])=} {element.get_attribute("title")=} {element.get_attribute("actionref")=}")
            l.w(f"Element {element_condition} enabled?  {element_enabled}")
            if element_enabled:
                method = element_condition + f".nth={action['iteration']-1}"
        else:
            l.w(f"No Test Attribute Specified")

        # Try Field Reference Element Conditions - main method when not overridden
        if not element_enabled:
            l.w(f"Field Reference Element Conditions")

            # Find Unique Field Reference
            fields_subset = fields[(fields['screen'] == action['screen']) & (fields['prompt'] == action['name'])]
            field = None
            if len(fields_subset) >= 1:
                l.w(f"Found Unique Field Reference(s)")
                field = fields_subset.iloc[0]
            elif len(fields_subset) == 0:
                l.w(f"  No Matching Field References")
            else: # There should be only one row, so we just take the first above [0]
                  # action["iteration"] is only to determine which element to take among those the field ref returned
                l.w(f"  Multiple Matching Field References")
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
                    if row_count == action["iteration"]:
                        l.w(f"    Field:  {attribute_1_display}  {attribute_2_display}")
                        field = f
                        break

            if field is not None:
                l.w(f"Trying field reference element conditions")
                element_conditions = []
                if field["attribute_1"] == "id" and field["value_1"] != "":
                    element_conditions.append(f"[#{field["value_1"]}]")
                if field["attribute_1"] != "id":
                    element_conditions.append(f"[{field["attribute_1"]}='{field["value_1"]}']")
                if field["attribute_2"] != "":
                    element_conditions.append(f"[{field["attribute_2"]}='{field["value_2"]}']")
                for element_condition in element_conditions:
                    element = page.locator(element_condition).nth(action["iteration"]-1)
                    element_enabled = enabled(element)
                    l.w(f"Element {element_condition} enabled?  {element_enabled}")
                    if element_enabled:
                        method = element_condition + f".nth={action['iteration']-1}"
                        break
            else:
                l.w(f"Did not find a unique Field Reference")

        # Try by various methods to use Name - flat out dangerous
        if not element_enabled and 1==0:
            l.w(f"Name Element Conditions")
            element_conditions = [  f"text={action["name"]}",
                                    f"[name='{action["name"]}']",
                                    f"[title='{action["name"]}']",
                                    f"[label='{action["name"]}']",   ]
            for element_condition in element_conditions:
                element = page.locator(element_condition)
                element_enabled = enabled(element)
                l.w(f"Element {element_condition} enabled?  {element_enabled}")
                if element_enabled:
                    method = element_condition
                    break

        # Try Test Name and Value by Role - in case no field ref exists:  diff the output xls
        if not element_enabled:
            l.w(f"Name and Value by Role Element Conditions")
            element_condition = f"['{action['type']}', name='{action['name']})'])"

            #elements = page.get_by_role(action['type'], name=action['name']).all()
            #l.w(f"Element Conditions:  {element_condition}")
            #l.w(f"Found {len(elements)} Elements")
            #for i, element in enumerate(elements):
            #    l.w(f"[{i}]  {element.get_attribute("id")=} {element.get_attribute("title")=} {element.get_attribute("actionref")=}")

            if 1==1:
                element = page.get_by_role(action['type'], name=action['name']).nth(action['iteration']-1)
                element_enabled = enabled(element)
                l.w(f"Element {element_condition} enabled?  {element_enabled}")
                if element_enabled:
                    method = element_condition + f".nth={action['iteration']-1}"

        # PROCESS ELEMENT

        # Was Element Found?
        if not element_enabled:
            l.w(f"Did Not Find Element")
        else:
            l.w(f"Element found by {method}")
            action['element'] = method

            # Process Element

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
                action["previous"] = element.input_value()
                if not action["check"]: # Not just checking on the value
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
                action["result"] = element.input_value()

            # RADIO
            if action['type'] == 'radio':
                l.w("Radio Button")
                action["previous"] = element.is_checked()
                if not action["check"]:
                    # Updating Value, not just checking value
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
                            l.w(f"Element enabled:  CLICKING")
                            element.click()
                            page.keyboard.press("Tab")
                        else:
                            l.w(f"Something went terribly wrong.")
                action["result"] = element.is_checked()

            # CHECKBOX
            if action['type'] == 'checkbox':
                action["previous"] = element.is_checked()
                if action['check']:
                    # Just checking the value
                    action['result'] = element.is_checked()
                else:
                    # Checking the box
                    check_box = tools.str_to_bool(action['value'])
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
                    action["result"] = element.is_checked()


        # Update result Time
        action['time'] = round(time.perf_counter() - start_time, 3)

        # Sleep
        if action['sleep'] > 0:
            l.w(f"Sleeping {action['sleep']} second(s)")
            time.sleep(action['sleep'])

    l.e()
    return action