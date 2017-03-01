import pytest

from support.factory import WebDriverFactory
from support.app import Application
from pageObjects.pages import MainPage, CartPage

@pytest.mark.parametrize("browser", ["Chrome", "Firefox", "Ie"])
def test_add_to_cart(browser):
    try:

        app = Application(WebDriverFactory.create(browser))
        app.set_options({'page_load_timeout': 5, 'implicitly_wait': 0})

        mainPage = MainPage(app, 'http://localhost/litecart')
        
        for i in range(1, 4):
            mainPage.open()

            duck_page = mainPage.click_on_most_popular_product(i)
            duck_page.add_to_cart()
        
        cartPage = CartPage(app).open()
        
        rows_count = cartPage.get_items_count()

        assert 1 < rows_count < 4, 'Check that order table contains rows of products'

        for i in range(1, rows_count + 1):
            cartPage.remove_item_on_position(1)
            assert cartPage.get_items_count() == (rows_count-i), 'Order table is not updated'
            
        assert cartPage.is_displayed_empty_cart(), 'No messages that the cart is empty'

    finally:
        app.exit()