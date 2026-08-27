from urllib.parse import urlparse

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
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
    FIRST_TEAM_LEAD_RADIO = (
    By.XPATH,
    "(//table[@id='members-table']//input[@name='team_lead'])[1]",
)
    TEAM_SEARCH_INPUT = (By.ID, "team-search")
    TEAMS_TABLE = (By.ID, "teams-table")
    TEAM_ROWS = (By.CSS_SELECTOR, "#teams-table tbody tr")
    ALERTS = (By.CSS_SELECTOR, ".alert, .alert-danger, .alert-success, .toast, .invalid-feedback")

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
        self._clickable(self.FIRST_TEAM_LEAD_RADIO).click()

    def create_team(self, team_name):
        self.fill_team_name(team_name)
        self.select_first_member()
        self.select_first_team_lead()
        self.submit()

    def has_available_members(self):
        return self._any_displayed(self.MEMBER_ROWS)

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

    def wait_for_team_to_be_listed(self, team_name):
        self.wait.until(lambda _: self.is_team_listed(team_name))

    def is_team_listed(self, team_name):
        team_name_lower = team_name.lower()
        return any(team_name_lower in text.lower() for text in self._get_texts(self.TEAM_ROWS))

    def get_page_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text.strip()

    def get_alert_texts(self):
        visible_texts = []
        for text in self._get_texts(self.ALERTS, visible_only=True):
            stripped_text = text.strip()
            if stripped_text:
                visible_texts.append(stripped_text)
        return visible_texts

    def _any_displayed(self, locator, attempts=3):
        for attempt in range(attempts):
            try:
                return any(element.is_displayed() for element in self.driver.find_elements(*locator))
            except StaleElementReferenceException:
                if attempt == attempts - 1:
                    raise
        return False

    def _get_texts(self, locator, visible_only=False, attempts=3):
        for attempt in range(attempts):
            try:
                elements = self.driver.find_elements(*locator)
                texts = []
                for element in elements:
                    if visible_only and not element.is_displayed():
                        continue
                    texts.append(element.text)
                return texts
            except StaleElementReferenceException:
                if attempt == attempts - 1:
                    raise
        return []

    def wait_for_team_creation_result(self, team_name, success_keyword, timeout=8):
        short_wait = WebDriverWait(self.driver, timeout)

        def _result(_):
            if self.is_team_listed(team_name):
                return {"status": "success", "details": team_name}

            alerts = self.get_alert_texts()
            if alerts:
                joined_alerts = " | ".join(alerts)
                if success_keyword.lower() in joined_alerts.lower():
                    return {"status": "success", "details": joined_alerts}
                return {"status": "error", "details": joined_alerts}

            body_text = self.get_page_text()
            lowered_body = body_text.lower()
            if success_keyword.lower() in lowered_body:
                return {"status": "success", "details": body_text}
            if any(
                keyword in lowered_body
                for keyword in ("already exists", "select at least one member", "team lead must be selected", "error")
            ):
                return {"status": "error", "details": body_text}
            return False

        return short_wait.until(_result)

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
