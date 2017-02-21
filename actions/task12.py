import pytest
from os import path, listdir
from faker import Factory
from random import randint
from datetime import datetime
import clipboard

from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait as WDWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

@pytest.fixture(scope="module")
def faker(request):
    return Factory.create( locale='en_US', providers=['faker.providers.lorem'])

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

def login(webDriver):
    webDriver.get("http://localhost/litecart/admin")
    webDriver.find_element_by_xpath('//input[@name="username" and @type="text"]').send_keys('admin')
    webDriver.find_element_by_xpath('//input[@name="password" and @type="password"]').send_keys('123456')
    webDriver.find_element_by_xpath('//button[@name="login" and @type="submit"]').click()
    WDWait(webDriver, 7).until(EC.element_to_be_clickable([By.CSS_SELECTOR, '#sidebar .header a[title="Logout"]']), 'Cannot login to admin panel')

def get_random_image(_dir_):
    if not path.exists(_dir_): raise FileExistsError('Directory is not exist')
    _list_ = [_file_ for _file_ in listdir(_dir_) if (path.isfile(path.join(_dir_, _file_)) and (path.splitext(_file_)[1].lower() in ['.jpg', '.png', '.jpeg', '.gif']))]
    if len(_list_) == 0: raise FileExistsError('No image files')
    return path.join(_dir_, _list_[randint(0, len(_list_)-1)])

@pytest.mark.parametrize("browser", ["Chrome", "Firefox", "Ie"])
def test_add_new_product(faker, browser):
    try:
        webDriver = get_swd_instance(browser)
        webDriver.set_page_load_timeout(10)
        webDriver.implicitly_wait(4)

        login(webDriver)
        
        webDriver.find_element_by_xpath('//ul[@id="box-apps-menu"]//a[contains(@href,"catalog")]').click()
        webDriver.find_element_by_xpath('//*[@id="content"]//a[@class="button" and contains(@href,"edit_product")]').click()
        
        ###############
        # GENERAL TAB #
        ###############
        webDriver.find_element_by_css_selector('ul.index a[href="#tab-general"]').click()
        tab_selector = [By.CSS_SELECTOR, '#tab-general']
        WDWait(webDriver, 5).until(EC.visibility_of_element_located(tab_selector), 'Content of tab is not displayed')

        general_tab = webDriver.find_element(*tab_selector)

        general_tab.find_element_by_xpath('.//input[@name="status" and @value="1"]').click()
        
        product = {}
        product['name'] = "{0} Duck".format(faker.word().title())

        input_text(general_tab.find_element_by_xpath('.//input[contains(@name,"name")]'), product['name'])
        input_text(general_tab.find_element_by_css_selector('input[name="code"]'), "rd{0:0>3d}".format(randint(6, 999)))
        
        set_checkbox(general_tab.find_element_by_xpath('.//input[@name="categories[]" and @data-name="Root"]'), True)
        set_checkbox(general_tab.find_element_by_xpath('.//input[@name="categories[]" and @data-name="Rubber Ducks"]'), True)
    
        Select(general_tab.find_element_by_css_selector('select[name="default_category_id"]')).select_by_visible_text('Rubber Ducks')

        for gented in general_tab.find_elements_by_css_selector('input[name="product_groups[]"]'): set_checkbox(gented, True)
        
        input_text(general_tab.find_element_by_css_selector('input[name="quantity"]'), randint(6, 999).__str__())
        
        Select(general_tab.find_element_by_css_selector('select[name="quantity_unit_id"]')).select_by_index(1)
        Select(general_tab.find_element_by_css_selector('select[name="delivery_status_id"]')).select_by_index(1)
        Select(general_tab.find_element_by_css_selector('select[name="sold_out_status_id"]')).select_by_index(1)

        general_tab.find_element_by_css_selector('a#add-new-image').click() #add second image
        
        img_dir = path.realpath(path.join(path.dirname(__file__), '..', 'images'))
        
        for file_input in general_tab.find_elements_by_css_selector('input[name="new_images[]"]'): file_input.send_keys(get_random_image(img_dir))

        _now = datetime.now()
        date_format = "{0:4d}-{1:0>2d}-{2:0>2d}"
        if(browser == "Chrome"): date_format = "{2:0>2d}.{1:0>2d}.{0:4d}"
        
        general_tab.find_element_by_css_selector('input[name="date_valid_from"]').send_keys(date_format.format(_now.year, _now.month, _now.day))
        general_tab.find_element_by_css_selector('input[name="date_valid_to"]').send_keys(date_format.format(_now.year + 1, _now.month, _now.day))

        ###################
        # INFORMATION TAB #
        ###################
        webDriver.find_element_by_css_selector('ul.index a[href="#tab-information"]').click()
        tab_selector = [By.CSS_SELECTOR, '#tab-information']
        WDWait(webDriver, 5).until(EC.visibility_of_element_located(tab_selector), 'Content of tab is not displayed')

        info_tab = webDriver.find_element(*tab_selector)

        Select(info_tab.find_element_by_css_selector('select[name="manufacturer_id"]')).select_by_index(1)
        #Select(info_tab.find_element_by_css_selector('select[name="supplier_id"]')).select_by_index(0)
        
        input_text(info_tab.find_element_by_css_selector('input[name="keywords"]'), ", ".join(faker.words(randint(4, 7))))
        input_text(info_tab.find_element_by_xpath('.//input[contains(@name,"short_description")]'), faker.sentence(randint(6, 10)))
        
        description = faker.paragraph(randint(4, 6))
        editor = info_tab.find_element_by_css_selector('.trumbowyg-editor')
        
        if(browser != "Chrome"): 
            editor.send_keys(description)
        else:
            clipboard.copy(description)
            ActionChains(webDriver).key_down(Keys.CONTROL, editor).send_keys('v').key_up(Keys.CONTROL).perform() # doesn't work in IE11: print 'v' only

        input_text(info_tab.find_element_by_xpath('.//input[contains(@name,"head_title")]'), faker.sentence(randint(7, 10)))
        input_text(info_tab.find_element_by_xpath('.//input[contains(@name,"meta_description")]'), faker.sentence(randint(7, 10)))
        
        ##############
        # PRICES TAB #
        ##############
        webDriver.find_element_by_css_selector('ul.index a[href="#tab-prices"]').click()
        tab_selector = [By.CSS_SELECTOR, '#tab-prices']
        WDWait(webDriver, 5).until(EC.visibility_of_element_located(tab_selector), 'Content of tab is not displayed')

        prices_tab = webDriver.find_element(*tab_selector)

        input_text(prices_tab.find_element_by_css_selector('input[name="purchase_price"]'), "{0:d}.{1:0>2d}".format(randint(10, 120), randint(0, 99)))

        Select(prices_tab.find_element_by_css_selector('select[name="purchase_price_currency_code"]')).select_by_visible_text('US Dollars')

        input_text(prices_tab.find_element_by_css_selector('input[name="prices[USD]"]'), "{0:d}.{1:0>2d}".format(randint(10, 120), randint(0, 99)))
        input_text(prices_tab.find_element_by_css_selector('input[name="prices[EUR]"]'), "0.00")
        
        # SAVE PRODUCT
        webDriver.find_element_by_css_selector('button[type="submit"][name="save"]').click()
        
        table_selector = [By.CSS_SELECTOR, '#content table.dataTable']
        WDWait(webDriver, 10).until(EC.visibility_of_element_located(table_selector), 'Products list is not displayed')
        
        links_list = webDriver.find_element(*table_selector).find_elements_by_xpath('.//tr[@class="row"]/td[3]/a')
        
        searched_link = None
        for item in links_list:
            if(item.text == product['name']):
                searched_link = item
                break
        
        assert searched_link is not None, 'Product was not added'

        searched_link.click()
        
        tab_locator = [By.CSS_SELECTOR, '#tab-general']
        WDWait(webDriver, 10).until(EC.visibility_of_element_located(tab_locator), 'Edit product page is not displayed')
        
        name_in_input = webDriver.find_element(*tab_locator).find_element_by_xpath('.//input[contains(@name,"name")]').get_attribute('value')

        assert name_in_input == product['name'], 'Fail'

    finally:
        webDriver.quit()
