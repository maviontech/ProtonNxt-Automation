import time
from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    NoAlertPresentException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.config import Config


class AssignJDToTeamPage:
    DEFAULT_PATHS = (
        "/assign_jd_page/",
        "/assign_jd/",
    )

    PAGE_MARKERS = (
        (By.ID, "jd-search-box"),
        (By.ID, "team-search-box"),
        (By.ID, "assignments-search"),
        (By.ID, "assign-btn"),
    )
    JD_SEARCH_LOCATORS = (
        (By.ID, "jd-search-box"),
        (By.ID, "jd-search"),
        (By.ID, "search-jd"),
        (By.NAME, "jd_search"),
        (
            By.XPATH,
            "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd') and "
            "contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'search')]",
        ),
        (By.XPATH, "//*[@id='jd-search' or @name='jd-search' or @name='search_jd']"),
    )
    TEAM_SEARCH_LOCATORS = (
        (By.ID, "team-search-box"),
        (By.ID, "team-search"),
        (By.ID, "search-team"),
        (By.NAME, "team_search"),
        (
            By.XPATH,
            "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'team') and "
            "contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'search')]",
        ),
        (By.XPATH, "//*[@id='team-search' or @name='team-search' or @name='search_team']"),
    )
    RECENT_SEARCH_LOCATORS = (
        (By.ID, "assignments-search"),
        (By.ID, "recent-assignment-search"),
        (By.ID, "assignment-search"),
        (By.NAME, "recent_assignment_search"),
        (
            By.XPATH,
            "//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'company') or "
            "contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'recent')]",
        ),
    )
    ASSIGN_BUTTON_LOCATORS = (
        (By.ID, "assign-btn"),
        (By.ID, "assign-jd-btn"),
        (
            By.XPATH,
            "//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'assign')]",
        ),
    )
    RESET_BUTTON_LOCATORS = (
        (By.ID, "reset-btn"),
        (By.ID, "assign-reset-btn"),
        (
            By.XPATH,
            "//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reset')]",
        ),
    )
    LIST_VIEW_BUTTONS = (
        (By.ID, "list-view-btn"),
        (
            By.XPATH,
            "//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'list')]",
        ),
    )
    CARD_VIEW_BUTTONS = (
        (By.ID, "cards-view-btn"),
        (
            By.XPATH,
            "//*[self::button or self::a][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cards')]",
        ),
    )
    ALERTS = (By.CSS_SELECTOR, ".alert, .alert-success, .alert-danger, .toast, .invalid-feedback")
    RESULT_BANNER = (By.ID, "assign-jd-result")
    JD_SELECT = (By.ID, "assign-jd-select")
    TEAM_SELECT = (By.ID, "assign-team-select")
    RECENT_TABLE = (
        By.XPATH,
        "//table[.//th[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd id')]]",
    )
    RECENT_HEADERS = (
        By.XPATH,
        "//table[.//th[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd id')]]//thead//th",
    )
    RECENT_ROWS = (
        By.XPATH,
        "//table[.//th[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'jd id')]]//tbody//tr[td]",
    )
    RECENT_CARDS = (
        By.XPATH,
        "//*[contains(@class,'card')][.//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'team')]]",
    )

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.last_alert_text = ""

    def open(self):
        paths = Config.ASSIGN_JD_TO_TEAM_SMOKE_TESTDATA.get("page_paths") or list(self.DEFAULT_PATHS)
        for path in paths:
            self.driver.get(f"{Config.BASE_URL.rstrip('/')}/{path.lstrip('/')}")
            if self._wait_for_known_page_markers():
                return
        self.driver.get(f"{Config.BASE_URL.rstrip('/')}/{paths[0].lstrip('/')}")

    def _wait_for_known_page_markers(self, timeout=4):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda _: self._find_first_visible(self.PAGE_MARKERS) is not None and not self.has_blocking_error()
            )
            return True
        except TimeoutException:
            return False

    def current_path(self):
        return urlparse(self.driver.current_url).path

    def _safe_is_displayed(self, element):
        try:
            return element.is_displayed()
        except StaleElementReferenceException:
            return False

    def _find_first_visible(self, locators):
        for locator in locators:
            for element in self.driver.find_elements(*locator):
                if self._safe_is_displayed(element):
                    return element
        return None

    def _find_all_visible(self, locator):
        return [element for element in self.driver.find_elements(*locator) if self._safe_is_displayed(element)]

    def _click(self, element):
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def _clear_and_type(self, element, value):
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        if value:
            element.send_keys(value)

    def _body_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text

    def page_contains_text(self, *needles):
        haystack = self.driver.page_source.lower()
        return any(needle.lower() in haystack for needle in needles if needle)

    def has_blocking_error(self):
        return self.page_contains_text("traceback", "internal server error", "server error", "exception")

    def is_page_displayed(self, quick=False):
        marker = self._find_first_visible(self.PAGE_MARKERS)
        has_core = marker is not None and not self.has_blocking_error()
        if quick:
            return has_core
        return has_core and self.are_major_sections_visible()

    def are_major_sections_visible(self):
        return all(
            self._find_first_visible(locators) is not None
            for locators in (self.JD_SEARCH_LOCATORS, self.TEAM_SEARCH_LOCATORS, self.RECENT_SEARCH_LOCATORS)
        ) and self._find_first_visible(self.ASSIGN_BUTTON_LOCATORS) is not None

    def _search_input(self, search_type):
        locator_map = {
            "jd": self.JD_SEARCH_LOCATORS,
            "team": self.TEAM_SEARCH_LOCATORS,
            "recent": self.RECENT_SEARCH_LOCATORS,
        }
        element = self._find_first_visible(locator_map[search_type])
        if element is None:
            raise NoSuchElementException(f"{search_type} search input is not available.")
        return element

    def search_jds(self, query):
        self._clear_and_type(self._search_input("jd"), query)
        self.wait_for_page_stable()

    def search_teams(self, query):
        self._clear_and_type(self._search_input("team"), query)
        self.wait_for_page_stable()

    def search_recent_assignments(self, query):
        self._clear_and_type(self._search_input("recent"), query)
        self.wait_for_page_stable()

    def get_search_value(self, search_type):
        return self._search_input(search_type).get_attribute("value") or ""

    def get_jd_items(self):
        try:
            return [option for option in Select(self.driver.find_element(*self.JD_SELECT)).options if self._normalized_text(option.text)]
        except Exception:
            return []

    def get_team_items(self):
        try:
            return [option for option in Select(self.driver.find_element(*self.TEAM_SELECT)).options if self._normalized_text(option.text)]
        except Exception:
            return []

    def get_jd_item_texts(self):
        return [self._normalized_text(item.text) for item in self.get_jd_items() if self._normalized_text(item.text)]

    def get_team_item_texts(self):
        return [self._normalized_text(item.text) for item in self.get_team_items() if self._normalized_text(item.text)]

    def _normalized_text(self, value):
        return " ".join((value or "").split()).strip()

    def _item_contains(self, item, text):
        return text.lower() in self._normalized_text(item.text).lower()

    def _select_item(self, items, query=""):
        target = None
        if query:
            for item in items:
                if self._item_contains(item, query):
                    target = item
                    break
        if target is None and items:
            target = items[0]
        if target is None:
            return None

        self.driver.execute_script("arguments[0].selected = true;", target)
        parent_select = target.find_element(By.XPATH, "./parent::select")
        self.driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            parent_select,
        )
        self.wait_for_page_stable()
        return target

    def select_jd(self, query=""):
        return self._select_item(self.get_jd_items(), query)

    def select_team(self, query=""):
        return self._select_item(self.get_team_items(), query)

    def _is_selected(self, item):
        try:
            return item.is_selected()
        except StaleElementReferenceException:
            return False

    def is_jd_selected(self, item):
        return self._is_selected(item)

    def is_team_selected(self, item):
        return self._is_selected(item)

    def has_jd_selection(self):
        return self._has_selection(self.JD_SELECT)

    def has_team_selection(self):
        return self._has_selection(self.TEAM_SELECT)

    def _has_selection(self, locator):
        try:
            select = Select(self.driver.find_element(*locator))
            selected = select.first_selected_option
            return selected.get_attribute("value") not in (None, "") and select.options.index(selected) > 0
        except Exception:
            return False

    def click_assign(self):
        button = self._find_first_visible(self.ASSIGN_BUTTON_LOCATORS)
        if button is None:
            raise NoSuchElementException("Assign button is not available.")
        self.last_alert_text = ""
        feedback_before_click = self._visible_feedback_text()
        self._click(button)
        self.last_alert_text = self._wait_for_operation_feedback(feedback_before_click)
        self.wait_for_page_stable()

    def click_reset(self):
        button = self._find_first_visible(self.RESET_BUTTON_LOCATORS)
        if button is None:
            raise NoSuchElementException("Reset button is not available.")
        self.last_alert_text = ""
        feedback_before_click = self._visible_feedback_text()
        self._click(button)
        self.last_alert_text = self._wait_for_operation_feedback(feedback_before_click, timeout=3)
        self.wait_for_page_stable()

    def wait_for_page_stable(self, timeout=8):
        WebDriverWait(self.driver, timeout).until(lambda _: not self.has_blocking_error())

    def get_feedback_text(self):
        if self.last_alert_text:
            return self.last_alert_text

        return self._visible_feedback_text()

    def _visible_feedback_text(self):
        banner = self.driver.find_elements(*self.RESULT_BANNER)
        for element in banner:
            if self._safe_is_displayed(element) and self._normalized_text(element.text):
                return self._normalized_text(element.text)

        for attempt in range(3):
            try:
                texts = [
                    self._normalized_text(element.text)
                    for element in self.driver.find_elements(*self.ALERTS)
                    if self._safe_is_displayed(element) and self._normalized_text(element.text)
                ]
                if texts:
                    return " | ".join(texts)
                return ""
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
        return ""

    def _wait_for_operation_feedback(self, feedback_before_click, timeout=10):
        """Wait for the alert, banner, or toast generated by an Assign/Reset action."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                alert = self.driver.switch_to.alert
                text = alert.text.strip()
                alert.accept()
                return text
            except NoAlertPresentException:
                pass

            visible_feedback = self._visible_feedback_text()
            if visible_feedback and visible_feedback != feedback_before_click:
                return visible_feedback
            time.sleep(0.1)
        return self._visible_feedback_text()

    def has_validation_message_for(self, subject):
        text = self.get_feedback_text().lower()
        checks = {
            "jd": ("select jd", "choose jd", "jd required"),
            "team": ("select team", "choose team", "team required"),
            "both": ("select jd", "select team", "required"),
        }
        return any(phrase in text for phrase in checks[subject])

    def get_recent_headers(self):
        return [self._normalized_text(element.text) for element in self.driver.find_elements(*self.RECENT_HEADERS) if self._normalized_text(element.text)]

    def get_recent_rows(self):
        rows = self._find_all_visible(self.RECENT_ROWS)
        return rows or self._find_all_visible(self.RECENT_CARDS)

    def get_recent_row_texts(self):
        return [self._normalized_text(row.text) for row in self.get_recent_rows() if self._normalized_text(row.text)]

    def get_recent_count(self):
        return len(self.get_recent_rows())

    def has_recent_assignments_section(self):
        return self._find_first_visible(self.RECENT_SEARCH_LOCATORS) is not None and (
            bool(self.driver.find_elements(*self.RECENT_TABLE)) or bool(self.get_recent_rows()) or self.page_contains_text("recent jd assignments")
        )

    def switch_recent_to_list(self):
        button = self._find_first_visible(self.LIST_VIEW_BUTTONS)
        if button is None:
            raise NoSuchElementException("List view button is not available.")
        self._click(button)
        WebDriverWait(self.driver, 8).until(lambda _: bool(self.driver.find_elements(*self.RECENT_TABLE)) or bool(self.get_recent_rows()))

    def switch_recent_to_cards(self):
        button = self._find_first_visible(self.CARD_VIEW_BUTTONS)
        if button is None:
            raise NoSuchElementException("Cards view button is not available.")
        self._click(button)
        WebDriverWait(self.driver, 8).until(lambda _: bool(self._find_all_visible(self.RECENT_CARDS)) or self.page_contains_text("card"))

    def has_no_results_state(self):
        return self.page_contains_text("no records", "no data", "not found", "no result", "no matching")

    def refresh(self):
        self.driver.refresh()
        self.wait_for_page_stable()
