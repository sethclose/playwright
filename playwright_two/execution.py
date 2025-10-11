from time import perf_counter

from openpyxl.pivot.table import Location
from playwright.sync_api import Page, Locator, expect
from datetime import datetime as dt
import pandas as pd
import time
import re
import actions
import log
import config
import tools
from tools import str_to_bool

def wait_for_page(l: log.Log, page: Page):
    l.s("Wait")

    def spinner():
        # Make Sure Spinner is Gone
        before = time.perf_counter()
        page.locator("#loading-spinner").wait_for(state="hidden")
        time_waited = time.perf_counter() - before
        if time_waited > 1:
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
        if time_waited > 1:
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
        if time_waited > 1:
            l.w(f"Waited {time_waited:.1f} seconds for page to load.")

    def idle():
        # Wait for Network Idle
        before = time.perf_counter()
        page.wait_for_load_state("networkidle")
        time_waited = time.perf_counter() - before
        if time_waited > 1:
            l.w(f"Waited {time_waited:.1f} seconds for network idle.")

    spinner()
    load()
    elements()
    idle()

    l.e()

def act(l:log.Log, c: config.Config, fields: pd.DataFrame, page: Page, action: pd.Series) -> pd.Series:
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
            print_row += f" {key}:{value} *"
        l.w(f"{print_row}")

        # Wait
        wait_for_page(l, page) if str_to_bool(action['wait']) else None

        # Find Action Type and Super Type (like "xact") if exists
        dot_index = action['type'].find(".")
        if dot_index != -1:
            super_type = action['type'][:dot_index]
            action_type = action['type'][dot_index + 1:]
            display_type = f"{action_type} ({super_type})"
        else:
            super_type = ""
            action_type = action['type']
            display_type = action_type
        l.w(f"Action Type:  {display_type}")

        # Process by Type
        if super_type in ("", "LU", "MG"):
            if action_type in ['textbox', 'button', 'link', 'radio', 'checkbox']:

                # TEXT
                # NEED TO CHECK VALUE FIRST
                # NEED TO STORE RESULT (STORE PRE-VALUE, TOO?)
                # NULL VALUE ENTRY
                if action_type == 'textbox':

                    locators = page.get_by_role(action_type, name=action['name']).all()
                    for i, loc in enumerate(locators):
                        if (i+1) == action['iteration']:
                            count = 0
                            entered = False
                            while not entered and loc.input_value() != action['value']:
                                count += 1
                                if loc.input_value() != action['value']:
                                    if loc.input_value() != "":
                                        l.w(f"Clearing Value:  '{loc.input_value()}'")
                                        loc.clear()
                                    if count == 1:
                                        l.w(f"Entering Text: {action['value']}")
                                    else:
                                        l.w(f"Re-entering Text: {action['value']}")
                                    loc.press_sequentially(action['value'])
                                    l.w(f"Value is set to: {loc.input_value()}")
                                    if loc.input_value() == action['value']:
                                        entered = True
                                    page.keyboard.press("Tab")
                            if not entered:
                                l.w(f"Element {action['name']} already set to correct value.")

                # BUTTON
                elif action_type == 'button':

                    if action['attribute'] == "" and action['iteration'] == 1:
                        l.w(f"Clicking Button:  {action['name']}")
                        page.get_by_role(action_type, name=action['name']).click()

                    # Attribute Specified - This is not button specific, but used for processSearch
                    # CAREFUL:  THIS IS ALSO AN ITERATION
                    # CAN I INCORPORATE A SEARCH FOR NAME?
                    elif action['attribute'] != "":

                        l.w(f'Looking for {(action_type)} where {action["attribute"]}={action["name"]}')
                        l.w(f"{len(page.get_by_role(action_type).all())=}")
                        n = 0
                        l.w(f"  Matching:  {action['attribute']} to Action name: {action["name"]}")
                        for loc in page.get_by_role(action_type).all():
                            l.w(f"    Locator Attribute value: {loc.get_attribute(action['attribute'])}")
                            if loc.get_attribute(action['attribute']) is not None:
                                if action["name"] in loc.get_attribute(action['attribute']):
                                    l.w(f"      Matched Attribute, Seeking Iteration #{action['iteration']}")
                                    l.w(f"        Match #{n+1}")
                                    if (n + 1) == action['iteration']:
                                        l.w(f"          Clicking")
                                        loc.click()
                                        break
                                    n += 1

                    # Iteration Specified
                    elif action['iteration'] > 1:
                        l.w(f"Looking for the #{action['iteration']} {action['name']} {action_type}")
                        locs = page.get_by_role("button").all() # THIS DOES NOT GET BY NAME
                        l.w(f"  Found {len(locs)} {action['name']} {action_type} locator(s)")
                        l.w(f"  Clicking #{action['iteration']}")
                        page.get_by_role(action_type).nth(action['iteration']-1).click()

                # LINK
                elif action_type == 'link':
                    l.w(f"Clicking Link: {action['name']}")
                    page.get_by_role(action_type, name=action['name']).click()

                # RADIO
                # NEED TO CHECK VALUE FIRST
                # NEED TO STORE RESULT
                # NULL VALUE
                elif action_type == 'radio':
                    l.w(f"Clicking '{action_type}' "
                        f"with name containing '{action['name']}' "
                        f"and value '{1 if 'Y' in action['value'].upper() else 0}' for '{action['value']}'")
                    page.locator(f"input[type='radio'][fieldref*='{action['name']}'][value='{1 if 'Y' in action['value'].upper() else 0}']").click()

                # CHECKBOX
                # NEED TO CHECK VALUE FIRST
                # NEED TO STORE RESULT
                # NULL VALUE
                elif action_type == 'checkbox':
                    l.w(f"Checking {action['name']} Box")
                    page.get_by_role(action["type"], name=action['name']).check()
                    #page.get_by_label(f"{action['name']}").check()
                    #page.get_by_role(action["type"]).and_(page.get_by_label(action["name"])).check()

        if super_type == 'LU': # Look Up
        # Get the Actual ID to look it up.

            l.w(f"Look Up:")
            # Find Unique Field Reference
            fields_subset = fields[(fields['screen']==action['screen']) & (fields['prompt']==action['name'])]
            if len(fields_subset) != 1:
                if len(fields_subset) == 0:
                    l.w(f"  No Matching Field References")
                else:
                    l.w(f"  Multiple Matching Field References")
                    row_count = 0
                    for i, field in fields_subset.iterrows():
                        row_count += 1
                        print_row = ""
                        for key, value in field.items():
                            print_row += f" {key}:{value} *"
                        l.w(f"  Field Reference:  [{i}] {print_row}")
                        attribute_1_display = f"{field['attribute_1']}={field['value_1']}"
                        attribute_2_display = f"{field['attribute_2']}={field['value_2']}" if field['attribute_2'] != "" else ""
                        l.w(f"  Element:  {attribute_1_display}  {attribute_2_display}")
            else:
                # Unique Field Reference
                row_count = 0
                for i, field in fields_subset.iterrows():
                    row_count += 1
                    print_row = ""
                    for key, value in field.items():
                        print_row += f" {key}:{value} *"
                    #l.w(f"  Field Reference:  [{i}] {print_row}")
                    #attribute_1_display = f"{field['attribute_1']}={field['value_1']}"
                    #attribute_2_display = f"{field['attribute_2']}={field['value_2']}" if field['attribute_2'] != "" else ""
                    #l.w(f"  Field Reference Attributes:  {attribute_1_display}  {attribute_2_display}")

                    # Retrieve Enabled Element
                    element = None
                    element_enabled = False
                    method = None

                    # Because playwright locator.is_enabled() crashes
                    def enabled(x_loc: Locator) -> bool:
                        max_time = 1  # seconds
                        try:
                            element.is_enabled(timeout=max_time*1000)
                        except Exception as e:
                            #l.w(f"    Fail:  Element Timed Out ({max_time} s)")
                            return False
                        else:
                            #l.w(f"    Success:  Element Enabled")
                            return True

                    # Various Locator() condition parameters
                    element_conditions = [  f"#xx{field["value_1"]}",
                                            #f"[{field["attribute_1"]}='{field["value_1"]}']",
                                            f"[{field["attribute_2"]}='{field["value_2"]}']",
                                            f"[{action["attribute"]}='{action["name"]}']",
                                            f"text={action["name"]}",
                                            f"[name='{action["name"]}']",
                                            f"[title='{action["name"]}']",
                                            f"[label='{action["name"]}']",  ]

                    # Find  Processing Method
                    for element_condition in element_conditions:
                        element = page.locator(element_condition)
                        element_enabled = enabled(element)
                        l.w(f"  {element_condition}?  {element_enabled}")
                        if element_enabled:
                            method = element_condition
                            break

                    if element_enabled == False:
                        element = page.get_by_role(action_type, name=action['name']).nth(action['iteration']-1)
                        element_enabled = enabled(element)
                        element_condition = f"  get_by_role({action_type}, name={action['name']}).nth({action['iteration']-1})?"
                        l.w(f"  {element_condition}?  {element_enabled}")
                        if element_enabled:
                            method = element_condition

                            page.get_by_role(action_type, name=action['name'])

                    # By ID (field reference)
                    if field["attribute_1"] == "xxxid":
                        element_condition = f"#{field["value_1"]}"
                        l.w(f"  Finding element by id: '{element_condition}'")
                        element = page.locator(element_condition)
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By Attribute (field reference)
                    if element_enabled == False and field["attribute_1"] == "xxxxid":
                        element_condition = f"{field["attribute_1"]}='{field["value_1"]}'"
                        l.w(f"  Finding element by attribute_1: [{element_condition}]")
                        element = page.locator(f"[{element_condition}]")
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By Alternate Attribute (field reference)
                    if element_enabled == False and field["attribute_2"] != "":
                        element_condition = f"{field["attribute_2"]}='{field["value_2"]}'"
                        l.w(f"  Finding element by attribute_2: [{element_condition}]")
                        element = page.locator(f"[{element_condition}]")
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By Test Attribute
                    if element_enabled == False and action["attribute"] != "":
                        element_condition = f"{action["attribute"]}='{action["name"]}'"
                        l.w(f"  Finding element by test attribute condition: [{element_condition}]")
                        element = page.locator(f"[{element_condition}]").nth(action["iteration"]-1)
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By Test Name as text
                    #   "text=Click me"
                    if element_enabled == False:
                        element_condition = f"text='{action["name"]}'"
                        l.w(f"  Finding element by test text condition: [{element_condition}]")
                        element = page.locator(f"[{element_condition}]").nth(action["iteration"]-1)
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By Test Name as name
                    if element_enabled == False:
                        element_condition = f"name='{action["name"]}'"
                        l.w(f"  Finding element by test name condition: [{element_condition}]")
                        element = page.locator(f"[{element_condition}]").nth(action["iteration"]-1)
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By Test Name as title
                    if element_enabled == False:
                        element_condition = f"title='{action["name"]}'"
                        l.w(f"  Finding element by test title condition: [{element_condition}]")
                        element = page.locator(f"[{element_condition}]").nth(action["iteration"]-1)
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By Test Name as label
                    if element_enabled == False:
                        element_condition = f"label='{action["name"]}'"
                        l.w(f"  Finding element by test label condition: [{element_condition}]")
                        element = page.locator(f"[{element_condition}]").nth(action["iteration"]-1)
                        element_enabled = enabled(element)
                        if element_enabled:
                            method = element_condition

                    # By...?
                    if element_enabled == False:
                        l.w(f"  Still looking...")
                    else:
                        l.w(f"  Element found by {method}")




                        # Process Element
                        if action_type == "textbox":
                            element_value = element.input_value()
                            l.w(f"    Element Value: {element_value}")
                            if element_value == action['value']:
                                l.w(f"      Element Value matches New Value")
                            else:
                                l.w(f"      ?Updating Element")




        if super_type == 'XACT':
            # MAYBE CUE BY SHEET NAME?
            # LOOK, YOU NEED A SCREEN COLUMN,
            # NOT THIS JANKY SUPER TYPE SHIT.
        # XactWare 360 Value (Dwelling Information):

            # Field Data
            if action_type != 'element': # "element" is a testing cue to get the current context

                l.w(f"Looking for attribute matching prompt = '{action['name']}' #{action['iteration']}")

                # ALSO MATCH f[f['screen'] == 'xact'] and change screen to 360Value or something
                attributes = fields[fields['prompt'] == action['name']]['attribute']

                #l.w(f"Found {len(attributes)}")
                if len(attributes) > (action['iteration']-1):
                    attribute_name = fields[fields['prompt'] == action['name']]['attribute'].iloc[(action['iteration'] - 1)]
                else:
                    l.w(f"Did not find prompt #{action['iteration']-1} named '{action['name']}', Defaulting to 'id'.")
                    attribute_name = "id"
                l.w(f"  Attribute name:  {attribute_name}")

                l.w(f"Looking for attribute matching prompt = '{action['name']}' #{action['iteration']}")
                values = attribute_value = fields[fields['prompt'] == action['name']]['value']
                if len(values) > (action['iteration']-1):
                    attribute_value = fields[fields['prompt'] == action['name']]['value'].iloc[(action['iteration'] - 1)]
                else:
                    l.w(f"Did not find prompt #{action['iteration']-1} named '{action['name']}', Defaulting to '{action['name']}'.")
                    attribute_value = action['name']
                l.w(f"  Attribute value: {attribute_value}")

            # Buttons (Continue, etc)
            if action_type == "button":

                l.w(f"Looking for element {attribute_name} equal to {attribute_value}")
                tab_max = 35
                tab_count = 0
                while True:
                    iframe_frame = page.query_selector("iframe[title='Xact Value']").content_frame()
                    xact_element = iframe_frame.evaluate_handle("document.activeElement")
                    #l.w(f"  Element has {attribute_name} attribute value of:  {xact_element.get_attribute(attribute_name)}")
                    #l.w(f"  {xact_element}")
                    if xact_element.get_attribute(attribute_name) == attribute_value:
                        #l.w(f"    [{tab_count}] {xact_element.get_attribute(attribute_name)=}")
                        l.w(f"Pressing {action['name']}")
                        page.keyboard.press(key='Enter')
                        break
                    else:
                        page.keyboard.press(key='Tab')
                        tab_count += 1
                        time.sleep(0.1)
                    if tab_count > tab_max:
                        l.w(f"Could not find {action['name']}")
                        break

            elif action_type == "textbox":
            # Input Boxes (Number of Stories, et cetera

                l.w(f"Looking for element {attribute_name} equal to {attribute_value}")
                tab_max = 25
                tab_count = 0
                while True:
                    iframe_frame = page.query_selector("iframe[title='Xact Value']").content_frame()
                    xact_element = iframe_frame.evaluate_handle("document.activeElement")
                    #l.w(f"  Element has {attribute_name} attribute value of:  {xact_element.get_attribute(attribute_name)}")
                    #l.w(f"  {xact_element}")
                    if xact_element.get_attribute(attribute_name) == attribute_value:
                        #l.w(f"    [{tab_count}] {xact_element.get_attribute(action['attribute'])=}")
                        page.keyboard.type(action['value'])
                        page.keyboard.press(key='ArrowDown')
                        page.keyboard.press(key='Enter')
                        page.keyboard.press(key='Tab')
                        break
                    else:
                        page.keyboard.press(key='Tab')
                        tab_count += 1
                        time.sleep(0.1)
                    if tab_count > tab_max:
                        l.w(f"Hit maximum number of tabs:  {tab_max}")
                        break

            elif action_type == "element":
            # Print information about the current element on page
                active_element_handle = page.evaluate_handle("document.activeElement")
                iframe_handle = page.query_selector("iframe[title='Xact Value']")
                iframe_frame = iframe_handle.content_frame()
                active_element_in_iframe_handle = iframe_frame.evaluate_handle("document.activeElement")
                tag_name = active_element_in_iframe_handle.evaluate("element => element.tagName")
                l.w(f"Current Element: "
                    f"{active_element_handle.evaluate('e => e.tagName')} {tag_name} "
                    f"{active_element_in_iframe_handle.get_attribute("id")}")

        if super_type == 'MG': # Match Game

            # The Match Game
            l.w(f"{action_type} {action['name']} {(action['attribute'])} {action['iteration']}")
            locators = page.get_by_role(action_type).all()
            l.w(f"  # Locators?  {len(locators)}")
            query_match_count = 0
            complete_match_count = 0
            match_index = None
            for i, loc in enumerate(locators):
                query_value = action['name'].lower()
                id_value = loc.get_attribute('id').lower() if loc.get_attribute('id') is not None else ""
                name_value = loc.get_attribute('name').lower() if loc.get_attribute('name') is not None else ""
                title_value = loc.get_attribute('title').lower() if loc.get_attribute('title') is not None else ""
                content_value = loc.all_text_contents()[0].lower() if loc.all_text_contents()[0] is not None else ""
                text_value = loc.all_inner_texts()[0].lower() if loc.all_inner_texts()[0] is not None else ""
                att_value = loc.get_attribute(action['attribute']).lower() if loc.get_attribute(
                    action['attribute']) is not None else ""
                query_id_match = (query_value in id_value)
                query_name_match = (query_value in name_value)
                query_title_match = (query_value in title_value)
                query_text_match = (query_value in text_value)
                query_content_match = (query_value in content_value)
                query_att_match = (query_value in att_value)
                if query_id_match or query_name_match or query_title_match or query_text_match or query_content_match or query_att_match:
                    query_match_count += 1
                    if query_match_count == action['iteration']:
                        complete_match_count += 1
                        match_index = i
                l.w(f"  {i=} {query_id_match} {query_name_match} {query_title_match} {query_text_match} {query_content_match} {query_att_match}")
            l.w(f"  Matches:  {complete_match_count}/{query_match_count}", "")
            if complete_match_count == 0:
                l.w(f"MG:  Found no matches.")
            elif complete_match_count > 1:
                l.w(f"MG:  Multiple matches ({complete_match_count})")
            else:
                l.w(f"MG:  Singular match at {match_index}")

        # Capture Result
        action['time'] = round(time.perf_counter() - start_time, 3)

        # Sleep
        if action['sleep'] > 0:
            l.w(f"Sleeping {action['sleep']} second(s)")
            time.sleep(action['sleep'])

    l.e()
    return action