import time
from urllib.parse import urlparse

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class LoginPage:
    LOGIN_FORM = (By.ID, "login-form")
    COMPANY_CODE_INPUT = (By.ID, "company_code")
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.ID, "error-message")
    FORGOT_PASSWORD_LINK = (
        By.XPATH,
        "//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'forgot password')]",
    )
    REMEMBER_ME_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    TENANT_ADMIN_PORTAL_BUTTON = (
        By.XPATH,
        "//*[self::a or self::button][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'tenant administration portal')]",
    )
    SUBSCRIPTION_PACKAGES_LINK = (
        By.XPATH,
        "//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'subscription package')]",
    )
    PASSWORD_TOGGLE = (
    By.ID,
    "toggle-password",
    )

    DASHBOARD_SIDEBAR = (By.ID, "sidebar")
    PRELOGOUT_LINK = (By.CSS_SELECTOR, "a[href='/prelogout/']")
    FINAL_LOGOUT_BUTTON = (By.CSS_SELECTOR, "form[action='/logout/'] button[type='submit']")
    SIGN_IN_AGAIN_BUTTON = (
        By.XPATH,
        "//*[self::a or self::button][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]",
    )
    AUTHENTICATED_NAV_MARKERS = (
        (By.ID, "sidebar"),
        (By.CSS_SELECTOR, "a[href='/prelogout/']"),
        (By.XPATH, "//*[contains(normalize-space(), 'Recruitment Tasks')]"),
        (By.XPATH, "//*[contains(normalize-space(), 'Dashboard')]"),
    )

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url):
        self.driver.get(url)

    def open_path(self, path):
        self.driver.get(f"{Config.BASE_URL.rstrip('/')}/{path.lstrip('/')}")

    def _visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def _present(self, locator):
        return self.driver.find_elements(*locator)

    def _is_visible(self, locator):
        try:
            self._visible(locator)
            return True
        except TimeoutException:
            return False

    def _is_displayed_now(self, locator):
        elements = self.driver.find_elements(*locator)
        for element in elements:
            try:
                if element.is_displayed():
                    return True
            except Exception:
                continue
        return False

    def is_login_page_displayed(self):
        return self._is_visible(self.LOGIN_FORM)

    def is_username_displayed(self):
        return self._is_visible(self.USERNAME_INPUT)

    def is_password_displayed(self):
        return self._is_visible(self.PASSWORD_INPUT)

    def is_company_code_displayed(self):
        return self._is_visible(self.COMPANY_CODE_INPUT)

    def is_login_button_displayed(self):
        return self._is_visible(self.LOGIN_BUTTON)

    def is_forgot_password_link_displayed(self):
        return self._is_visible(self.FORGOT_PASSWORD_LINK)

    def is_remember_me_checkbox_displayed(self):
        return self._is_visible(self.REMEMBER_ME_CHECKBOX)

    def is_tenant_admin_portal_button_displayed(self):
        return self._is_visible(self.TENANT_ADMIN_PORTAL_BUTTON)

    def is_subscription_packages_link_displayed(self):
        return self._is_visible(self.SUBSCRIPTION_PACKAGES_LINK)

    def is_password_toggle_displayed(self):
        return self._is_visible(self.PASSWORD_TOGGLE)

    def get_password_input_type(self):
        return self._visible(self.PASSWORD_INPUT).get_attribute("type")

    def get_company_code_value(self):
        return self._visible(self.COMPANY_CODE_INPUT).get_attribute("value")

    def get_username_value(self):
        return self._visible(self.USERNAME_INPUT).get_attribute("value")

    def get_password_value(self):
        return self._visible(self.PASSWORD_INPUT).get_attribute("value")

    def _native_validation_message(self, locator):
        element = self._visible(locator)
        return self.driver.execute_script("return arguments[0].validationMessage || '';", element).strip()

    def _is_field_invalid(self, locator):
        element = self._visible(locator)
        return not self.driver.execute_script("return arguments[0].checkValidity();", element)

    def is_remember_me_selected(self):
        return self._visible(self.REMEMBER_ME_CHECKBOX).is_selected()

    def get_company_code_validation_message(self):
        return self._native_validation_message(self.COMPANY_CODE_INPUT)

    def get_username_validation_message(self):
        return self._native_validation_message(self.USERNAME_INPUT)

    def get_password_validation_message(self):
        return self._native_validation_message(self.PASSWORD_INPUT)

    def is_company_code_invalid(self):
        return self._is_field_invalid(self.COMPANY_CODE_INPUT)

    def is_username_invalid(self):
        return self._is_field_invalid(self.USERNAME_INPUT)

    def is_password_invalid(self):
        return self._is_field_invalid(self.PASSWORD_INPUT)

    def set_remember_me(self, should_select):
        checkbox = self._visible(self.REMEMBER_ME_CHECKBOX)
        if checkbox.is_selected() != should_select:
            checkbox.click()

    def click_password_toggle(self):
        self._clickable(self.PASSWORD_TOGGLE).click()

    def click_forgot_password(self):
        self._clickable(self.FORGOT_PASSWORD_LINK).click()

    def click_tenant_admin_portal(self):
        self._clickable(self.TENANT_ADMIN_PORTAL_BUTTON).click()

    def click_subscription_packages(self):
        self._clickable(self.SUBSCRIPTION_PACKAGES_LINK).click()

    def current_path(self):
        return urlparse(self.driver.current_url).path

    def current_url_contains(self, text):
        return text.lower() in self.driver.current_url.lower()

    def is_authenticated_destination_displayed(self):
        return self.wait_for_authenticated_destination(timeout=25)

    def _masked_value(self, value):
        return "*" * len(value) if value else "(empty)"

    def _pause(self, seconds):
        if seconds > 0:
            time.sleep(seconds)

    def _type_slowly(self, element, value):
        for character in value:
            element.send_keys(character)
            self._pause(Config.LOGIN_TYPE_DELAY)

    def _set_password_visibility(self, visible):
        password_input = self._visible(self.PASSWORD_INPUT)
        input_type = "text" if visible else "password"
        self.driver.execute_script("arguments[0].setAttribute('type', arguments[1]);", password_input, input_type)

    def fill_login_form(self, company_code="", username="", password="", remember_me=None):
        print("[Login Input] company_code=", company_code or "(empty)")
        print("[Login Input] username=", username or "(empty)")
        print("[Login Input] password=", self._masked_value(password))

        company_input = self._visible(self.COMPANY_CODE_INPUT)
        company_input.clear()
        self._type_slowly(company_input, company_code)
        self._pause(Config.LOGIN_STEP_DELAY)

        username_input = self._visible(self.USERNAME_INPUT)
        username_input.clear()
        self._type_slowly(username_input, username)
        self._pause(Config.LOGIN_STEP_DELAY)

        password_input = self._visible(self.PASSWORD_INPUT)
        password_input.clear()
        if Config.SHOW_PASSWORD_WHILE_TYPING:
            self._set_password_visibility(True)
        self._type_slowly(password_input, password)
        self._pause(Config.LOGIN_STEP_DELAY)
        if Config.SHOW_PASSWORD_WHILE_TYPING:
            self._set_password_visibility(False)

        if remember_me is not None and self.is_remember_me_checkbox_displayed():
            self.set_remember_me(remember_me)

    def submit(self):
        self._pause(Config.LOGIN_STEP_DELAY)
        current_url = self.driver.current_url
        login_form = self._visible(self.LOGIN_FORM)
        button = self._clickable(self.LOGIN_BUTTON)
        try:
            button.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", button)

        self._wait_for_post_submit_transition(login_form, current_url)

    def login(self, company_code, username, password, remember_me=None):
        self.fill_login_form(
            company_code=company_code,
            username=username,
            password=password,
            remember_me=remember_me,
        )
        self.submit()
        self.wait_for_authenticated_destination(timeout=25)

    def submit_login_without_changes(self):
        self.submit()

    def is_dashboard_displayed(self):
        return any(self._is_displayed_now(locator) for locator in self.AUTHENTICATED_NAV_MARKERS)

    def is_authentication_screen_displayed(self):
        page_source = self.driver.page_source.lower()
        current_url = self.driver.current_url.lower()
        current_path = self.current_path().lower()
        return (
            self._is_displayed_now(self.LOGIN_FORM)
            or current_path in ("", "/", "/login", "/login/", "/logout", "/logout/")
            or current_url.endswith("/logout/")
            or "logged out" in page_source
            or "sign in" in page_source
            or "login" in page_source
        )

    def wait_for_authenticated_destination(self, timeout=25):
        def authenticated(_):
            return self.is_dashboard_displayed() or not self.is_authentication_screen_displayed()

        try:
            WebDriverWait(self.driver, timeout).until(authenticated)
            return True
        except TimeoutException:
            return False

    def _wait_for_post_submit_transition(self, login_form, previous_url, timeout=12):
        def transitioned(_):
            if self.driver.current_url != previous_url:
                return True
            if self.is_dashboard_displayed():
                return True
            if self._is_displayed_now(self.ERROR_MESSAGE):
                return True
            try:
                return EC.staleness_of(login_form)(self.driver)
            except StaleElementReferenceException:
                return True

        try:
            WebDriverWait(self.driver, timeout).until(transitioned)
        except TimeoutException:
            return False
        return True

    def is_invalid_login_message_displayed(self):
        return self._is_visible(self.ERROR_MESSAGE)

    def get_error_message_text(self):
        if not self.is_invalid_login_message_displayed():
            return ""
        return self._visible(self.ERROR_MESSAGE).text.strip()

    def page_contains_text(self, *needles):
        haystack = self.driver.page_source.lower()
        return any(needle.lower() in haystack for needle in needles if needle)

    def has_lockout_message(self):
        message = self.get_error_message_text().lower()
        if any(keyword in message for keyword in Config.LOCK_MESSAGE_KEYWORDS):
            return True
        return self.page_contains_text(*Config.LOCK_MESSAGE_KEYWORDS)

    def clear_session_storage(self):
        try:
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        except WebDriverException:
            return False
        return True

    def logout(self):
        self._clickable(self.PRELOGOUT_LINK).click()
        self._clickable(self.FINAL_LOGOUT_BUTTON).click()

    def ensure_login_form_displayed(self):
        if self.is_login_page_displayed():
            return True

        if self._is_visible(self.SIGN_IN_AGAIN_BUTTON):
            self._clickable(self.SIGN_IN_AGAIN_BUTTON).click()

        return self.is_login_page_displayed()
