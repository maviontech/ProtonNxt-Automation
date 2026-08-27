from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class CreateCustomerPage:
    PAGE_PATH = "/create_customer/"

    PAGE_HEADING = (By.XPATH, "//h2[normalize-space()='Create Customer']")
    CUSTOMER_DETAILS_SECTION = (
        By.XPATH,
        "//*[self::h2 or self::h3][normalize-space()='Customer Details']",
    )
    CUSTOMER_LIST_SECTION = (
        By.XPATH,
        "//*[self::h2 or self::h3][normalize-space()='Customer List']",
    )
    COMPANY_NAME_INPUT = (By.NAME, "company_name")
    CONTACT_PERSON_INPUT = (By.NAME, "contact_person_name")
    CONTACT_EMAIL_INPUT = (By.NAME, "contact_email")
    CONTACT_PHONE_INPUT = (By.NAME, "contact_phone")
    CREATE_BUTTON = (
        By.XPATH,
        "//button[@type='submit' and normalize-space()='Create Customer']",
    )
    SEARCH_INPUT = (By.XPATH, "//input[@name='search' and contains(@placeholder, 'Search company')]")
    SEARCH_BUTTON = (
        By.XPATH,
        "//input[@name='search']/ancestor::*[self::form or self::div][1]//button[@type='submit']",
    )
    CUSTOMER_TABLE = (By.CSS_SELECTOR, "table.dash-table")
    ALERTS = (
        By.XPATH,
        "//*[contains(@class,'alert') or contains(@class,'toast') or contains(normalize-space(.), 'created successfully')]",
    )

    FIELD_LOCATORS = {
        "company_name": COMPANY_NAME_INPUT,
        "contact_person_name": CONTACT_PERSON_INPUT,
        "contact_email": CONTACT_EMAIL_INPUT,
        "contact_phone": CONTACT_PHONE_INPUT,
    }

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(f"{Config.BASE_URL.rstrip('/')}{self.PAGE_PATH}")

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

    def _field(self, field_name):
        return self._visible(self.FIELD_LOCATORS[field_name])

    def _clear_and_type(self, locator, value):
        element = self._visible(locator)
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        if value:
            element.send_keys(value)
        return element

    def current_path(self):
        return urlparse(self.driver.current_url).path

    def page_contains_text(self, *needles):
        haystack = self.driver.page_source.lower()
        return any(needle.lower() in haystack for needle in needles if needle)

    def has_blocking_error(self):
        return self.page_contains_text("traceback", "internal server error", "server error")

    def is_page_displayed(self):
        current_path = self.current_path().rstrip("/")
        expected_path = self.PAGE_PATH.rstrip("/")
        return (
            self._is_visible(self.PAGE_HEADING)
            and self._is_visible(self.COMPANY_NAME_INPUT)
            and self._is_visible(self.CREATE_BUTTON)
            and current_path.endswith(expected_path)
            and not self.has_blocking_error()
        )

    def is_form_displayed(self):
        return all(
            self._is_visible(locator)
            for locator in (
                self.CUSTOMER_DETAILS_SECTION,
                self.COMPANY_NAME_INPUT,
                self.CONTACT_PERSON_INPUT,
                self.CONTACT_EMAIL_INPUT,
                self.CONTACT_PHONE_INPUT,
                self.CREATE_BUTTON,
            )
        )

    def is_list_displayed(self):
        return all(
            self._is_visible(locator)
            for locator in (
                self.CUSTOMER_LIST_SECTION,
                self.SEARCH_INPUT,
                self.CUSTOMER_TABLE,
            )
        )

    def get_heading_text(self):
        return self._visible(self.PAGE_HEADING).text.strip()

    def are_core_controls_displayed(self):
        return self.is_form_displayed() and self.is_list_displayed()

    def fill_field(self, field_name, value):
        self._clear_and_type(self.FIELD_LOCATORS[field_name], value)

    def fill_form(
        self,
        company_name="",
        contact_person_name="",
        contact_email="",
        contact_phone="",
    ):
        self.fill_field("company_name", company_name)
        self.fill_field("contact_person_name", contact_person_name)
        self.fill_field("contact_email", contact_email)
        self.fill_field("contact_phone", contact_phone)

    def submit(self):
        self._clickable(self.CREATE_BUTTON).click()

    def submit_with_data(self, **customer_data):
        self.fill_form(**customer_data)
        self.submit()

    def get_field_value(self, field_name):
        return self._field(field_name).get_attribute("value") or ""

    def get_field_placeholder(self, field_name):
        return self._field(field_name).get_attribute("placeholder") or ""

    def get_search_placeholder(self):
        return self._visible(self.SEARCH_INPUT).get_attribute("placeholder") or ""

    def get_native_validation_message(self, field_name):
        return self.driver.execute_script(
            "return arguments[0].validationMessage || '';",
            self._field(field_name),
        ).strip()

    def is_field_valid(self, field_name):
        return bool(
            self.driver.execute_script(
                "return arguments[0].checkValidity();",
                self._field(field_name),
            )
        )

    def get_alert_texts(self):
        texts = []
        for element in self.driver.find_elements(*self.ALERTS):
            try:
                if element.is_displayed():
                    text = " ".join(element.text.split()).strip()
                    if text and text not in texts:
                        texts.append(text)
            except Exception:
                continue
        return texts

    def get_success_feedback(self):
        texts = self.get_alert_texts()
        if texts:
            return " | ".join(texts)

        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        for keyword in ("created successfully", "customer created", "create customer"):
            if keyword in body_text.lower():
                return body_text
        return ""

    def search_customer(self, query):
        search_input = self._clear_and_type(self.SEARCH_INPUT, query)
        search_input.send_keys(Keys.TAB)
        self._clickable(self.SEARCH_BUTTON).click()

    def get_table_text(self):
        return " ".join(self._visible(self.CUSTOMER_TABLE).text.split())

    def is_customer_listed(self, company_name):
        return company_name.lower() in self.get_table_text().lower()

    def wait_for_customer_to_be_listed(self, company_name, timeout=12):
        WebDriverWait(self.driver, timeout).until(lambda _: self.is_customer_listed(company_name))
