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
    FORM = (
        By.XPATH,
        "//form[.//*[@id='jd_summary'] and .//*[@id='jd_description']]",
    )
    JD_SUMMARY_INPUT = (By.ID, "jd_summary")
    COMPANY_SEARCH_INPUT = (By.ID, "companySearch")
    COMPANY_ID_INPUT = (By.ID, "companyId")
    COMPANY_DROPDOWN = (By.ID, "companyDropdown")
    COMPANY_DROPDOWN_OPTIONS = (By.CSS_SELECTOR, "#companyDropdown .dropdown-option")
    JD_SPOC_NAME_INPUT = (By.ID, "jd_spoc_name")
    JD_SPOC_EMAIL_INPUT = (By.ID, "jd_spoc_email")
    JD_DESCRIPTION_TEXTAREA = (By.ID, "jd_description")
    JD_DESCRIPTION_EDITOR = (By.CSS_SELECTOR, "#jd_description_editor .ql-editor")
    JD_DESCRIPTION_TOOLBAR = (By.CSS_SELECTOR, "#jd_description_editor .ql-toolbar")
    JD_DESCRIPTION_BOLD_BUTTON = (By.CSS_SELECTOR, "#jd_description_editor .ql-bold")
    FORMAT_PASTED_TEXT_BUTTON = (By.ID, "formatTextBtn")
    MUST_HAVE_SKILLS_TEXTAREA = (By.ID, "must_have_skills")
    GOOD_TO_HAVE_SKILLS_TEXTAREA = (By.ID, "good_to_have_skills")
    BUDGET_CTC_INPUT = (By.ID, "budget_ctc")
    EXPERIENCE_REQUIRED_INPUT = (By.ID, "experience_required")
    EDUCATION_REQUIRED_INPUT = (By.ID, "education_required")
    LOCATION_INPUT = (By.ID, "location")
    CLOSURE_DATE_INPUT = (By.ID, "closure_date")
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
    EDIT_SAVE_BUTTON = (
        By.XPATH,
        "//*[contains(@class,'modal') or contains(@class,'dialog')]"
        "//*[self::button or @role='button'][@id='jd-save-btn' or normalize-space()='Save']",
    )
    DETAILS_MODAL = (
        By.XPATH,
        "//*[contains(@class,'modal') or contains(@class,'dialog')][.//*[normalize-space()='Job Description']]",
    )

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

    def _dispatch_input_events(self, element):
        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            """,
            element,
        )

    def _normalize_text(self, value):
        if value is None:
            return ""
        return " ".join(str(value).split()).strip()

    def _normalize_newlines(self, value):
        if value is None:
            return ""
        return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()

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
        backing_field = self._field("jd_description")
        editor = None
        if self._is_visible(self.JD_DESCRIPTION_EDITOR):
            editor = self._visible(self.JD_DESCRIPTION_EDITOR)

        target = editor or backing_field
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
            self.driver.execute_script("arguments[0].click();", target)
        except Exception:
            pass

        try:
            target.send_keys(Keys.CONTROL, "a")
            target.send_keys(Keys.BACKSPACE)
        except Exception:
            self.driver.execute_script("arguments[0].value = '';", backing_field)
            if editor is not None:
                self.driver.execute_script("arguments[0].innerText = '';", editor)

        if value:
            typed = False
            try:
                target.send_keys(value)
                typed = True
            except Exception:
                typed = False

            if not typed:
                if editor is not None:
                    self.driver.execute_script("arguments[0].innerText = arguments[1];", editor, value)
                self.driver.execute_script("arguments[0].value = arguments[1];", backing_field, value)
            else:
                self.driver.execute_script("arguments[0].value = arguments[1];", backing_field, value)

        if editor is not None:
            self._dispatch_input_events(editor)
        self._dispatch_input_events(backing_field)
        expected_value = self._normalize_text(value)
        self.wait.until(
            lambda _: expected_value in self._normalize_text(self.get_description_value())
            if expected_value
            else self._normalize_text(self.get_description_value()) == ""
        )

    def get_description_value(self):
        raw_value = self._field("jd_description").get_attribute("value") or ""
        if raw_value.strip():
            return raw_value
        if self._is_visible(self.JD_DESCRIPTION_EDITOR):
            return self._visible(self.JD_DESCRIPTION_EDITOR).text.strip()
        return raw_value

    def get_description_html(self):
        if self._is_visible(self.JD_DESCRIPTION_EDITOR):
            return self.driver.execute_script("return arguments[0].innerHTML || '';", self._visible(self.JD_DESCRIPTION_EDITOR))
        return ""

    def _select_all_description_text(self):
        editor = self._visible(self.JD_DESCRIPTION_EDITOR)
        try:
            editor.click()
            editor.send_keys(Keys.CONTROL, "a")
        except Exception:
            self.driver.execute_script(
                """
                const editor = arguments[0];
                const selection = window.getSelection();
                const range = document.createRange();
                range.selectNodeContents(editor);
                selection.removeAllRanges();
                selection.addRange(range);
                """,
                editor,
            )
        return editor

    def has_description_content(self, expected_text=""):
        current_value = self._normalize_text(self.get_description_value())
        if not current_value:
            return False
        expected_value = self._normalize_text(expected_text)
        if not expected_value:
            return True
        expected_words = [word for word in expected_value.split() if len(word) > 2]
        if not expected_words:
            return True
        matched_words = sum(1 for word in expected_words if word in current_value)
        return matched_words >= max(1, min(3, len(expected_words)))

    def apply_basic_description_formatting(self, format_name="bold"):
        if format_name != "bold":
            raise ValueError(f"Unsupported description format: {format_name}")

        editor = self._select_all_description_text()
        toolbar_button = self._clickable(self.JD_DESCRIPTION_BOLD_BUTTON)
        before_html = self.get_description_html().lower()

        try:
            toolbar_button.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", toolbar_button)

        def bold_applied(_):
            html_value = self.get_description_html().lower()
            button_classes = (toolbar_button.get_attribute("class") or "").lower()
            aria_pressed = (toolbar_button.get_attribute("aria-pressed") or "").lower()
            return (
                html_value != before_html
                or "<strong" in html_value
                or "<b>" in html_value
                or 'font-weight: bold' in html_value
                or "ql-active" in button_classes
                or aria_pressed == "true"
            )

        self.wait.until(bold_applied)
        editor.click()

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

    def enter_closure_date(self, value):
        field = self._visible(self.CLOSURE_DATE_INPUT)
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true})); arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            field,
            value,
        )

    def enable_edit_mode(self):
        self._clickable(self.EDIT_BUTTON).click()
        self.wait.until(lambda _: self._visible(self.LOCATION_INPUT).is_enabled())

    def save_edit(self):
        self._clickable(self.EDIT_SAVE_BUTTON).click()
        alert = WebDriverWait(self.driver, 8).until(EC.alert_is_present())
        message = alert.text.strip()
        alert.accept()
        return message

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
        if self.is_details_modal_displayed():
            return self.get_details_modal_values().get("status", "").lower()
        return Select(self._visible(self.JD_STATUS_SELECT)).first_selected_option.get_attribute("value")

    def get_selected_status_text(self):
        return Select(self._visible(self.JD_STATUS_SELECT)).first_selected_option.text.strip()

    def get_status_options(self):
        select = Select(self._visible(self.JD_STATUS_SELECT))
        return [(option.get_attribute("value"), option.text.strip()) for option in select.options]

    def get_field_value(self, field_name):
        if self.is_details_modal_displayed():
            modal_values = self.get_details_modal_values()
            modal_field_map = {
                "jd_summary": "position summary",
                "jd_description": "job description",
                "must_have_skills": "required skills",
                "good_to_have_skills": "preferred skills",
                "experience_required": "experience required",
                "education_required": "education required",
                "budget_ctc": "budget/ctc",
                "location": "location",
                "no_of_positions": "number of positions",
                "jd_status": "status",
            }
            modal_key = modal_field_map.get(field_name)
            if modal_key is not None:
                return modal_values.get(modal_key, "")

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
            self.wait.until(lambda _: expected_company.lower() in self.get_selected_company().lower())
        return self.get_selected_company()

    def get_selected_company(self):
        return self._visible(self.COMPANY_SEARCH_INPUT).get_attribute("value") or ""

    def get_company_id(self):
        return self.driver.find_element(*self.COMPANY_ID_INPUT).get_attribute("value") or ""

    def clear_company(self):
        company_input = self._visible(self.COMPANY_SEARCH_INPUT)
        company_input.click()
        company_input.send_keys(Keys.CONTROL, "a")
        company_input.send_keys(Keys.BACKSPACE)
        company_id = self.driver.find_element(*self.COMPANY_ID_INPUT)
        self.driver.execute_script(
            """
            arguments[0].value = '';
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[1].value = '';
            arguments[1].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            company_input,
            company_id,
        )

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
        self._assert_required_fields_ready(jd_summary=jd_summary, jd_description=jd_description)

    def submit(self):
        self._clickable(self.SUBMIT_BUTTON).click()

    def _assert_required_fields_ready(self, jd_summary="", jd_description=""):
        if jd_summary:
            self.wait.until(lambda _: self.get_field_value("jd_summary").strip() == jd_summary.strip())
        if jd_description:
            self.wait.until(lambda _: self.has_description_content(jd_description))

    def submit_with_data(self, **jd_data):
        jd_summary = (jd_data.get("jd_summary") or "").strip()
        self.fill_form(**jd_data)
        self.submit()
        self.wait_for_submission_success(jd_summary=jd_summary)

    def wait_for_submission_success(self, jd_summary="", timeout=20):
        expected_summary = jd_summary.strip().lower()

        def submission_completed(_):
            current_path = self.current_path().rstrip("/")
            if current_path.endswith(self.VIEW_EDIT_PATH.rstrip("/")):
                return True

            feedback = self.get_success_feedback().lower()
            if any(keyword in feedback for keyword in ("created successfully", "jd created", "job description created successfully")):
                return True

            if expected_summary and self._is_visible(self.JD_SUMMARY_INPUT):
                current_value = (self._field("jd_summary").get_attribute("value") or "").strip().lower()
                if current_value != expected_summary:
                    return True

            return False

        WebDriverWait(self.driver, timeout).until(submission_completed)

    def get_alert_texts(self):
        for attempt in range(3):
            try:
                return [
                    element.text.strip()
                    for element in self.driver.find_elements(*self.ALERTS)
                    if element.is_displayed() and element.text.strip()
                ]
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
        return []

    def get_success_feedback(self):
        texts = self.get_alert_texts()
        if texts:
            return " | ".join(texts)

        page_text = self._get_body_text()
        for keyword in ("created successfully", "jd created", "job description created successfully"):
            if keyword in page_text.lower():
                return page_text
        return ""

    def get_validation_feedback(self):
        texts = self.get_alert_texts()
        if texts:
            return " | ".join(texts)
        return self._get_body_text()

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

    def count_listed_jds(self, title):
        title_lower = title.lower()
        rows = self.driver.find_elements(
            By.XPATH,
            f"//tr[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"{title_lower}\")]",
        )
        return sum(
            1
            for row in rows
            if self._element_contains_title(row, title_lower)
        )

    @staticmethod
    def _element_contains_title(element, title_lower):
        try:
            return element.is_displayed() and title_lower in element.text.lower()
        except StaleElementReferenceException:
            return False

    def is_jd_listed(self, title):
        title_lower = title.lower()
        rows = self.driver.find_elements(
            By.XPATH,
            f"//tr[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"{title_lower}\")]",
        )
        for row in rows:
            try:
                if self._element_contains_title(row, title_lower):
                    return True
            except StaleElementReferenceException:
                continue
        return False

    def wait_for_jd_to_be_listed(self, title, timeout=25):
        def jd_is_listed(_):
            self.search_jd(title)
            return self.is_jd_listed(title)

        WebDriverWait(self.driver, timeout).until(jd_is_listed)

    def open_matching_jd_for_edit(self, title, timeout=8):
        self.search_jd(title)
        self.wait_for_jd_to_be_listed(title, timeout=timeout)

        title_lower = title.lower()
        row_locators = [
            (
                By.XPATH,
                f"//tr[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"{title_lower}\")]",
            ),
            (
                By.XPATH,
                f"//*[contains(@class,'card') and contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"{title_lower}\")]",
            ),
        ]

        for locator in row_locators:
            elements = self.driver.find_elements(*locator)
            for element in elements:
                if not self._open_matching_result_element(element):
                    continue
                try:
                    WebDriverWait(self.driver, 3).until(
                        lambda _: self._is_any_edit_field_visible() or self.is_details_modal_displayed()
                    )
                    return True
                except TimeoutException:
                    continue

        if self._is_visible(self.EDIT_BUTTON):
            self._clickable(self.EDIT_BUTTON).click()
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda _: self._is_any_edit_field_visible() or self.is_details_modal_displayed()
                )
                return True
            except TimeoutException:
                return False
        return False

    def is_details_modal_displayed(self):
        return self._is_visible(self.DETAILS_MODAL)

    def get_details_modal_values(self):
        if not self.is_details_modal_displayed():
            return {}

        modal = self._visible(self.DETAILS_MODAL)
        lines = [line.strip() for line in modal.text.splitlines() if line.strip()]
        values = {}
        i = 0
        labels = {
            "position summary",
            "job description",
            "required skills",
            "preferred skills",
            "experience required",
            "education required",
            "budget/ctc",
            "location",
            "number of positions",
            "status",
            "company",
            "team",
        }

        while i < len(lines) - 1:
            label = lines[i].lower()
            if label in labels:
                values[label] = lines[i + 1]
                i += 2
                continue
            i += 1

        return values

    def _open_matching_result_element(self, element):
        try:
            if not element.is_displayed():
                return False
        except StaleElementReferenceException:
            return False

        action_locators = [
            (By.XPATH, ".//button"),
            (By.XPATH, ".//a"),
            (
                By.XPATH,
                ".//*[self::button or self::a or @role='button'][contains(@id, 'edit') or contains(@class, 'edit')]",
            ),
            (
                By.XPATH,
                ".//*[self::button or self::a or @role='button'][contains(@href, 'edit') or contains(@onclick, 'edit')]",
            ),
        ]

        for locator in action_locators:
            try:
                actions = element.find_elements(*locator)
            except StaleElementReferenceException:
                return False
            for action in actions:
                if not self._click_result_action(action):
                    continue
                return True

        try:
            ActionChains(self.driver).move_to_element(element).click(element).perform()
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException):
            return False

    def _click_result_action(self, action):
        try:
            if not action.is_displayed() or not action.is_enabled():
                return False
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", action)
            try:
                action.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", action)
            return True
        except StaleElementReferenceException:
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

    def _get_body_text(self, attempts=3):
        for attempt in range(attempts):
            try:
                return self.driver.find_element(By.TAG_NAME, "body").text
            except StaleElementReferenceException:
                if attempt == attempts - 1:
                    raise
        return ""
