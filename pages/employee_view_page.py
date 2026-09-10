from urllib.parse import urljoin, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class EmployeeViewPage:
    PATH = "/employee_view/"
    INPUT = (By.ID, "member-search-box")
    SEARCH = (By.ID, "search-btn")
    RESET = (By.ID, "reset-btn")
    OPTIONS = (By.CSS_SELECTOR, "#member-dropdown .ev-autocomplete-item")
    RESULT = (By.ID, "employee-result")
    ASSIGNED = (By.XPATH, "//*[@id='employee-result']/div[h3[starts-with(normalize-space(.), 'Assigned JDs')]]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def open(self):
        self.driver.get(urljoin(Config.BASE_URL, self.PATH))
        self.wait_ready()

    def open_from_menu(self):
        link = self.driver.find_element(By.CSS_SELECTOR, "a[href='/employee_view/']")
        if not link.is_displayed():
            self.driver.find_element(By.XPATH, "//button[contains(., 'Recruitment Tasks')]").click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/employee_view/']"))).click()
        self.wait_ready()

    def wait_ready(self):
        self.visible(self.INPUT)
        # The dropdown's initial member fetch must finish before typing.
        self.wait.until(lambda d: d.execute_script(
            "return performance.getEntriesByType('resource').some(e => "
            "new URL(e.name).pathname === '/employee_view_data/' && e.responseEnd > 0)"))
        assert urlparse(self.driver.current_url).path == self.PATH
        self.visible((By.XPATH, "//h1[contains(., 'Recruiter Assignment View')] | //h2[contains(., 'Recruiter Assignment View')]"))

    def type_query(self, query):
        field = self.visible(self.INPUT)
        field.send_keys(Keys.CONTROL, 'a')
        field.send_keys(Keys.BACKSPACE)
        if query:
            field.send_keys(query)

    def options(self):
        return [e for e in self.driver.find_elements(*self.OPTIONS) if e.is_displayed()]

    def search_member(self, query, member):
        self.type_query(query)
        expected = f"{member['name']} ({member['email']})"
        options = self.wait.until(lambda _: self.options())
        assert all(query.casefold() in e.text.casefold() for e in options), 'Unrelated search suggestions'
        matches = [e for e in options if e.text.strip().casefold() == expected.casefold()]
        assert len(matches) == 1, f'Expected exactly one suggestion for {expected}'
        matches[0].click()
        self.wait.until(EC.element_to_be_clickable(self.SEARCH)).click()
        self.wait.until(lambda _: self.member_details().get('Email') == member['email'])
        details = self.member_details()
        assert details.get('Name') == member['name']
        assert details.get('Email') == member['email']

    def member_details(self):
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#employee-result > .ev-section:first-child tr')
        result = {}
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) == 2:
                result[cells[0].text.strip()] = cells[1].text.strip()
        return result

    def result_text(self):
        return self.driver.find_element(*self.RESULT).text.strip()

    def reset(self):
        self.visible(self.RESET).click()
        self.wait.until(lambda _: not self.result_text())
        assert self.visible(self.INPUT).get_attribute('value') == ''
        assert not self.options()
        assert not self.visible(self.SEARCH).is_enabled()

    def assigned_jds(self):
        section = self.visible(self.ASSIGNED)
        result = []
        while True:
            for row in section.find_elements(By.CSS_SELECTOR, 'tbody tr'):
                cells = [c.text.strip() for c in row.find_elements(By.TAG_NAME, 'td')]
                assert len(cells) == 5
                result.append(dict(zip(('jd_id', 'summary', 'status', 'team', 'company'), cells)))
            buttons = section.find_elements(By.XPATH, ".//button[normalize-space(.)='Next']")
            if not buttons or not buttons[0].is_enabled():
                break
            old_row = section.find_element(By.CSS_SELECTOR, 'tbody tr')
            buttons[0].click()
            self.wait.until(EC.staleness_of(old_row))
        return result
