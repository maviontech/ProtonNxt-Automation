from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class CreateTeamPage:
    """Page object for Teams > Create Team."""

    PAGE_PATH = "/create-team/"

    CREATE_TEAM_FORM = (By.ID, "create-team-form")
    TEAM_NAME_INPUT = (By.ID, "team_name")
    CREATE_TEAM_BUTTON = (By.CSS_SELECTOR, "#create-team-form button[type='submit']")
    MEMBER_SEARCH_INPUT = (By.ID, "member-search")
    MEMBER_TABLE = (By.ID, "members-table")
    MEMBER_ROWS = (By.CSS_SELECTOR, "#members-table tbody tr")
    FIRST_MEMBER_CHECKBOX_LABEL = (
        By.XPATH,
        "(//table[@id='members-table']//input[@name='members']/parent::label)[1]",
    )
    FIRST_TEAM_LEAD_RADIO_LABEL = (
        By.XPATH,
        "(//table[@id='members-table']//input[@name='team_lead']/parent::label)[1]",
    )
    TEAM_SEARCH_INPUT = (By.ID, "team-search")
    TEAMS_TABLE = (By.ID, "teams-table")
    TEAM_ROWS = (By.CSS_SELECTOR, "#teams-table tbody tr")

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
            self._is_visible(self.CREATE_TEAM_FORM)
            and self._is_visible(self.MEMBER_TABLE)
            and self._is_visible(self.TEAMS_TABLE)
            and self.current_path().rstrip("/").endswith(self.PAGE_PATH.rstrip("/"))
        )

    def is_team_name_required(self):
        return self._visible(self.TEAM_NAME_INPUT).get_attribute("required") is not None

    def get_team_name_maxlength(self):
        return self._visible(self.TEAM_NAME_INPUT).get_attribute("maxlength")

    def fill_team_name(self, team_name):
        team_name_input = self._visible(self.TEAM_NAME_INPUT)
        team_name_input.clear()
        if team_name:
            team_name_input.send_keys(team_name)

    def submit(self):
        self._clickable(self.CREATE_TEAM_BUTTON).click()

    def select_first_member(self):
        self._clickable(self.FIRST_MEMBER_CHECKBOX_LABEL).click()

    def select_first_team_lead(self):
        self._clickable(self.FIRST_TEAM_LEAD_RADIO_LABEL).click()

    def create_team(self, team_name):
        self.fill_team_name(team_name)
        self.select_first_member()
        self.select_first_team_lead()
        self.submit()

    def is_team_name_valid(self):
        return bool(
            self.driver.execute_script(
                "return arguments[0].checkValidity();", self._visible(self.TEAM_NAME_INPUT)
            )
        )

    def get_team_name_validation_message(self):
        return self.driver.execute_script(
            "return arguments[0].validationMessage || '';", self._visible(self.TEAM_NAME_INPUT)
        ).strip()

    def page_contains_text(self, text):
        return text.lower() in self.driver.page_source.lower()

    def wait_for_page_text(self, text):
        self.wait.until(lambda _: self.page_contains_text(text))

    def is_team_listed(self, team_name):
        return any(
            team_name.lower() in row.text.lower()
            for row in self.driver.find_elements(*self.TEAM_ROWS)
        )

    def search_members(self, query):
        search_input = self._visible(self.MEMBER_SEARCH_INPUT)
        search_input.click()
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(query)

    def get_member_search_value(self):
        return self._visible(self.MEMBER_SEARCH_INPUT).get_attribute("value")

    def search_teams(self, query):
        search_input = self._visible(self.TEAM_SEARCH_INPUT)
        search_input.click()
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(query)

    def get_team_search_value(self):
        return self._visible(self.TEAM_SEARCH_INPUT).get_attribute("value")
