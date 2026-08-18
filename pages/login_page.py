from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    LOGIN_FORM = (By.ID, "login-form")
    COMPANY_CODE_INPUT = (By.ID, "company_code")
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.ID, "error-message")

    DASHBOARD_SIDEBAR = (By.ID, "sidebar")
    PRELOGOUT_LINK = (By.CSS_SELECTOR, "a[href='/prelogout/']")
    FINAL_LOGOUT_BUTTON = (By.CSS_SELECTOR, "form[action='/logout/'] button[type='submit']")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url):
        self.driver.get(url)

    def _visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def _is_visible(self, locator):
        try:
            self._visible(locator)
            return True
        except TimeoutException:
            return False

    def is_login_page_displayed(self):
        return self._is_visible(self.LOGIN_FORM)

    def is_username_displayed(self):
        return self._is_visible(self.USERNAME_INPUT)

    def is_password_displayed(self):
        return self._is_visible(self.PASSWORD_INPUT)

    def is_login_button_displayed(self):
        return self._is_visible(self.LOGIN_BUTTON)

    def login(self, company_code, username, password):
        company_input = self._visible(self.COMPANY_CODE_INPUT)
        company_input.clear()
        company_input.send_keys(company_code)

        username_input = self._visible(self.USERNAME_INPUT)
        username_input.clear()
        username_input.send_keys(username)

        password_input = self._visible(self.PASSWORD_INPUT)
        password_input.clear()
        password_input.send_keys(password)

        self._clickable(self.LOGIN_BUTTON).click()

    def is_dashboard_displayed(self):
        return self._is_visible(self.DASHBOARD_SIDEBAR)

    def is_invalid_login_message_displayed(self):
        return self._is_visible(self.ERROR_MESSAGE)

    def logout(self):
        self._clickable(self.PRELOGOUT_LINK).click()
        self._clickable(self.FINAL_LOGOUT_BUTTON).click()

    def is_authentication_screen_displayed(self):
        page_source = self.driver.page_source.lower()
        current_url = self.driver.current_url.lower()
        return (
            self.is_login_page_displayed()
            or current_url.endswith("/logout/")
            or "logged out" in page_source
            or "sign in" in page_source
            or "login" in page_source
        )
