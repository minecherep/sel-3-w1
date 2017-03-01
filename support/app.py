from selenium.webdriver.support.wait import WebDriverWait as WDWait
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

class Application:

    def __init__(self, driver = None):
        if(not isinstance(driver, RemoteWebDriver)):
            raise ValueError('Invalid input parameter: it should be instance of inheritor of "selenium.webdriver.remote.webdriver.WebDriver" class')
        self._driver = driver
        #options by defaults
        self._driver.set_page_load_timeout(0)
        self._driver.implicitly_wait(0)

    def set_options(self, options):
        for option_name, option_value  in options.items():
            web_driver_method = getattr(self._driver, option_name, None)
            if(web_driver_method is None):
                web_driver_method = getattr(self._driver, 'set_' + option_name, None)
                if(web_driver_method is None): raise Exception('Unknown option: {0}'.format(option_name))
                
            web_driver_method(option_value)
        return self

    def openPage(self, url, wait_condition = None, time = 0, timeout_msg = ''):
        self._driver.get(url)
        if(wait_condition is not None):
            WDWait(self._driver, time).until(wait_condition, timeout_msg)
        return self

    def wait(self, wait_condition, time, timeout_msg):
        result = WDWait(self._driver, time).until(wait_condition, timeout_msg)
        return result

    def find(self, by, locator):
        return self._driver.find_elements(by, locator)

    def find_one(self, by, locator):
        return self._driver.find_element(by, locator)

    def exit(self):
        self._driver.quit()