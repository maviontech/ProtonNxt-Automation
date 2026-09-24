"""Calendar and MavionMeet account settings."""

import re
from urllib.parse import urljoin, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class CalendarSettingsPage:
    PATH = "/interview/calendar/settings/"
    HEADING = (By.XPATH, "//h1[contains(normalize-space(), 'Calendar & MavionMeet')]")
    EMAIL = (By.XPATH, "//label[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'mavionmeet email')]/following::input[1]")
    API_KEY = (By.XPATH, "//label[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'api key')]/following::input[1]")
    CONNECT = (By.XPATH, "//button[contains(normalize-space(), 'Connect & verify')]")
    REVOKE = (By.XPATH, "//button[contains(normalize-space(), 'Revoke')]")
    CONNECTED_CARD = (By.XPATH, "//button[contains(normalize-space(), 'Revoke')]/ancestor::*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'connected')][1]")
    BACK = (By.XPATH, "//a[contains(normalize-space(), 'Back to Calendar')]")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(urljoin(Config.BASE_URL, self.PATH))
        self.wait.until(EC.visibility_of_element_located(self.HEADING))
        assert urlparse(self.driver.current_url).path == self.PATH
        return self

    def email_input(self):
        return self.wait.until(EC.visibility_of_element_located(self.EMAIL))

    def key_input(self):
        return self.wait.until(EC.visibility_of_element_located(self.API_KEY))

    def connect_button(self):
        return self.wait.until(EC.visibility_of_element_located(self.CONNECT))

    def is_connected(self):
        return any(button.is_displayed() for button in self.driver.find_elements(*self.REVOKE))

    def connected_email(self):
        if not self.is_connected():
            return ""
        card_text = self.driver.find_element(*self.CONNECTED_CARD).text
        match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", card_text, re.IGNORECASE)
        return match.group(0) if match else ""

    def connection_is_confirmed(self):
        return self.is_connected() and "CONNECTED" in self.driver.find_element(*self.CONNECTED_CARD).text.upper()

    def connect(self, email, api_key):
        email_field = self.email_input()
        email_field.clear()
        email_field.send_keys(email)
        key_field = self.key_input()
        key_field.clear()
        key_field.send_keys(api_key)
        self.wait.until(EC.element_to_be_clickable(self.CONNECT)).click()
        self.wait.until(lambda _: self.connection_is_confirmed() or self._visible_error())

    def _visible_error(self):
        return any(
            element.is_displayed() and element.text.strip()
            for element in self.driver.find_elements(
                By.CSS_SELECTOR, "[role='alert'], .alert-danger, .error, .error-message"
            )
        )

    def back_to_calendar(self):
        href = self.wait.until(EC.element_to_be_clickable(self.BACK)).get_attribute("href")
        self.driver.find_element(*self.BACK).click()
        self.wait.until(lambda d: urlparse(d.current_url).path != self.PATH)
        return href
