from support.webpage import WebPage

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException

class MainPage(WebPage):

    def open(self):
        super().open(EC.visibility_of_element_located((By.CSS_SELECTOR, '#box-most-popular')), self.wait_time, 'The main page is not opened')
        return self

    def click_on_most_popular_product(self, index):
        most_popular = self.find(By.CSS_SELECTOR, '#box-most-popular ul.products > li.product > a.link')

        try:
            link = most_popular[index-1]
        except IndexError:
            raise NoSuchElementException('No most popular product with such index in list')
        
        page_url = link.get_attribute('href')
        link.click()

        return ProductPage(self._app, page_url)

class ProductPage(WebPage):

    def add_to_cart(self):
        add_to_cart_button = self.wait(EC.element_to_be_clickable((By.CSS_SELECTOR, '#box-product button[name="add_cart_product"]')), self.wait_time, 'The "Add To Cart" button cannot be pressed')

        options =  self.find(By.XPATH, '//*[@id="box-product"]//form[@name="buy_now_form"]//select[contains(@name, "options")]')
        for option in options:
            Select(option).select_by_index(1)

        add_to_cart_button.click()

    def verify_cart_counter(self, value):
        result = self.wait(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#cart .content .quantity'), str(value)), self.wait_time, 'Cart counter is not "{0}"'.format(value))
        return result

class CartPage(WebPage):

    def open(self):
        self.find_one(By.CSS_SELECTOR, '#cart a.link').click()
        self.wait(EC.visibility_of_element_located((By.CSS_SELECTOR, '#order_confirmation-wrapper table.dataTable')), self.wait_time, 'Order table is not displayed')
        return self

    def get_items_count(self):
        rows_cnt = len(self.find(By.CSS_SELECTOR, '#order_confirmation-wrapper table.dataTable tr'))
        count = (rows_cnt - 5) if (rows_cnt > 5) else 0
        return count

    def remove_item_on_position(self, index):
        shortcuts = self.find(By.XPATH, '//*[@id="box-checkout-cart"]/ul[@class="shortcuts"]/li/a')

        if(len(shortcuts) > 0):
            try: 
                shortcuts[index -1].click()
            except IndexError:
                raise NoSuchElementException('No product in cart on position #{0}'.format(index))

        remove_from_cart_button = self.wait(EC.element_to_be_clickable((By.CSS_SELECTOR, '#box-checkout-cart ul.items > li.item button[name="remove_cart_item"]')), self.wait_time, 'The "Remove" button cannot be pressed')
        remove_from_cart_button.click();

        self.wait(EC.staleness_of(remove_from_cart_button), self.wait_time, 'Item is not removed')

        return self

    def is_displayed_empty_cart(self):
        elm = self.wait(EC.visibility_of_element_located((By.XPATH, '//*[@id="checkout-cart-wrapper"]/p[1]/em')), self.wait_time, 'Element is not displayed')
        return elm.text == 'There are no items in your cart.'
       
        