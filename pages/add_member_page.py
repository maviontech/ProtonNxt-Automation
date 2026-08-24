from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class AddMemberPage:
    PAGE_PATH = "/teams/add-member/"

    FORM = (By.ID, "addMemberForm")
    VALIDATION_SUMMARY = (By.ID, "addMemberValidationSummary")

    FIRST_NAME_INPUT = (By.ID, "first_name")
    LAST_NAME_INPUT = (By.ID, "last_name")
    EMAIL_INPUT = (By.ID, "email")
    PHONE_INPUT = (By.ID, "phone")
    ROLE_INPUT = (By.ID, "role")
    DATE_JOINED_INPUT = (By.ID, "date_joined")
    STATUS_SELECT = (By.ID, "status")
    SUBMIT_BUTTON = (By.XPATH, "//form[@id='addMemberForm']//button[@type='submit']")

    FIELD_LOCATORS = {
        "first_name": FIRST_NAME_INPUT,
        "last_name": LAST_NAME_INPUT,
        "email": EMAIL_INPUT,
        "phone": PHONE_INPUT,
        "role": ROLE_INPUT,
        "date_joined": DATE_JOINED_INPUT,
        "status": STATUS_SELECT,
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

    def is_page_displayed(self):
        current_path = self.current_path().rstrip("/")
        expected_path = self.PAGE_PATH.rstrip("/")
        return self._is_visible(self.FORM) and current_path.endswith(expected_path)

    def current_path(self):
        return urlparse(self.driver.current_url).path

    def is_form_displayed(self):
        return self._is_visible(self.FORM)

    def is_submit_button_displayed(self):
        return self._is_visible(self.SUBMIT_BUTTON)

    def fill_field(self, field_name, value):
        field = self._field(field_name)
        if field_name == "status":
            Select(field).select_by_value(value)
            return

        field.clear()
        if value:
            field.send_keys(value)

    def fill_form(
        self,
        first_name="",
        last_name="",
        email="",
        phone="",
        role="",
        date_joined="",
        status=None,
    ):
        self.fill_field("first_name", first_name)
        self.fill_field("last_name", last_name)
        self.fill_field("email", email)
        self.fill_field("phone", phone)
        self.fill_field("role", role)
        self.fill_field("date_joined", date_joined)
        if status is not None:
            self.fill_field("status", status)

    def submit(self):
        self._clickable(self.SUBMIT_BUTTON).click()

    def submit_with_data(self, **member_data):
        self.fill_form(**member_data)
        self.submit()

    def get_field_value(self, field_name):
        field = self._field(field_name)
        if field_name == "status":
            return Select(field).first_selected_option.get_attribute("value")
        return field.get_attribute("value")

    def get_field_placeholder(self, field_name):
        return self._field(field_name).get_attribute("placeholder") or ""

    def get_field_attribute(self, field_name, attribute_name):
        return self._field(field_name).get_attribute(attribute_name)

    def get_status_options(self):
        select = Select(self._field("status"))
        return [(option.get_attribute("value"), option.text.strip()) for option in select.options]

    def is_field_required(self, field_name):
        return self._field(field_name).get_attribute("required") is not None

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

    def is_field_invalid(self, field_name):
        return not self.is_field_valid(field_name)

    def get_validation_summary_text(self):
        elements = self._present(self.VALIDATION_SUMMARY)
        if not elements:
            return ""
        return elements[0].text.strip()

    def is_validation_summary_visible(self):
        elements = self._present(self.VALIDATION_SUMMARY)
        if not elements:
            return False
        return elements[0].is_displayed() and not elements[0].get_attribute("hidden")

    def get_date_bounds(self):
        field = self._field("date_joined")
        return {
            "min": field.get_attribute("min") or "",
            "max": field.get_attribute("max") or "",
        }

    def has_success_feedback(self):
        page_text = self.driver.page_source.lower()
        success_keywords = (
            "success",
            "successfully",
            "member added",
            "team member added",
        )
        return any(keyword in page_text for keyword in success_keywords)
