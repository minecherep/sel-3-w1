import pytest

from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait as WDWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def get_swd_instance(browser):
    runner = {
        "Chrome": lambda: SWD.Chrome(),
        "Firefox": lambda: SWD.Firefox(capabilities={'marionette': True, 'pageLoadStrategy': 'eager'}),
        "Ie": lambda: SWD.Ie(capabilities={'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True, 'pageLoadStrategy': 'eager'})
        }.get(browser)
    if runner != None: return runner()
    else: raise Exception('Unsupported browser')

def get_lists_difference(l1, l2):
    ll = (l1, l2) if len(l1) > len(l2) else (l2, l1)

    res = []
    for i in ll[0]:
        if i not in ll[1]: res.append(i)

    return res

def login(webDriver):
    webDriver.get("http://localhost/litecart/admin")
    webDriver.find_element_by_xpath('//input[@name="username" and @type="text"]').send_keys('admin')
    webDriver.find_element_by_xpath('//input[@name="password" and @type="password"]').send_keys('123456')
    webDriver.find_element_by_xpath('//button[@name="login" and @type="submit"]').click()
    WDWait(webDriver, 7).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#sidebar .header a[title="Logout"]')), 'Cannot login to admin panel')

@pytest.mark.parametrize("browser", ["Chrome", "Firefox", "Ie"])
#@pytest.mark.parametrize("browser", ["Ie"])
def test_external_link(browser):
    try:
        webDriver = get_swd_instance(browser)
        webDriver.implicitly_wait(2)
        delay = 5

        login(webDriver)

        webDriver.find_element_by_xpath('//ul[@id="box-apps-menu"]//a[contains(@href,"countries")]').click()
        add_country_button = WDWait(webDriver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#content a.button[href*="edit_country"]')), 'Cannot press "Add New Country" button')
        add_country_button.click()
        WDWait(webDriver, delay).until(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="content"]/h1'), 'Add New Country'))

        win_tab_handles = dict(main=webDriver.current_window_handle)

        external_links = webDriver.find_elements(By.XPATH, '//*[@id="content"]//i[contains(@class,"fa-external-link")]/..')
        assert len(external_links) > 0, 'No links on external resources'
        
        for link in external_links:
            assert link.get_attribute('target') == '_blank' #an optional check (can be removed)
            old_win_handles = webDriver.window_handles
            link.click()
            
            WDWait(webDriver, delay).until(EC.new_window_is_opened(old_win_handles), 'The link is not opened in a new window/tab')
            #or
            #WDWait(webDriver, delay).until(EC.number_of_windows_to_be(2), 'The link is not opened in a new window/tab')

            new_win_tab_handles = get_lists_difference(webDriver.window_handles, old_win_handles)
            assert len(new_win_tab_handles) == 1 #an optional check (can be removed)

            webDriver.switch_to_window(new_win_tab_handles[0])

            assert 'litecart' not in webDriver.current_url #make sure that it is other page

            webDriver.close()
            
            webDriver.switch_to_window(win_tab_handles['main'])

    finally:
        webDriver.quit()
