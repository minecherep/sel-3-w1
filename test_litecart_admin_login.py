import pytest
from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

@pytest.fixture
def webDriver(request):
    instance = SWD.Chrome()
    request.addfinalizer(instance.quit)
    return instance

def test_example(webDriver):
    try:
        webDriver.get("http://localhost/litecart/admin")
        
        webDriver.find_element_by_xpath('//input[@name="username" and @type="text"]').send_keys('admin')
        webDriver.find_element_by_xpath('//input[@name="password" and @type="password"]').send_keys('123456')
    
        remember_me = webDriver.find_element_by_xpath('//input[@name="remember_me" and @type="checkbox"]')
        remember_me_checked = remember_me.get_property('checked');
        
        if not(remember_me_checked):
            remember_me.click()

        webDriver.find_element_by_xpath('//button[@name="login" and @type="submit"]').click()
        
        WebDriverWait(webDriver, 7).until(lambda webDriver: webDriver.find_element(By.CSS_SELECTOR, 'tr.header th').is_displayed(), 'Main page of admin\'s panel is not opened')

        assert webDriver.find_element_by_css_selector('tr.header th').text == 'Statistics'

    finally:
        webDriver.close()
