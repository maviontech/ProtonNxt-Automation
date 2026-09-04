import re
from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class ViewEditJDsPage:
    PAGE_PATH = "/view_edit_jds/"

    SEARCH_INPUT = (By.ID, "jd-search")
    SEARCH_BUTTON = (By.ID, "jd-search-btn")
    LIST_VIEW_BUTTONS = (
        (By.ID, "list-view-btn"),
        (By.XPATH, "//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'list')]"),
    )
    CARD_VIEW_BUTTONS = (
        (By.ID, "cards-view-btn"),
        (By.XPATH, "//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cards')]"),
    )
    # The application renders a standard JD table, but its internal IDs are not
    # stable across builds. Anchor on the visible "JD ID" header instead.
    TABLE = (
        By.XPATH,
        "//table[.//th[contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd id')]]",
    )
    TABLE_HEADERS = (
        By.XPATH,
        "//table[.//th[contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd id')]]//thead//th",
    )
    TABLE_ROWS = (
        By.XPATH,
        "//table[.//th[contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd id')]]//tbody//tr[td]",
    )
    CARD_ITEMS = (
        By.XPATH,
        "//*[contains(@class,'card')][.//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd')]]",
    )
    PAGINATION_ROOT = (
        By.XPATH,
        "//*[contains(@class,'pagination') or @aria-label='Pagination' or contains(@class,'page-item')]",
    )
    PAGINATION_BUTTONS = (
        By.XPATH,
        "//*[contains(@class,'pagination') or @aria-label='Pagination']//*[self::a or self::button]",
    )
    DETAILS_MODAL = (
        By.XPATH,
        "//*[contains(@class,'modal') or contains(@class,'dialog')][.//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'job description') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd details')]]",
    )
    SHARE_DIALOG = (
        By.XPATH,
        "//*[contains(@class,'modal') or contains(@class,'dialog')][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'share')]",
    )

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.last_share_alert_text = ""

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

    def _click(self, element):
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def _clear_and_type(self, locator, value):
        element = self._visible(locator)
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        if value:
            element.send_keys(value)
        return element

    def _get_first_visible(self, locators):
        for locator in locators:
            elements = self.driver.find_elements(*locator)
            for element in elements:
                try:
                    if element.is_displayed():
                        return element
                except StaleElementReferenceException:
                    continue
        return None

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
        return self._is_visible(self.SEARCH_INPUT) and current_path.endswith(expected_path) and not self.has_blocking_error()

    def are_main_controls_displayed(self):
        has_search = self._is_visible(self.SEARCH_INPUT) and self._is_visible(self.SEARCH_BUTTON)
        has_toggle = bool(self._get_first_visible(self.LIST_VIEW_BUTTONS)) or bool(self._get_first_visible(self.CARD_VIEW_BUTTONS))
        has_results = self.is_results_section_displayed()
        has_pagination_or_results = self.has_pagination() or self.page_contains_text("showing", "no jd", "no records")
        return has_search and has_toggle and has_results and has_pagination_or_results

    def is_results_section_displayed(self):
        return self._is_visible(self.TABLE) or bool(self.get_card_items())

    def get_table_headers(self):
        return [element.text.strip() for element in self.driver.find_elements(*self.TABLE_HEADERS) if element.text.strip()]

    def get_table_rows(self):
        return [row for row in self.driver.find_elements(*self.TABLE_ROWS) if self._safe_is_displayed(row)]

    def get_card_items(self):
        return [card for card in self.driver.find_elements(*self.CARD_ITEMS) if self._safe_is_displayed(card)]

    def get_results_count(self):
        return len(self.get_table_rows()) or len(self.get_card_items())

    def get_visible_result_texts(self):
        texts = []
        for element in self.get_table_rows() or self.get_card_items():
            try:
                text = " ".join(element.text.split()).strip()
                if text:
                    texts.append(text)
            except StaleElementReferenceException:
                continue
        return texts

    def search(self, query):
        search_input = self._clear_and_type(self.SEARCH_INPUT, query)
        search_input.send_keys(Keys.TAB)
        self._clickable(self.SEARCH_BUTTON).click()
        self.wait_for_results_refresh()

    def wait_for_results_refresh(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda _: self._is_visible(self.SEARCH_INPUT) and not self.has_blocking_error()
        )

    def get_search_value(self):
        return self._visible(self.SEARCH_INPUT).get_attribute("value") or ""

    def find_matching_result(self, needle):
        needle_lower = needle.lower()
        for element in self.get_table_rows() or self.get_card_items():
            try:
                if needle_lower in element.text.lower():
                    return element
            except StaleElementReferenceException:
                continue
        return None

    def wait_for_matching_result(self, needle, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                lambda _: self.find_matching_result(needle) or False
            )
        except TimeoutException:
            return None

    def is_result_listed(self, needle):
        return self.find_matching_result(needle) is not None

    def get_first_result(self):
        results = self.get_table_rows() or self.get_card_items()
        return results[0] if results else None

    def get_result_details(self, element):
        text = " ".join((element.text or "").split()).strip()
        details = {
            "raw_text": text,
            "jd_id": self._extract_value(text, r"\bJD\d+\b"),
            "status": self._extract_labeled_value(text, ["status"]),
            "summary": self._extract_labeled_value(text, ["summary", "position summary", "job summary"]),
            "positions": self._extract_labeled_value(text, ["positions", "number of positions"]),
            "company": self._extract_labeled_value(text, ["company"]),
            "team": self._extract_labeled_value(text, ["team"]),
            "closure": self._extract_labeled_value(text, ["closure", "closure date"]),
        }
        if not details["summary"]:
            details["summary"] = text
        return details

    def get_no_results_message(self):
        candidates = [
            "no jd",
            "no records",
            "no data",
            "not found",
            "0 jds",
        ]
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        for phrase in candidates:
            if phrase in body_text:
                return phrase
        return ""

    def switch_to_cards(self):
        button = self._get_first_visible(self.CARD_VIEW_BUTTONS)
        if button is None:
            raise NoSuchElementException("Cards view control is not available.")
        self._click(button)
        WebDriverWait(self.driver, 8).until(lambda _: bool(self.get_card_items()) or self.page_contains_text("card"))

    def switch_to_list(self):
        button = self._get_first_visible(self.LIST_VIEW_BUTTONS)
        if button is None:
            raise NoSuchElementException("List view control is not available.")
        self._click(button)
        WebDriverWait(self.driver, 8).until(lambda _: self._is_visible(self.TABLE) or bool(self.get_table_rows()))

    def open_action_for_result(self, element, action_name):
        action_name = action_name.lower()
        action_locators = [
            (
                By.XPATH,
                f".//*[self::button or self::a or @role='button'][contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action_name}') or contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action_name}') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action_name}')]",
            ),
            (
                By.XPATH,
                f".//*[self::i or self::span][contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action_name}')]/ancestor::*[self::button or self::a][1]",
            ),
        ]
        for locator in action_locators:
            try:
                actions = element.find_elements(*locator)
            except StaleElementReferenceException:
                return False
            for action in actions:
                if not self._safe_is_displayed(action):
                    continue
                self._click(action)
                return True
        try:
            ActionChains(self.driver).move_to_element(element).perform()
        except Exception:
            pass
        return False

    def is_action_available_for_result(self, element, action_name):
        action_name = action_name.lower()
        locator = (
            By.XPATH,
            f".//*[self::button or self::a or @role='button'][contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action_name}') or contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action_name}') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action_name}')]",
        )
        for action in element.find_elements(*locator):
            if self._safe_is_displayed(action) and action.is_enabled():
                return True
        return False

    def open_view_for_result(self, element):
        if not self.open_action_for_result(element, "view"):
            return False
        WebDriverWait(self.driver, 8).until(lambda _: self.is_details_modal_displayed() or self.page_contains_text("job description"))
        return True

    def open_edit_for_result(self, element):
        if not self.open_action_for_result(element, "edit"):
            return False
        WebDriverWait(self.driver, 8).until(
            lambda _: self.page_contains_text("update jd", "save", "edit jd") or self.current_path().rstrip("/") != self.PAGE_PATH.rstrip("/")
        )
        return True

    def open_share_for_result(self, element):
        if not self.open_action_for_result(element, "share"):
            return False

        self.last_share_alert_text = self._accept_alert_if_present(timeout=3)
        if self.last_share_alert_text:
            return True

        WebDriverWait(self.driver, 8).until(self.is_share_dialog_displayed)
        return True

    def _accept_alert_if_present(self, timeout):
        try:
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        except TimeoutException:
            return ""

        message = alert.text.strip()
        alert.accept()
        return message

    def is_details_modal_displayed(self):
        return self._is_visible(self.DETAILS_MODAL)

    def is_share_dialog_displayed(self):
        return self._is_visible(self.SHARE_DIALOG)

    def get_details_modal_text(self):
        return " ".join(self._visible(self.DETAILS_MODAL).text.split())

    def is_view_mode_read_only(self):
        modal = self._visible(self.DETAILS_MODAL)
        fields = modal.find_elements(By.CSS_SELECTOR, "input, textarea, select")
        return not fields or all(not field.is_enabled() for field in fields)

    def is_close_control_displayed(self):
        modal = self._visible(self.DETAILS_MODAL)
        return any(
            self._safe_is_displayed(control)
            for control in modal.find_elements(
                By.XPATH,
                ".//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'close') or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'close')]",
            )
        )

    def close_details_modal(self):
        modal = self._visible(self.DETAILS_MODAL)
        controls = modal.find_elements(
            By.XPATH,
            ".//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'close') or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'close')]",
        )
        for control in controls:
            if self._safe_is_displayed(control):
                self._click(control)
                WebDriverWait(self.driver, 8).until(
                    lambda _: not any(self._safe_is_displayed(item) for item in self.driver.find_elements(*self.DETAILS_MODAL))
                )
                return True
        return False

    def get_details_modal_values(self):
        if not self.is_details_modal_displayed():
            return {}
        modal = self._visible(self.DETAILS_MODAL)
        lines = [line.strip() for line in modal.text.splitlines() if line.strip()]
        values = {}
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
            "jd id",
            "closure date",
        }
        index = 0
        while index < len(lines) - 1:
            label = lines[index].lower()
            if label in labels:
                values[label] = lines[index + 1]
                index += 2
                continue
            index += 1
        return values

    def has_pagination(self):
        return self._is_visible(self.PAGINATION_ROOT) or bool(self.driver.find_elements(*self.PAGINATION_BUTTONS))

    def get_active_page_number(self):
        candidates = self.driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'active') and (self::li or self::button or self::a)]",
        )
        for candidate in candidates:
            text = candidate.text.strip()
            if text.isdigit():
                return int(text)
        return 1

    def go_to_next_page(self):
        return self._click_pagination_control(["next", ">"])

    def go_to_previous_page(self):
        return self._click_pagination_control(["prev", "previous", "<"])

    def go_to_page_number(self, page_number):
        locator = (
            By.XPATH,
            f"//*[contains(@class,'pagination') or @aria-label='Pagination']//*[self::a or self::button][normalize-space()='{page_number}']",
        )
        try:
            button = self._clickable(locator)
        except TimeoutException:
            return False
        current_page = self.get_active_page_number()
        self._click(button)
        return self._wait_for_page_change(current_page)

    def get_pagination_summary(self):
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        match = re.search(r"Showing\s+(\d+)\s*[-to]+\s*(\d+)\s+of\s+(\d+)\s+JD", body_text, re.IGNORECASE)
        if not match:
            match = re.search(r"(\d+)\s*[-to]+\s*(\d+)\s+of\s+(\d+)\s+JD", body_text, re.IGNORECASE)
        if not match:
            return {}
        start, end, total = match.groups()
        return {"start": int(start), "end": int(end), "total": int(total)}

    def _click_pagination_control(self, labels):
        current_page = self.get_active_page_number()
        buttons = self.driver.find_elements(*self.PAGINATION_BUTTONS)
        for button in buttons:
            text = button.text.strip().lower()
            aria_label = (button.get_attribute("aria-label") or "").strip().lower()
            if any(label in text or label in aria_label for label in labels):
                if not self._safe_is_displayed(button):
                    continue
                disabled = (button.get_attribute("class") or "").lower()
                if "disabled" in disabled:
                    return False
                self._click(button)
                return self._wait_for_page_change(current_page)
        return False

    def _wait_for_page_change(self, current_page, timeout=8):
        try:
            WebDriverWait(self.driver, timeout).until(lambda _: self.get_active_page_number() != current_page)
            return True
        except TimeoutException:
            return False

    def _safe_is_displayed(self, element):
        try:
            return element.is_displayed()
        except StaleElementReferenceException:
            return False

    def _extract_value(self, text, pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else ""

    def _extract_labeled_value(self, text, labels):
        for label in labels:
            pattern = rf"{re.escape(label)}\s*[:\-]\s*([^|]+?)(?=\s+[A-Z][a-z]+\s*[:\-]|\s*\||$)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
