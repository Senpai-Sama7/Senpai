import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserController:
    def __init__(self, driver_path='chromedriver'):
        self.driver = webdriver.Chrome(executable_path=driver_path)

    def navigate_to(self, url):
        self.driver.get(url)

    def enter_text(self, selector, text, selector_type=By.CSS_SELECTOR):
        element = self.driver.find_element(selector_type, selector)
        element.send_keys(text)

    def click_element(self, selector, selector_type=By.CSS_SELECTOR):
        element = self.driver.find_element(selector_type, selector)
        element.click()

    def take_screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def get_page_source(self):
        return self.driver.page_source

    def close(self):
        self.driver.quit()
