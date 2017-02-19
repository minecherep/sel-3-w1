import pytest
from faker import Factory
from random import randint
from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

@pytest.fixture(scope="module")
def faker(request):
    return Factory.create( locale='en_US', providers=['faker.providers.address', 
                                                      'faker.providers.person', 
                                                      'faker.providers.internet', 
                                                      'faker.providers.misc'])

def get_swd_instance(browser):
    runner = {
        "Chrome": lambda: SWD.Chrome(),
        "Firefox": lambda: SWD.Firefox(capabilities={'marionette': True}),
        "Ie": lambda: SWD.Ie(capabilities={'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True })
        }.get(browser)
    if runner != None: return runner()
    else: raise Exception('Unsupported browser')

def set_checkbox(element, state):
    checked = element.get_property('checked')
    if(checked != state): element.click()
    return element

def input_text(input_element, text):
    input_element.clear()
    input_element.send_keys(text)
    return input_element

@pytest.mark.parametrize("browser", ["Chrome", "Firefox", "Ie"])
def test_product_page(faker, browser):
    try:
        webDriver = get_swd_instance(browser)
        webDriver.set_page_load_timeout(10)
        webDriver.implicitly_wait(4)
        
        webDriver.get("http://localhost/litecart/")
        webDriver.find_element(By.XPATH, '//*[@id="box-account-login"]//a[contains(@href,"create_account")]').click()

        profile = {}
        profile['company'] = 'No company'
        profile['first_name'] = faker.first_name()
        profile['last_name'] = faker.last_name()
        profile['address'] = faker.address()
        profile['city'] = faker.city()
        profile['postcode'] = faker.postalcode()
        profile['country'] = 'United States'
        profile['state'] = faker.state()
        profile['email'] = faker.free_email()
        profile['phone'] = "+1-{0}-{1}-{2}".format(randint(100, 999), randint(100, 999), randint(1000, 9999))
        profile['password'] = faker.password(randint(7,11))

        form = webDriver.find_element(By.CSS_SELECTOR, '#create-account form[name="customer_form"]')

        input_text(form.find_element_by_css_selector('input[name="company"]'), profile['company'])
        input_text(form.find_element_by_css_selector('input[name="firstname"]'), profile['first_name'])
        input_text(form.find_element_by_css_selector('input[name="lastname"]'), profile['last_name'])
        input_text(form.find_element_by_css_selector('input[name="address1"]'), profile['address'])
        input_text(form.find_element_by_css_selector('input[name="postcode"]'), profile['postcode'])
        input_text(form.find_element_by_css_selector('input[name="city"]'), profile['city'])
        
        form.find_element_by_css_selector('.selection > .select2-selection[role="combobox"]').click()
        webDriver.find_element_by_xpath('//*[@class="select2-results"]/ul[@class="select2-results__options"]/li[string(.)="{0}"]'.format(profile['country'])).click()
        
        WebDriverWait(webDriver, 10).until(lambda form: form.find_element_by_css_selector('select[name="zone_code"]').is_enabled(), 'Cannot choose State')

        form.find_element_by_xpath('//select[@name="zone_code"]/option[string(.)="{0}"]'.format(profile['state'])).click()

        input_text(form.find_element_by_css_selector('input[name="email"]'), profile['email'])
        input_text(form.find_element_by_css_selector('input[name="phone"]'), profile['phone'])
        
        set_checkbox(form.find_element_by_css_selector('input[name="newsletter"]'), False) #don't want to get spam :-)
        
        form.find_element_by_css_selector('input[name="password"]').send_keys(profile['password'])
        form.find_element_by_css_selector('input[name="confirmed_password"]').send_keys(profile['password'])
        
        form.find_element_by_css_selector('button[type="submit"]').click()
        
        logout_locator = [By.XPATH, '//*[@id="box-account"]//a[contains(@href,"logout")]']
        WebDriverWait(webDriver, 10).until(expected_conditions.element_to_be_clickable(logout_locator), 'Account is not created')
        
        webDriver.find_element(*logout_locator).click()
        
        login_form_locator = [By.CSS_SELECTOR, '#box-account-login form[name="login_form"]']
        WebDriverWait(webDriver, 10).until(expected_conditions.presence_of_element_located(login_form_locator), 'Unexpected page is opened after logout')
        
        login_form = webDriver.find_element(*login_form_locator)
        input_text(login_form.find_element_by_css_selector('input[name="email"]'), profile['email'])
        login_form.find_element_by_css_selector('input[name="password"]').send_keys(profile['password'])
        set_checkbox(login_form.find_element_by_css_selector('input[name="remember_me"]'), True)
        login_form.find_element_by_css_selector('button[type="submit"][name="login"]').click()
        
        WebDriverWait(webDriver, 10).until(expected_conditions.element_to_be_clickable(logout_locator), 'Cannot login to account')

        webDriver.find_element(*logout_locator).click()
        
        WebDriverWait(webDriver, 10).until(expected_conditions.presence_of_element_located(login_form_locator), 'Unexpected page is opened after logout')

    finally:
        webDriver.quit()
