from playwright.sync_api import Page
import os
import time
import locus

DEV21_URL = os.environ.get('DEV21_URL')
AGENT_USER = os.environ.get('AGENT_USER')
AGENT_PASS = os.environ.get('AGENT_PASS')

def start_page(browser, trace_mode: bool):
    context = browser.new_context(viewport=None)
    if trace_mode:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = browser.new_page()
    return page, context

def stop_page(browser, context, trace_mode: bool):
    if trace_mode:
        context.tracing.stop(path="pytest/trace.zip")
    context.close()
    browser.close()

def goto_brm(page: Page):
    page.goto(DEV21_URL)
    time.sleep(1)

def is_login(page: Page):
    page_title_correct = "Sign in"
    try:
        assert page.title() == page_title_correct
        print(f"    {page.title()} page found.")
    except AssertionError:
        print(f"    '{page.title()}' did not match expected: '{page_title_correct}'.")
        return False
    return True

def log_in(page: Page, sleep_time: int=0):
    page.locator("#signInName").fill(AGENT_USER)
    page.locator("#password").fill(AGENT_PASS)
    page.locator("#next").click()  # Sign in
    time.sleep(sleep_time)

def log_out(page: Page):
    page.locator("#action_0").click() # => top right
    time.sleep(6)

def start_new_quote(page: Page):
    locus.do_locator(page, 'button', 'New Quote', value="CLICK", sleep_time=1)

def start_notifications(page: Page):
    locus.do_locator(page, 'a', 'Notifications', value="CLICK", sleep_time=1)

def all_locators(page: Page):
    locators = locus.search_locators(page, locator_types=['button', 'textbox', 'a'])

def all_locators_old(page: Page):
    print('         Found locators:')
    locus.search_locators_old(page, 'a', "loc")
    locus.search_locators_old(page, 'button', "loc")
    #locus.search_locators_old(page, 'button', "role") # This works, too
    locus.search_locators_old(page, 'textbox', "role")

def start_quote(page: Page):

    locus.do_locator(page, 'button', 'New Quote', value="CLICK", sleep_time=1)

    locus.do_locator(page, 'textbox', 'NewQuoteInput.AgencyID', value="Advance Insurance - Lehi", sleep_time=0)
    locus.do_locator(page, 'textbox', 'NewQuoteInput.Producer', value="Alfredo Torres", sleep_time=0)
    locus.do_locator(page, 'textbox', 'NewQuoteInput.ProductSelect', value="Home HO3", sleep_time=2)
    locus.do_locator(page, 'textbox', 'PolicyInput.EffectiveDate', value="09/19/2025", sleep_time=1)

    locus.do_locator(page, 'textbox', 'PartySearchInput.FirstName', value="Roxan", sleep_time=1)
    locus.do_locator(page, 'textbox', 'PartySearchInput.MiddleName', value="TEST", sleep_time=1)
    locus.do_locator(page, 'textbox', 'PartySearchInput.Lastname', value="Begg", sleep_time=1)
    locus.do_locator(page, 'textbox', 'PartySearchInput.BirthDate', value="08/09/1986", sleep_time=1)
    locus.do_locator(page, 'textbox', 'PartySearchInput.PhoneNumber', value="8015551212", sleep_time=1)
    locus.do_locator(page, 'textbox', 'PartySearchInput.LocationAddressLine1', value="2371 W 2300 N", sleep_time=1)
    locus.do_locator(page, 'textbox', 'PartySearchInput.LocationPostalCode', value="84015", sleep_time=1)

    locus.do_locator(page, 'button', 'Search', nth=2, value="CLICK", sleep_time=1)
    locus.do_locator(page, 'button', 'Start Full Quote', value="CLICK", sleep_time=1)