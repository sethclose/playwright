from idlelib.autocomplete import FORCE

from playwright.sync_api import Page
import os
import time
import locus
import data
from locus import evaluate_locator

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
        context.tracing.stop(path="trace.zip")
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
    locus.do_locator(page, 'button', 'New Quote', locator_value="CLICK", sleep_time=1)

def open_existing_quote(page: Page):
    locus.do_locator(page, 'a', 'My Home', locator_value="CLICK", sleep_time=1)
    locus.do_locator(page, 'a', 'Roxan Playwright Begg', locator_value="CLICK", sleep_time=1)
    locus.do_locator(page, 'a', 'H01411918Q', locator_value="CLICK", sleep_time=3)

def start_notifications(page: Page):
    locus.do_locator(page, 'a', 'Notifications', locator_value="CLICK", sleep_time=1)

def start_quote(page: Page):
    locus.do_locator(page, 'button', 'New Quote', locator_value="CLICK", sleep_time=1)

    locus.do_locator(page, 'textbox', 'Agency', locator_value=data.get_value('Agency'))
    locus.do_locator(page, 'textbox', 'Producer', locator_value=data.get_value('Producer'), sleep_time=1)
    locus.do_locator(page, 'textbox', 'Product', locator_value=data.get_value('Product'), sleep_time=2)
    locus.do_locator(page, 'textbox', 'Product', locator_value=data.get_value('Product'), sleep_time=5)
    locus.do_locator(page, 'textbox', 'Product', locator_value='Home HO3', sleep_time=2)
    locus.do_locator(page, 'textbox', 'EffectiveDate', locator_value=data.get_value('EffectiveDate'), sleep_time=1)
    locus.do_locator(page, 'textbox', 'First Name', locator_value=data.get_value('FirstName'))
    locus.do_locator(page, 'textbox', 'Middle Name', locator_value=data.get_value('MiddleName'))
    locus.do_locator(page, 'textbox', 'Last Name', locator_value=data.get_value('LastName'))
    locus.do_locator(page, 'textbox', 'Birth Date', locator_value=data.get_value('BirthDate'))
    locus.do_locator(page, 'textbox', 'Phone Number', locator_value=data.get_value('PhoneNumber'))
    locus.do_locator(page, 'textbox', 'Address1', locator_value=data.get_value('AddressLine1'))
    locus.do_locator(page, 'textbox', 'ZIP Code', locator_value=data.get_value('PostalCode'), sleep_time=1)

    locus.do_locator(page, 'button', 'Search', locator_value="CLICK",  iteration=2, sleep_time=3)

def start_quote_new_party(page: Page):
    locus.do_locator(page, 'button', 'Start Full Quote', locator_value="CLICK", sleep_time=3)

def new_quote_party(page: Page):
    locus.do_locator(page, 'textbox', 'AccountInput.FirstName', locator_value=data.get_value('FirstName'))
    locus.do_locator(page, 'textbox', 'AccountInput.MiddleName', locator_value=data.get_value('MiddleName'))
    locus.do_locator(page, 'textbox', 'AccountInput.LastName', locator_value=data.get_value('LastName'))
    locus.do_locator(page, 'textbox', 'AccountInput.Suffix', locator_value=data.get_value('Suffix'))
    locus.do_locator(page, 'textbox', 'AccountInput.BirthDate', locator_value=data.get_value('BirthDate'))

    locus.do_locator(page, 'textbox', 'AccountInput.Gender', locator_value=data.get_value('Gender'))
    locus.do_locator(page, 'textbox', 'AccountInput.MaritalStatus', locator_value=data.get_value('MaritalStatus'))
    locus.do_locator(page, 'textbox', 'AccountInput.Occupation', locator_value=data.get_value('Occupation'))
    locus.do_locator(page, 'textbox', 'AccountInput.SSN', locator_value=data.get_value('SSN'))

    locus.do_locator(page, 'textbox', 'AccountInput.PrimaryPhone', locator_value=data.get_value('PrimaryPhone'))
    locus.do_locator(page, 'textbox', 'AccountInput.SecondaryPhone', locator_value=data.get_value('SecondaryPhone'))
    locus.do_locator(page, 'textbox', 'AccountInput.SecondaryPhoneType', locator_value=data.get_value('SecondaryPhoneType'))
    locus.do_locator(page, 'textbox', 'AccountInput.Email', locator_value=data.get_value('Email'))
    locus.do_locator(page, 'textbox', 'AccountInput.CommunicationPreference', locator_value=data.get_value('CommunicationPreference'))
    locus.do_locator(page, 'textbox', 'AccountInput.DocumentDeliveryMethod', locator_value=data.get_value('DocumentDeliveryMethod'))

    locus.do_locator(page, 'textbox', 'AccountInput.Address1', locator_value=data.get_value('Address1'))
    locus.do_locator(page, 'textbox', 'AccountInput.Address2', locator_value=data.get_value('Address2'))
    locus.do_locator(page, 'textbox', 'AccountInput.City', locator_value=data.get_value('City'))
    locus.do_locator(page, 'textbox', 'AccountInput.State', locator_value=data.get_value('State'))
    locus.do_locator(page, 'textbox', 'AccountInput.ZipCode', locator_value=data.get_value('ZipCode'), sleep_time=1)

    locus.do_locator(page, 'button', 'Verify', locator_value="CLICK", sleep_time=5)
    locus.do_locator(page, 'button', 'Save', locator_value="CLICK", sleep_time=5)

def start_quote_old_party(page: Page):
    time.sleep(2)  # Links to search take a few seconds
    locus.do_locator(page, 'a', 'Start Full Quote', locator_value="CLICK", sleep_time=1)

def finish_named_insured(page: Page):
    locus.do_locator(page, 'button', 'Verify', locator_value="CLICK", sleep_time=1)
    time.sleep(3)
    locus.do_locator(page, 'radio', 'InsuranceScore_Events.PermissionToOrderScore', iteration=1, sleep_time=5)
    #locus.do_locator(page, 'button', 'Next', locator_value="CLICK", sleep_time=5)

def underwriting_questions(page: Page):
    print('    START underwriting_questions')
    locus.do_locator(page, 'a', 'Underwriting Questions', locator_value='CLICK', sleep_time=3)
    locus.do_locator(page, 'radio', 'CoverageDeclinedCanceledNonRenewedInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'ConvictedOfArsonOrFraudInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'HomeForSaleOrVacantInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'LapseInCoverageInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'HomeEverRentedInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'BusinessOrFarmInput.Value', iteration=2)
    locus.do_locator(page, 'textbox', 'NumberOfDogsInput.Value', locator_value="7", sleep_time=2)
    locus.do_locator(page, 'radio', 'ExoticAnimalsInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'PropertyDifficultToAccessInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'AdditionalNamesOnTitleInput.Value', iteration=2)
    locus.do_locator(page, 'radio', 'ApplicantResideAtPremisesInput.Value', iteration=1)
    locus.do_locator(page, 'radio', 'AdditionalFamiliesOrRoommatesInput.Value', iteration=2)

    page.screenshot(path="./log/screenshots/underwriting_questions.png")
    print('    END underwriting_questions')

def dwelling_information(page: Page):
    print('    START dwelling_information')
    locus.do_locator(page, 'a', 'Dwelling Information', locator_value='CLICK', do_clear=False, do_tab=False, sleep_time=3)

    locus.do_locator(page, 'textbox', 'Coverage A', locator_value="300000", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Dwelling Type', locator_value="Single Family/Twin", sleep_time=2)

    locus.do_locator(page, 'textbox', 'Usage', locator_value="Primary", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Construction', locator_value="Frame", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Roof Type', locator_value="Asphalt Shingles", sleep_time=1)

    locus.do_locator(page, 'textbox', 'Acreage', locator_value="1", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Trampoline', locator_value="None", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Pool', locator_value="None", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Central Alarm', locator_value="None", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Wood Stoves-Dwelling', locator_value="0")
    locus.do_locator(page, 'textbox', 'Wood Stoves-Other Structures', locator_value="0")

    locus.do_locator(page, 'radio', 'Solar Panels', iteration=2)
    locus.do_locator_radio(page, 'radio', 'Smokers in Home', iteration=2, sleep_time=1)
    locus.do_locator_radio(page, 'radio', 'Water Features', iteration=2, sleep_time=1)
    locus.do_locator_radio(page, 'radio', 'Existing Damage', iteration=2, sleep_time=1)
    locus.do_locator_radio(page, 'radio', 'Polybutylene Plumbing', iteration=2, sleep_time=1)

    page.screenshot(path="./log/screenshots/dwelling_information.png")
    locus.do_locator(page, 'button', 'Next', locator_value="CLICK", sleep_time=5)
    print('    START dwelling_information')

def rate_summary(page: Page):
    print('    START rate_summary')
    locus.do_locator(page, 'a', 'Rate Summary', locator_value='CLICK', do_clear=False, do_tab=False, sleep_time=3)

    locus.do_locator(page, 'textbox', 'Deductible', locator_value="$10,000", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Coverage E', locator_value="$300,000", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Coverage F', locator_value="$3,000", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Account', locator_value="New Account", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Collection Method', locator_value="Auto Pay", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Pay Plan', locator_value="Full Pay", sleep_time=2)

    locus.do_locator(page, 'a', 'Proceed To Application', locator_value='CLICK', do_clear=False, do_tab=False, sleep_time=10)

    page.screenshot(path="./log/screenshots/rate_summary.png")
    #locus.do_locator(page, 'button', 'Next', locator_value="CLICK", sleep_time=5)
    print('    START dwelling_information')

def payment_details(page: Page):
    print('    START payment_details')
    locus.do_locator(page, 'a', 'Rate Summary', locator_value='CLICK', do_clear=False, do_tab=False, sleep_time=6)
    locus.do_locator(page, 'a', 'Payment Details', locator_value='CLICK', do_clear=False, do_tab=False, sleep_time=3)

    locus.do_locator(page, 'textbox', 'Account', locator_value="+", iteration=2, sleep_time=2)
    locus.do_locator(page, 'textbox', 'Account Nickname', locator_value="Roxan Playwright Begg", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Account Type', locator_value="Checking", sleep_time=2)
    locus.do_locator(page, 'textbox', 'Routing Number', locator_value="111111118", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Account Number', locator_value="123456789", sleep_time=1)
    locus.do_locator(page, 'textbox', 'Method of Payment', locator_value="eCheck", sleep_time=2)
    locus.do_locator(page, 'checkbox', 'Use AutoPay Bank Account', locator_value="CHECK", sleep_time=1)

    page.screenshot(path="./log/screenshots/payment_details.png")
    #locus.do_locator(page, 'button', 'Next', locator_value="CLICK", sleep_time=5)
    print('    END payment_details')

def dwelling_information_360(page: Page):
    print('    START dwelling_information_360')
    locus.do_locator(page, 'a', 'Dwelling Information', locator_value='CLICK', do_clear=False, do_tab=False, sleep_time=5)

    loc_name = '#action_292'
    loc_type = 'button'
    print(f"      Checking:  page.locator({loc_name}), locator_name='{loc_type}'")
    loc = page.locator(loc_name)
    if loc is not None:
        print(f"        Found:  {locus.evaluate_locator(loc)}")
        #print(f"        Hover:")
        #loc.hover()
        #print(f"        Enter:")
        #page.keyboard.press("Enter")
        #print(f"        Enter Again:")
        #page.keyboard.press("Enter")
    else:
        print(f"Did not find locator {loc_name}")
    time.sleep(7)

    for i in range(25):
        focused_element_html = page.evaluate("document.activeElement.outerHTML")
        focused_locator = page.locator(f"css={focused_element_html}")
        print(f"        {locus.evaluate_locator(focused_locator)}")
        page.keyboard.press("Tab")


    if False:
        loc_name = '#iv360-continue'
        loc_type = 'button'
        print(f"      Checking:  page.locator({loc_name}), locator_name='{loc_type}'")

        max_attempts = 1
        done = False
        attempt = 0
        while not done:
            attempt += 1
            loc = page.locator(loc_name)
            try:
                loc.click() if loc is not None else print(f"        Did not find locator {loc_name}")
            except Exception as e:
                print(f"        Got Exception {e}")
            if attempt > max_attempts:
                done = True
        time.sleep(1)

        loc_name = 'Number of Stories'
        loc_type = 'textbox'
        print(f"      Checking:  locus.get_locator_object(page, locator_type='{loc_name}', locator_name='{loc_type}'")
        loc = locus.get_locator_object(page, locator_type="textbox", locator_name=loc_name)
        loc.type("4") if loc is not None else print(f"        Did not find locator {loc_name}")
        time.sleep(2)

    page.screenshot(path="./log/screenshots/dwelling_information_360.png")
    print('    END dwelling_information_360')

