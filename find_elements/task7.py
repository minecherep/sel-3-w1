import pytest
from selenium import webdriver as SWD
from selenium.webdriver.support.wait import WebDriverWait

@pytest.fixture
def webDriver(request):
    instance = SWD.Chrome()
    #instance = SWD.Firefox(capabilities={'marionette': True})
    #instance = SWD.Ie(capabilities={'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True })
    instance.set_page_load_timeout(10)
    instance.implicitly_wait(3)
    request.addfinalizer(instance.quit)
    return instance

def login(webDriver):
    webDriver.get("http://localhost/litecart/admin")
    webDriver.find_element_by_xpath('//input[@name="username" and @type="text"]').send_keys('admin')
    webDriver.find_element_by_xpath('//input[@name="password" and @type="password"]').send_keys('123456')
    webDriver.find_element_by_xpath('//button[@name="login" and @type="submit"]').click()
    WebDriverWait(webDriver, 7).until(lambda webDriver: webDriver.find_element_by_css_selector('a[title="Logout"]').is_displayed(), 'Cannot login to admin panel')

def test_admin_menu_items(webDriver):
    try:
        login(webDriver)

        menu_links = {
            'appearance':[{'doc':'template', 'h1': 'Template'},
                          {'doc': 'logotype', 'h1': 'Logotype'}],
            'catalog':[{'doc': 'catalog', 'h1': 'Catalog'},
                       {'doc': 'product_groups', 'h1': 'Product Groups'},
                       {'doc': 'option_groups', 'h1': 'Option Groups'},
                       {'doc': 'manufacturers', 'h1': 'Manufacturers'},
                       {'doc': 'suppliers', 'h1': 'Suppliers'},
                       {'doc': 'delivery_statuses', 'h1': 'Delivery Statuses'},
                       {'doc': 'sold_out_statuses', 'h1': 'Sold Out Statuses'},
                       {'doc': 'quantity_units', 'h1': 'Quantity Units'},
                       {'doc': 'csv', 'h1': 'CSV Import/Export'}],
            'countries':[{'doc': 'countries', 'h1': 'Countries'}],
            'currencies':[{'doc': 'currencies', 'h1': 'Currencies'}],
            'customers':[{'doc': 'customers', 'h1': 'Customers'},
                         {'doc': 'csv', 'h1': 'CSV Import/Export'},
                         {'doc': 'newsletter', 'h1': 'Newsletter'}],
            'geo_zones':[{'doc': 'geo_zones', 'h1': 'Geo Zones'}],
            'languages':[{'doc': 'languages', 'h1': 'Languages'},
                         {'doc': 'storage_encoding', 'h1': 'Storage Encoding'}],
            'modules':[{'doc': 'jobs', 'h1': 'Job Modules'},
                       {'doc': 'customer', 'h1': 'Customer Modules'},
                       {'doc': 'shipping', 'h1': 'Shipping Modules'},
                       {'doc': 'payment', 'h1': 'Payment Modules'},
                       {'doc': 'order_total', 'h1': 'Order Total Modules'},
                       {'doc': 'order_success', 'h1': 'Order Success Modules'},
                       {'doc': 'order_action', 'h1': 'Order Action Modules'}],
            'orders':[{'doc': 'orders', 'h1': 'Orders'},
                      {'doc': 'order_statuses', 'h1': 'Order Statuses'}],
            'pages':[{'doc': 'pages', 'h1': 'Pages'}],
            'reports':[{'doc': 'monthly_sales', 'h1': 'Monthly Sales'},
                       {'doc': 'most_sold_products', 'h1': 'Most Sold Products'},
                       {'doc': 'most_shopping_customers', 'h1': 'Most Shopping Customers'}],
            'settings':[{'doc': 'store_info', 'h1': 'Settings'},
                        {'doc': 'defaults', 'h1': 'Settings'},
                        {'doc': 'general', 'h1': 'Settings'},
                        {'doc': 'listings', 'h1': 'Settings'},
                        {'doc': 'images', 'h1': 'Settings'},
                        {'doc': 'checkout', 'h1': 'Settings'},
                        {'doc': 'advanced', 'h1': 'Settings'},
                        {'doc': 'security', 'h1': 'Settings'}],
            'slides':[{'doc': 'slides', 'h1': 'Slides'}],
            'tax':[{'doc': 'tax_classes', 'h1': 'Tax Classes'},
                   {'doc': 'tax_rates', 'h1': 'Tax Rates'}],
            'translations':[{'doc': 'search', 'h1': 'Search Translations'},
                            {'doc': 'scan', 'h1': 'Scan Files For Translations'},
                            {'doc': 'csv', 'h1': 'CSV Import/Export'}],
            'users':[{'doc': 'users', 'h1': 'Users'}],
            'vqmods':[{'doc': 'vqmods', 'h1': 'vQmods'}],
            }

        for app, submenu in sorted(menu_links.items()):
            for subitem in submenu:
                link_xpath_locator = 'a[contains(@href,"' + app +'") and contains(@href,"' + subitem['doc'] + '")]'
                
                webDriver.find_element_by_xpath('//ul[@id="box-apps-menu"]//' + link_xpath_locator).click()
                
                selected_item_locator = '//li[@class="selected"]/' + link_xpath_locator
               
                WebDriverWait(webDriver, 5).until(lambda webDriver: webDriver.find_element_by_xpath(selected_item_locator).is_displayed(), 'Selected menu item is not displayed')

                h1 = webDriver.find_element_by_css_selector('td#content > h1')
                
                assert h1.text.strip() == subitem['h1'];

    finally:
        webDriver.close()
