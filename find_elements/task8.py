import pytest
from selenium import webdriver as SWD
from selenium.webdriver.common.by import By

@pytest.fixture
def webDriver(request):
    instance = SWD.Chrome()
    #instance = SWD.Firefox(capabilities={'marionette': True})
    #instance = SWD.Ie(capabilities={'ignoreProtectedModeSettings': True, 'ignoreZoomSetting': True })
    instance.set_page_load_timeout(5)
    instance.implicitly_wait(2)
    request.addfinalizer(instance.quit)
    return instance

def test_product_sticker(webDriver):
    try:
        webDriver.get("http://localhost/litecart")

        products_blocks = ['#box-most-popular', '#box-campaigns', '#box-latest-products']

        for block in products_blocks:
            products_list = webDriver.find_elements(By.CSS_SELECTOR, '{0} ul.products > li.product'.format(block));
            assert len(products_list) > 0

            for product in products_list:
                stickers = product.find_elements(By.CSS_SELECTOR, '.sticker');
                assert len(stickers) == 1
                #assert stickers[0].text.lower() in ['sale', 'new']

    finally:
        webDriver.close()
