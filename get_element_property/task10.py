import pytest
import re
from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

def parse_float(input_str):
    m = re.search('\d+\.?(\d+)?', input_str)
    if(m == None): raise Exception('Cannot find float value in the given string')
    return float(m.group(0))

def get_swd_instance(browser):
    runner = {
        "Chrome": lambda: SWD.Chrome(),
        "Firefox": lambda: SWD.Firefox(capabilities={'marionette': True}),
        "Ie": lambda: SWD.Ie(capabilities={'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True })
        }.get(browser)
    if runner != None: return runner()
    else: raise Exception('Unsupported browser')

@pytest.mark.parametrize("browser", ["Chrome", "Firefox", "Ie"])
def test_product_page(browser):
    try:
        webDriver = get_swd_instance(browser)
        webDriver.set_page_load_timeout(12)
        webDriver.implicitly_wait(3)
        
        webDriver.get("http://localhost/litecart/")
        
        alink = webDriver.find_element_by_css_selector('#box-campaigns ul.products > li.product > a.link')
        regular_price = alink.find_element_by_css_selector('.price-wrapper > .regular-price')
        campaign_price = alink.find_element_by_css_selector('.price-wrapper > .campaign-price')

        product_details = {}
        product_details['name'] = alink.find_element_by_css_selector('.name').text.strip()
        product_details['regular-price'] = regular_price.text.strip()
        product_details['campaign-price'] = campaign_price.text.strip()
        
        assert regular_price.get_attribute('tagName').lower() in ['s', 'strike'] #check regular price is strikeout
        assert regular_price.value_of_css_property('color').lower() in ['rgba(119, 119, 119, 1)', 'rgb(119, 119, 119)', '#777', '#777777'] #check regular price color

        assert campaign_price.get_attribute('tagName').lower() in ['b', 'strong'] #check campaign price is bold
        assert campaign_price.value_of_css_property('color').lower() in ['rgba(204, 0, 0, 1)', 'rgb(204, 0, 0)', '#c00', '#cc0000'] #check campaign price color

        assert parse_float(campaign_price.value_of_css_property('font-size')) > parse_float(regular_price.value_of_css_property('font-size'))
        
        ### open product page ###
        alink.click()
        WebDriverWait(webDriver, 5).until(expected_conditions.visibility_of_element_located([By.CSS_SELECTOR, '#box-product']), 'Page of product is not opened')
        product_box = webDriver.find_element_by_css_selector('#box-product')
        
        regular_price = product_box.find_element_by_css_selector('.price-wrapper > .regular-price')
        campaign_price = product_box.find_element_by_css_selector('.price-wrapper > .campaign-price')

        assert product_details['name'] == product_box.find_element_by_css_selector('h1.title').text.strip()
        assert product_details['regular-price'] == regular_price.text.strip()
        assert product_details['campaign-price'] == campaign_price.text.strip()

        assert regular_price.get_attribute('tagName').lower() in ['s', 'strike'] #check regular price is strikeout
        assert regular_price.value_of_css_property('color').lower() in ['rgba(102, 102, 102, 1)', 'rgb(102, 102, 102)', '#666', '#666666'] #check regular price color
        
        assert campaign_price.get_attribute('tagName').lower() in ['b', 'strong'] #check campaign price is bold
        assert campaign_price.value_of_css_property('color').lower() in ['rgba(204, 0, 0, 1)', 'rgb(204, 0, 0)', '#c00', '#cc0000'] #check campaign price color

        assert parse_float(campaign_price.value_of_css_property('font-size')) > parse_float(regular_price.value_of_css_property('font-size'))

    finally:
        webDriver.quit()
