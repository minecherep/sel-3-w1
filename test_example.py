import pytest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture
def driver(request):
    wd = webdriver.Chrome()
    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd


def test_example(driver):
    driver.get("https://www.yandex.ru/")
    driver.find_element_by_id("text").send_keys("webdriver")
    driver.find_element_by_xpath("//div[@class='search2__button']/button[@type='submit']").click()
    WDW(driver, 10).until(EC.title_contains("webdriver — Яндекс:"))