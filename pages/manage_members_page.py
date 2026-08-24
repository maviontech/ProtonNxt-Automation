from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class ManageMembersPage:
    """Page object for Teams > View Members."""

    PAGE_PATH = "/teams/manage_members/"

    PAGE_TITLE = (
        By.XPATH,
        "//*[self::h1 or self::h2 or self::h3 or self::div][normalize-space()='Manage Members']",
    )
    GLOBAL_SEARCH_INPUT = (
        By.XPATH,
        "//input[contains(@placeholder, 'Search candidates') and not(contains(@placeholder, 'name or email'))]",
    )
    SEARCH_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Search by name or email')]")
    MEMBER_TABLE = (By.XPATH, "//table[.//th[contains(normalize-space(.), 'Member Name')]]")
    TABLE_HEADERS = (By.XPATH, "//table//thead//th")
    MEMBER_ROWS = (By.XPATH, "//table//tbody/tr[not(@hidden)]")
    LIST_VIEW_BUTTON = (By.XPATH, "//button[normalize-space()='List']")
    CARD_VIEW_BUTTON = (By.XPATH, "//button[normalize-space()='Cards']")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(f"{Config.BASE_URL.rstrip('/')}{self.PAGE_PATH}")

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

    def current_path(self):
        return urlparse(self.driver.current_url).path

    def is_page_displayed(self):
        return (
            self._is_visible(self.PAGE_TITLE)
            and self._is_visible(self.SEARCH_INPUT)
            and self.current_path().rstrip("/").endswith(self.PAGE_PATH.rstrip("/"))
        )

    def is_member_table_displayed(self):
        return self._is_visible(self.MEMBER_TABLE)

    def get_table_headers(self):
        return [header.text.strip() for header in self.driver.find_elements(*self.TABLE_HEADERS)]

    def get_visible_member_rows(self):
        return [
            row for row in self.driver.find_elements(*self.MEMBER_ROWS) if row.is_displayed()
        ]

    def get_visible_member_row_texts(self):
        return [row.text.strip() for row in self.get_visible_member_rows() if row.text.strip()]

    def get_first_member_name(self):
        rows = self.get_visible_member_rows()
        if not rows:
            return ""

        cells = rows[0].find_elements(By.CSS_SELECTOR, "td")
        if len(cells) < 2:
            return ""
        return cells[1].text.strip()

    def search(self, value):
        search_input = self._visible(self.SEARCH_INPUT)
        search_input.click()
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(value)

    def get_member_search_value(self):
        return self._visible(self.SEARCH_INPUT).get_attribute("value")

    def search_globally(self, value):
        global_search_input = self._visible(self.GLOBAL_SEARCH_INPUT)
        global_search_input.click()
        global_search_input.send_keys(Keys.CONTROL, "a")
        global_search_input.send_keys(value)

    def get_global_search_value(self):
        return self._visible(self.GLOBAL_SEARCH_INPUT).get_attribute("value")

    def switch_to_cards(self):
        self._clickable(self.CARD_VIEW_BUTTON).click()

    def switch_to_list(self):
        self._clickable(self.LIST_VIEW_BUTTON).click()
