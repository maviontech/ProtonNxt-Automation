from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.config import Config


class CreateJDPage:
    PAGE_PATH = "/jds/"
    VIEW_EDIT_PATH = "/view_edit_jds/"

    PAGE_HEADING = (
        By.XPATH,
        "//h2[normalize-space()='Create Job Description' or normalize-space()='Create New JD']",
    )
    FORM = (By.XPATH, "//form[.//*[@id='jd_summary'] and .//*[@id='jd_description']]")
    JD_SUMMARY_INPUT = (By.ID, "jd_summary")
    COMPANY_SEARCH_INPUT = (By.ID, "companySearch")
    COMPANY_ID_INPUT = (By.ID, "companyId")
    COMPANY_DROPDOWN = (By.ID, "companyDropdown")
    COMPANY_DROPDOWN_OPTIONS = (By.CSS_SELECTOR, "#companyDropdown .dropdown-option")
    JD_SPOC_NAME_INPUT = (By.ID, "jd_spoc_name")
    JD_SPOC_EMAIL_INPUT = (By.ID, "jd_spoc_email")
    JD_DESCRIPTION_TEXTAREA = (By.ID, "jd_description")
    FORMAT_PASTED_TEXT_BUTTON = (By.ID, "formatTextBtn")
    MUST_HAVE_SKILLS_TEXTAREA = (By.ID, "must_have_skills")
    GOOD_TO_HAVE_SKILLS_TEXTAREA = (By.ID, "good_to_have_skills")
    BUDGET_CTC_INPUT = (By.ID, "budget_ctc")
    EXPERIENCE_REQUIRED_INPUT = (By.ID, "experience_required")
    EDUCATION_REQUIRED_INPUT = (By.ID, "education_required")
    LOCATION_INPUT = (By.ID, "location")
    NO_OF_POSITIONS_INPUT = (By.ID, "no_of_positions")
    JD_STATUS_SELECT = (By.ID, "jd_status")
    SUBMIT_BUTTON = (
        By.XPATH,
        "//form[.//*[@id='jd_summary']]//button[@type='submit' and normalize-space()='Create JD']",
    )
    ALERTS = (By.CSS_SELECTOR, ".alert, .alert-success, .alert-danger, .toast, .invalid-feedback")

    VIEW_EDIT_LINK = (By.CSS_SELECTOR, "a[href='/view_edit_jds/']")
    JD_SEARCH_INPUT = (By.ID, "jd-search")
    JD_SEARCH_BUTTON = (By.ID, "jd-search-btn")
    UNWORKED_JDS_TABLE = (By.ID, "unworked-jds-table")
    UNWORKED_JDS_BODY = (By.ID, "unworked-jds-tbody")
    EDIT_BUTTON = (By.ID, "jd-edit-btn")

    FIELD_LOCATORS = {
        "jd_summary": JD_SUMMARY_INPUT,
        "jd_spoc_name": JD_SPOC_NAME_INPUT,
        "jd_spoc_email": JD_SPOC_EMAIL_INPUT,
        "jd_description": JD_DESCRIPTION_TEXTAREA,
        "must_have_skills": MUST_HAVE_SKILLS_TEXTAREA,
        "good_to_have_skills": GOOD_TO_HAVE_SKILLS_TEXTAREA,
        "budget_ctc": BUDGET_CTC_INPUT,
        "experience_required": EXPERIENCE_REQUIRED_INPUT,
        "education_required": EDUCATION_REQUIRED_INPUT,
        "location": LOCATION_INPUT,
        "no_of_positions": NO_OF_POSITIONS_INPUT,
        "jd_status": JD_STATUS_SELECT,
    }

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(f"{Config.BASE_URL.rstrip('/')}{self.PAGE_PATH}")

    def open_view_edit(self):
        self.driver.get(f"{Config.BASE_URL.rstrip('/')}{self.VIEW_EDIT_PATH}")

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
        if field_name == "jd_description":
            elements = self.driver.find_elements(*self.FIELD_LOCATORS[field_name])
            if not elements:
                raise TimeoutException("JD description backing field is not present on the page.")
            return elements[0]
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
        return self.page_contains_text("traceback", "internal server error", "server error", "exception")

    def is_page_displayed(self):
        current_path = self.current_path().rstrip("/")
        expected_path = self.PAGE_PATH.rstrip("/")
        return (
            self._is_visible(self.PAGE_HEADING)
            and self._is_visible(self.JD_SUMMARY_INPUT)
            and self._is_visible(self.SUBMIT_BUTTON)
            and current_path.endswith(expected_path)
            and not self.has_blocking_error()
        )

    def is_form_displayed(self):
        return self._is_visible(self.JD_SUMMARY_INPUT) and self._is_visible(self.SUBMIT_BUTTON)

    def get_heading_text(self):
        return self._visible(self.PAGE_HEADING).text.strip()

    def are_core_controls_displayed(self):
        visible_controls = (
            self.JD_SUMMARY_INPUT,
            self.COMPANY_SEARCH_INPUT,
            self.JD_SPOC_NAME_INPUT,
            self.JD_SPOC_EMAIL_INPUT,
            self.FORMAT_PASTED_TEXT_BUTTON,
            self.MUST_HAVE_SKILLS_TEXTAREA,
            self.GOOD_TO_HAVE_SKILLS_TEXTAREA,
            self.BUDGET_CTC_INPUT,
            self.EXPERIENCE_REQUIRED_INPUT,
            self.EDUCATION_REQUIRED_INPUT,
            self.LOCATION_INPUT,
            self.NO_OF_POSITIONS_INPUT,
            self.JD_STATUS_SELECT,
            self.SUBMIT_BUTTON,
        )
        description_present = bool(self.driver.find_elements(*self.JD_DESCRIPTION_TEXTAREA))
        return description_present and all(self._is_visible(locator) for locator in visible_controls)

    def enter_summary(self, value):
        self._clear_and_type(self.JD_SUMMARY_INPUT, value)

    def enter_spoc_name(self, value):
        self._clear_and_type(self.JD_SPOC_NAME_INPUT, value)

    def enter_spoc_email(self, value):
        self._clear_and_type(self.JD_SPOC_EMAIL_INPUT, value)

    def enter_description(self, value):
        field = self._field("jd_description")
        self.driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            field,
            value or "",
        )

    def get_description_value(self):
        return self._field("jd_description").get_attribute("value") or ""

    def format_pasted_text(self):
        try:
            self._clickable(self.FORMAT_PASTED_TEXT_BUTTON).click()
        except UnexpectedAlertPresentException:
            pass

    def accept_alert_if_present(self, timeout=2):
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        except TimeoutException:
            return ""
        text = alert.text.strip()
        alert.accept()
        return text

    def enter_must_have_skills(self, value):
        self._clear_and_type(self.MUST_HAVE_SKILLS_TEXTAREA, value)

    def enter_good_to_have_skills(self, value):
        self._clear_and_type(self.GOOD_TO_HAVE_SKILLS_TEXTAREA, value)

    def enter_budget(self, value):
        self._clear_and_type(self.BUDGET_CTC_INPUT, value)

    def enter_experience(self, value):
        self._clear_and_type(self.EXPERIENCE_REQUIRED_INPUT, value)

    def enter_education(self, value):
        self._clear_and_type(self.EDUCATION_REQUIRED_INPUT, value)

    def enter_location(self, value):
        self._clear_and_type(self.LOCATION_INPUT, value)

    def enter_positions(self, value):
        self._clear_and_type(self.NO_OF_POSITIONS_INPUT, str(value))

    def get_positions_value(self):
        return self._visible(self.NO_OF_POSITIONS_INPUT).get_attribute("value") or ""

    def get_positions_min(self):
        return self._visible(self.NO_OF_POSITIONS_INPUT).get_attribute("min") or ""

    def select_status(self, value=None, visible_text=None):
        select = Select(self._visible(self.JD_STATUS_SELECT))
        if value:
            select.select_by_value(value)
        elif visible_text:
            select.select_by_visible_text(visible_text)
        else:
            raise ValueError("Either value or visible_text must be provided to select_status().")

    def get_selected_status_value(self):
        return Select(self._visible(self.JD_STATUS_SELECT)).first_selected_option.get_attribute("value")

    def get_selected_status_text(self):
        return Select(self._visible(self.JD_STATUS_SELECT)).first_selected_option.text.strip()

    def get_status_options(self):
        select = Select(self._visible(self.JD_STATUS_SELECT))
        return [(option.get_attribute("value"), option.text.strip()) for option in select.options]

    def get_field_value(self, field_name):
        field = self._field(field_name)
        if field_name == "jd_status":
            return Select(field).first_selected_option.get_attribute("value")
        return field.get_attribute("value") or ""

    def get_field_attribute(self, field_name, attribute_name):
        return self._field(field_name).get_attribute(attribute_name)

    def get_native_validation_message(self, field_name):
        return self.driver.execute_script(
            "return arguments[0].validationMessage || '';",
            self._field(field_name),
        ).strip()

    def is_field_required(self, field_name):
        return self._field(field_name).get_attribute("required") is not None

    def is_field_valid(self, field_name):
        return bool(
            self.driver.execute_script(
                "return arguments[0].checkValidity();",
                self._field(field_name),
            )
        )

    def select_company(self, search_text="", exact_company=""):
        company_input = self._clear_and_type(self.COMPANY_SEARCH_INPUT, search_text or exact_company or "a")
        expected_text = exact_company.strip().lower()
        self.driver.execute_script(
            "arguments[0].classList.add('show');",
            self.driver.find_element(*self.COMPANY_DROPDOWN),
        )

        dropdown_options = self.driver.find_elements(*self.COMPANY_DROPDOWN_OPTIONS)
        for option in dropdown_options:
            try:
                text = (option.get_attribute("data-text") or option.text or "").strip()
                if not text:
                    continue
                if exact_company and text.lower() != expected_text:
                    continue
                if search_text and not exact_company and search_text.lower() not in text.lower():
                    continue

                option_value = option.get_attribute("data-value") or ""
                self.driver.execute_script(
                    """
                    const option = arguments[0];
                    const companyInput = arguments[1];
                    const companyIdInput = arguments[2];
                    const dropdown = arguments[3];
                    companyInput.value = option.getAttribute('data-text') || option.textContent.trim();
                    companyIdInput.value = option.getAttribute('data-value') || '';
                    companyInput.dispatchEvent(new Event('input', { bubbles: true }));
                    companyInput.dispatchEvent(new Event('change', { bubbles: true }));
                    companyIdInput.dispatchEvent(new Event('change', { bubbles: true }));
                    dropdown.classList.remove('show');
                    option.classList.add('selected');
                    """,
                    option,
                    company_input,
                    self.driver.find_element(*self.COMPANY_ID_INPUT),
                    self.driver.find_element(*self.COMPANY_DROPDOWN),
                )
                if option_value:
                    return self.wait_for_company_selection(exact_company or search_text)
            except StaleElementReferenceException:
                continue

        suggestion_locators = [
            (
                By.XPATH,
                f"//*[self::li or self::div or self::button or self::a][normalize-space()='{exact_company}']",
            )
            if exact_company
            else None,
            (
                By.XPATH,
                f"//*[self::li or self::div or self::button or self::a][contains(normalize-space(), '{search_text}')]",
            )
            if search_text
            else None,
            (By.XPATH, "//*[@role='option']"),
            (
                By.XPATH,
                "//*[contains(@class,'dropdown') or contains(@class,'suggest') or contains(@class,'autocomplete')]"
                "//*[self::li or self::div or self::button or self::a]",
            ),
        ]

        for locator in suggestion_locators:
            if locator is None:
                continue
            elements = self.driver.find_elements(*locator)
            for element in elements:
                try:
                    if not element.is_displayed():
                        continue
                    text = element.text.strip()
                    if exact_company and text.lower() != expected_text:
                        continue
                    try:
                        element.click()
                    except ElementClickInterceptedException:
                        self.driver.execute_script("arguments[0].click();", element)
                    return self.wait_for_company_selection(exact_company or search_text)
                except StaleElementReferenceException:
                    continue

        company_input.send_keys(Keys.ARROW_DOWN)
        company_input.send_keys(Keys.ENTER)
        return self.wait_for_company_selection(exact_company or search_text)

    def wait_for_company_selection(self, expected_company=""):
        self.wait.until(lambda _: bool(self.get_company_id()))
        self.wait.until(lambda _: bool(self.get_selected_company()))
        if expected_company:
            self.wait.until(
                lambda _: expected_company.lower() in self.get_selected_company().lower()
            )
        return self.get_selected_company()

    def get_selected_company(self):
        return self._visible(self.COMPANY_SEARCH_INPUT).get_attribute("value") or ""

    def get_company_id(self):
        return self.driver.find_element(*self.COMPANY_ID_INPUT).get_attribute("value") or ""

    def fill_form(
        self,
        jd_summary="",
        company_search="",
        expected_company="",
        jd_spoc_name="",
        jd_spoc_email="",
        jd_description="",
        must_have_skills="",
        good_to_have_skills="",
        budget_ctc="",
        experience_required="",
        education_required="",
        location="",
        no_of_positions="",
        jd_status=None,
    ):
        self.enter_summary(jd_summary)
        self.select_company(company_search, expected_company)
        self.enter_spoc_name(jd_spoc_name)
        self.enter_spoc_email(jd_spoc_email)
        self.enter_description(jd_description)
        self.enter_must_have_skills(must_have_skills)
        self.enter_good_to_have_skills(good_to_have_skills)
        self.enter_budget(budget_ctc)
        self.enter_experience(experience_required)
        self.enter_education(education_required)
        self.enter_location(location)
        if no_of_positions != "":
            self.enter_positions(no_of_positions)
        if jd_status:
            self.select_status(value=jd_status)

    def submit(self):
        self._clickable(self.SUBMIT_BUTTON).click()

    def submit_with_data(self, **jd_data):
        self.fill_form(**jd_data)
        self.submit()

    def get_alert_texts(self):
        return [
            element.text.strip()
            for element in self.driver.find_elements(*self.ALERTS)
            if element.is_displayed() and element.text.strip()
        ]

    def get_success_feedback(self):
        texts = self.get_alert_texts()
        if texts:
            return " | ".join(texts)

        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        for keyword in ("created successfully", "jd created", "job description created successfully"):
            if keyword in page_text.lower():
                return page_text
        return ""

    def get_validation_feedback(self):
        texts = self.get_alert_texts()
        if texts:
            return " | ".join(texts)
        return self.driver.find_element(By.TAG_NAME, "body").text

    def open_view_edit_from_navigation(self):
        try:
            self._clickable(self.VIEW_EDIT_LINK).click()
        except TimeoutException:
            self.open_view_edit()

    def is_view_edit_page_displayed(self):
        current_path = self.current_path().rstrip("/")
        expected_path = self.VIEW_EDIT_PATH.rstrip("/")
        return self._is_visible(self.JD_SEARCH_INPUT) and current_path.endswith(expected_path)

    def search_jd(self, query):
        search_input = self._clear_and_type(self.JD_SEARCH_INPUT, query)
        search_input.send_keys(Keys.TAB)
        self._clickable(self.JD_SEARCH_BUTTON).click()

    def is_jd_listed(self, title):
        title_lower = title.lower()
        rows = self.driver.find_elements(By.XPATH, f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"{title_lower}\")]")
        for row in rows:
            try:
                if row.is_displayed() and title_lower in row.text.lower():
                    return True
            except StaleElementReferenceException:
                continue
        return False

    def wait_for_jd_to_be_listed(self, title, timeout=12):
        WebDriverWait(self.driver, timeout).until(lambda _: self.is_jd_listed(title))

    def open_matching_jd_for_edit(self, title, timeout=8):
        self.search_jd(title)
        self.wait_for_jd_to_be_listed(title, timeout=timeout)

        title_lower = title.lower()
        clickable_locators = [
            (
                By.XPATH,
                f"//tr[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"{title_lower}\")]",
            ),
            (
                By.XPATH,
                f"//*[contains(@class,'card') and contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"{title_lower}\")]",
            ),
        ]

        for locator in clickable_locators:
            elements = self.driver.find_elements(*locator)
            for element in elements:
                try:
                    if not element.is_displayed():
                        continue
                    ActionChains(self.driver).move_to_element(element).click(element).perform()
                    try:
                        WebDriverWait(self.driver, 3).until(
                            lambda _: self._is_any_edit_field_visible()
                        )
                        return True
                    except TimeoutException:
                        continue
                except (StaleElementReferenceException, ElementClickInterceptedException):
                    continue

        if self._is_visible(self.EDIT_BUTTON):
            self._clickable(self.EDIT_BUTTON).click()
            try:
                WebDriverWait(self.driver, 3).until(lambda _: self._is_any_edit_field_visible())
                return True
            except TimeoutException:
                return False
        return False

    def _is_any_edit_field_visible(self):
        try:
            return any(
                self.driver.find_element(*locator).is_displayed()
                for locator in (
                    self.JD_SUMMARY_INPUT,
                    self.JD_SPOC_NAME_INPUT,
                    self.NO_OF_POSITIONS_INPUT,
                    self.JD_STATUS_SELECT,
                )
            )
        except Exception:
            return False
