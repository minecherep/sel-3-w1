import pytest

from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait as WDWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By

def get_swd_instance(browser):
    runner = {
        "Chrome": lambda: SWD.Chrome(),
        "Firefox": lambda: SWD.Firefox(capabilities={'marionette': True}),
        "Ie": lambda: SWD.Ie(capabilities={'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True })
        }.get(browser)
    if runner != None: return runner()
    else: raise Exception('Unsupported browser')

@pytest.mark.parametrize("browser", ["Chrome", "Firefox", "Ie"])
def test_add_to_cart(browser):
    try:
        webDriver = get_swd_instance(browser)
        webDriver.set_page_load_timeout(5)
        webDriver.implicitly_wait(0) #special for using 'explicit waiting' only
        delay = 4

        webDriver.get("http://localhost/litecart")

        for i in range(1, 4):
            first_product = WDWait(webDriver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#box-most-popular ul.products > li.product:first-of-type > a.link')), 'The first Most popular product')
            first_product.click()
            add_to_cart_button = WDWait(webDriver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#box-product button[name="add_cart_product"]')), 'The "Add To Cart" button cannot be pressed')

            options = webDriver.find_elements_by_xpath('//*[@id="box-product"]//form[@name="buy_now_form"]//select[contains(@name, "options")]')
            for option in options:
                Select(option).select_by_index(1)

            add_to_cart_button.click()
            WDWait(webDriver, delay).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#cart .content .quantity'), str(i)), 'Cart counter is not updated')
            webDriver.back()
            WDWait(webDriver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#box-most-popular')))
            webDriver.refresh() # for changing first item

        webDriver.find_element_by_css_selector('#cart a.link').click();

        oder_table = WDWait(webDriver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#order_confirmation-wrapper table.dataTable')), 'Order table is not displayed')

        rows_count = len(oder_table.find_elements_by_css_selector('tr'))
        assert rows_count > 5, 'Check that order table contains rows of products'
        last_in_cart = False

        for i in range(1, rows_count - 4):
            shortcuts = webDriver.find_elements_by_xpath('//*[@id="box-checkout-cart"]/ul[@class="shortcuts"]/li/a')
            if(len(shortcuts) > 0): 
                shortcuts[0].click()
            else: last_in_cart = True
            
            remove_from_cart = WDWait(webDriver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#box-checkout-cart ul.items > li.item button[name="remove_cart_item"]')), 'The "Remove" button cannot be pressed')
            remove_from_cart.click();
            
            if not(last_in_cart):
                WDWait(webDriver, delay).until(lambda webDriver: len(webDriver.find_elements_by_css_selector('#order_confirmation-wrapper table.dataTable tr')) == (rows_count-i), 'Order table is not updated')
            else: 
                WDWait(webDriver, delay).until(EC.staleness_of(oder_table), 'Order table is not removed')

        WDWait(webDriver, delay).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="checkout-cart-wrapper"]/p[1]/em'), 'There are no items in your cart.'))

    finally:
        webDriver.quit()
