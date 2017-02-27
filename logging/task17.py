import pytest
import time

from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait as WDWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def login(webDriver):
    webDriver.get("http://localhost/litecart/admin")
    webDriver.find_element_by_xpath('//input[@name="username" and @type="text"]').send_keys('admin')
    webDriver.find_element_by_xpath('//input[@name="password" and @type="password"]').send_keys('123456')
    webDriver.find_element_by_xpath('//button[@name="login" and @type="submit"]').click()
    WDWait(webDriver, 7).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#sidebar .header a[title="Logout"]')), 'Cannot login to admin panel')

def test_browser_log():
    try:
        # unfortunately FF via geckodriver and IE don't support browser's log, hence use Chrome only
        webDriver = SWD.Chrome()
        webDriver.set_page_load_timeout(10)
        webDriver.implicitly_wait(2)
        delay = 5

        login(webDriver)

        assert 'browser' in webDriver.log_types, 'Browser log is not supported' # an optional check

        webDriver.find_element_by_xpath('//ul[@id="box-apps-menu"]//a[contains(@href,"catalog")]').click()
        WDWait(webDriver, delay).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="content"]/h1'), 'Catalog'), 'Catalog page is not opened')
        
        webDriver.find_element_by_xpath('//*[@id="content"]//table[@class="dataTable"]//a[string(.)="Rubber Ducks"]').click()
        
        target_links_locator = (By.XPATH, '//*[@id="content"]//table[@class="dataTable"]//tr[@class="row"]/td[3]/a[contains(@href,"product_id")]')
        WDWait(webDriver, delay).until(lambda webDriver: len(webDriver.find_elements(*target_links_locator)) > 0)

        target_links = webDriver.find_elements(*target_links_locator)
        
        urls = [a.get_attribute('href') for a in target_links] # list of pages for visit

        # verify that the browser's log is empty for all pages
        for url in urls:
            webDriver.get(url)
            WDWait(webDriver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"][name="delete"]')))
            time.sleep(3) # delay for executing javascripts (optional)
            
            log = webDriver.get_log('browser')

            try:
                assert len(log) == 0, "Browser's log is not empty"
            except AssertionError as ae:
                for msg in log:
                    print(msg)
                raise ae

        # verify that the browser's log works correctly
        webDriver.get(urls[0])
        WDWait(webDriver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"][name="delete"]')))
        time.sleep(3) # delay for executing javascripts (optional)
        webDriver.execute_script('console.error("[ERROR]: Test error")')
        log = webDriver.get_log('browser')
        assert len(log) > 0, "Browser's log is empty"

    finally:
        webDriver.quit()
