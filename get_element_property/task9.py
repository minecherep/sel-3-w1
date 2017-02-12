import pytest
from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait

@pytest.fixture
def webDriver(request):
    instance = SWD.Chrome()
    #instance = SWD.Firefox(capabilities={'marionette': True})
    #instance = SWD.Ie(capabilities={'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True })
    instance.set_page_load_timeout(12)
    instance.implicitly_wait(3)
    request.addfinalizer(instance.quit)
    return instance

def login(webDriver):
    webDriver.get("http://localhost/litecart/admin")
    webDriver.find_element_by_xpath('//input[@name="username" and @type="text"]').send_keys('admin')
    webDriver.find_element_by_xpath('//input[@name="password" and @type="password"]').send_keys('123456')
    webDriver.find_element_by_xpath('//button[@name="login" and @type="submit"]').click()
    WebDriverWait(webDriver, 7).until(lambda webDriver: webDriver.find_element_by_css_selector('a[title="Logout"]').is_displayed(), 'Cannot login to admin panel')

def test_countries_zones_sorting(webDriver):
    try:
        login(webDriver)
        
        webDriver.get("http://localhost/litecart/admin/?app=countries&doc=countries")
        #webDriver.find_element_by_css_selector('ul#box-apps-menu a[href*="countries"]').click()

        rows = webDriver.find_elements_by_css_selector('td#content table.dataTable tr.row')
        assert len(rows) > 0

        previous_country_name = ''
        countries_with_zones = []

        for row in rows:
            link = row.find_element_by_xpath('.//td[5]/a')
            current_country_name = link.text.strip().lower()
            assert current_country_name > previous_country_name
            previous_country_name = current_country_name

            zones_count = int(row.find_element_by_xpath('.//td[6]').text.strip())

            if zones_count > 0:
                countries_with_zones.append((link.get_attribute('href'), zones_count))

        for country in countries_with_zones:
            webDriver.get(country[0])

            rows = webDriver.find_elements_by_css_selector('table#table-zones tr:not([class="header"]')
            rows.pop() # remove last row which is used to append zones
            assert len(rows) == country[1]
            
            previous_zone_name = ''

            for row in rows:
                current_zone_name = row.find_element_by_xpath('.//td[3]').text.strip().lower()
                assert current_zone_name > previous_zone_name
                previous_zone_name = current_zone_name
        
        ##############################
        ####### test geo zones #######
        ##############################
        webDriver.get("http://localhost/litecart/admin/?app=geo_zones&doc=geo_zones")
        
        rows = webDriver.find_elements_by_css_selector('td#content table.dataTable tr.row')
        assert len(rows) > 0
        
        countries_with_geo_zones = []

        for row in rows:
            link = row.find_element_by_xpath('.//td[3]/a')
            gzones_count = int(row.find_element_by_xpath('.//td[4]').text)
            countries_with_geo_zones.append((link.get_attribute('href'), gzones_count))

        for country in countries_with_geo_zones:
            webDriver.get(country[0])

            rows = webDriver.find_elements_by_css_selector('table#table-zones tr:not([class="header"]')
            rows.pop() # remove last row which is used to append geo zones
            assert len(rows) == country[1]
            
            previous_geo_zone_name = ''

            for row in rows:
                select = row.find_element_by_xpath('.//td[3]/select')
                current_geo_zone_name = select.find_element_by_css_selector('option[value="{0}"]'.format(select.get_attribute('value'))).text.strip().lower()
                #current_geo_zone_name = select.find_element_by_xpath('.//option[{0}]'.format(int(select.get_attribute('selectedIndex'))+1)).text.strip().lower()

                assert current_geo_zone_name > previous_geo_zone_name
                previous_geo_zone_name = current_geo_zone_name

    finally:
        webDriver.close()
