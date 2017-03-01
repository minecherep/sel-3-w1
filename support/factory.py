from selenium import webdriver as SWD
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import WebDriverException

class WebDriverFactory:

    @staticmethod
    def create(browser, capabilities = {}):
        if(not isinstance(capabilities, dict)):
            raise TypeError('Invalid input parameter: the "capabilities" must be dictinary')
        
        specific_method = getattr(__class__, browser.lower(), None)

        if(specific_method is None):
            raise WebDriverException('Unsupported browser: {0}'.format(browser))
        
        return specific_method(capabilities)

    @staticmethod
    def chrome(capabilities):
        ch_capabilities = capabilities
        return SWD.Chrome(chrome_options=ChromeOptions(), desired_capabilities = ch_capabilities)
        
    @staticmethod
    def firefox(capabilities):
        ff_capabilities = {'marionette': True}.update(capabilities)
        return SWD.Firefox(capabilities = ff_capabilities)

    @staticmethod
    def ie(capabilities):
        ie_capabilities = {'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True }.update(capabilities)
        return SWD.Ie(capabilities = ie_capabilities)
