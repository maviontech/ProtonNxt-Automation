"""Recruiter Assignment View interactions; the application route is /employee_view/."""

from urllib.parse import urljoin, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class RecruiterAssignmentViewPage:
    PATH = '/employee_view/'
    INPUT = (By.ID, 'member-search-box')
    SEARCH = (By.ID, 'search-btn')
    RESET = (By.ID, 'reset-btn')
    RESULT = (By.ID, 'employee-result')
    OPTIONS = (By.CSS_SELECTOR, '#member-dropdown .ev-autocomplete-item')
    ASSIGNED = (By.XPATH, "//*[@id='employee-result']/div[h3[starts-with(normalize-space(.), 'Assigned JDs')]]")
    TEAMS = (By.XPATH, "//*[@id='employee-result']/div[h3[normalize-space(.)='Teams & JDs']]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def open(self, from_menu=False):
        if from_menu:
            locator = (By.CSS_SELECTOR, "a[href='/employee_view/']")
            if not self.driver.find_element(*locator).is_displayed():
                self.driver.find_element(By.XPATH, "//button[contains(., 'Recruitment Tasks')]").click()
            self.wait.until(EC.element_to_be_clickable(locator)).click()
        else:
            self.driver.get(urljoin(Config.BASE_URL, self.PATH))
        self.visible(self.INPUT)
        self.visible((By.XPATH, "//h1[contains(., 'Recruiter Assignment View')] | //h2[contains(., 'Recruiter Assignment View')]"))
        self.wait.until(lambda d: d.execute_script("""return performance.getEntriesByType('resource')
            .some(e => new URL(e.name).pathname === '/employee_view_data/' && e.responseEnd > 0)"""))
        assert urlparse(self.driver.current_url).path == self.PATH

    def type_query(self, query):
        field = self.visible(self.INPUT)
        field.send_keys(Keys.CONTROL, 'a')
        field.send_keys(Keys.BACKSPACE)
        if query:
            field.send_keys(query)

    def options(self):
        return [e for e in self.driver.find_elements(*self.OPTIONS) if e.is_displayed()]

    def select_member(self, query, member):
        self.type_query(query)
        expected = f"{member['name']} ({member['email']})".casefold()
        self.wait.until(lambda _: any(e.text.strip().casefold() == expected for e in self.options()),
                        f'No exact autocomplete identity for query {query!r}')
        matches = [e for e in self.options() if e.text.strip().casefold() == expected]
        assert len(matches) == 1, 'Duplicate member suggestions'
        matches[0].click()

    def search(self, query, member, enter=False):
        self.select_member(query, member)
        if enter:
            self.visible(self.INPUT).send_keys(Keys.ENTER)
        else:
            self.wait.until(EC.element_to_be_clickable(self.SEARCH)).click()
        self.wait.until(lambda _: self.member_details().get('Email') == member['email'],
                        'Search did not display the selected member')
        assert self.member_details()['Name'] == member['name']

    def member_details(self):
        result = {}
        for row in self.driver.find_elements(By.CSS_SELECTOR, '#employee-result > .ev-section:first-child tr'):
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

    def _all_rows(self, container, keys):
        result, seen_pages = [], set()
        while True:
            rows = container.find_elements(By.CSS_SELECTOR, 'tbody tr')
            values = [tuple(c.text.strip() for c in row.find_elements(By.TAG_NAME, 'td')) for row in rows]
            assert all(len(row) == len(keys) for row in values), 'Unexpected result table columns'
            fingerprint = tuple(values)
            assert fingerprint not in seen_pages, 'Pagination repeated a page'
            seen_pages.add(fingerprint)
            result.extend(dict(zip(keys, row)) for row in values)
            buttons = container.find_elements(By.XPATH, ".//button[normalize-space(.)='Next']")
            if not buttons or not buttons[0].is_enabled():
                return result
            assert rows, 'Next is enabled for an empty page'
            buttons[0].click()
            self.wait.until(EC.staleness_of(rows[0]))

    def assigned_jds(self):
        return self._all_rows(self.visible(self.ASSIGNED), ('jd_id', 'summary', 'status', 'team', 'company'))

    def teams(self):
        result = []
        section = self.visible(self.TEAMS)
        for heading in section.find_elements(By.CSS_SELECTOR, '.ev-team-header'):
            name = heading.text.strip()
            container = heading.find_element(By.XPATH, '..')
            result.append({'name': name, 'jds': self._all_rows(container, ('jd_id', 'summary', 'status', 'company'))})
        return result

    def read_members(self):
        result = self.driver.execute_async_script("""
            const done = arguments[arguments.length - 1];
            fetch('/employee_view_data/').then(r => {
                if (!r.ok) throw Error('Roster HTTP ' + r.status);
                return r.json();
            }).then(done).catch(e => done({error: String(e)}));
        """)
        assert 'error' not in result, result
        return result['members']

    def assert_matches(self, query, roster, minimum=1):
        term = query.strip().casefold()
        expected = sorted(f"{m['first_name']} {m['last_name']} ({m['email']})" for m in roster
                          if term in f"{m['first_name']} {m['last_name']}".casefold()
                          or term in m['email'].casefold())
        assert len(expected) >= minimum, f'Query must match at least {minimum} existing members'
        self.type_query(query)
        self.wait.until(lambda _: sorted(e.text.strip() for e in self.options()) == expected,
                        'Suggestions do not match the complete expected roster subset')
        assert len(expected) == len(set(expected)), 'Duplicate member identities'

    def request_count(self):
        return self.driver.execute_script("""return performance.getEntriesByType('resource')
            .filter(e => new URL(e.name).pathname === '/employee_view_report/').length""")

    def assert_no_server_error(self):
        body = self.driver.find_element(By.TAG_NAME, 'body').text.casefold()
        for message in ('internal server error', 'server error (500)', 'traceback (most recent call last)'):
            assert message not in body, f'Application error: {message}'

    def assert_layout(self):
        controls = [self.visible(loc) for loc in (self.INPUT, self.SEARCH, self.RESET)]
        result = self.visible(self.RESULT)
        errors = self.driver.execute_script("""
            const controls = arguments[0], result = arguments[1], errors = [];
            const width = document.documentElement.clientWidth;
            if (document.documentElement.scrollWidth > width + 1) errors.push('Page overflows horizontally');
            const rects = controls.map(e => e.getBoundingClientRect());
            [...rects, result.getBoundingClientRect()].forEach((r,i) => {
                if (r.width <= 0 || r.left < 0 || r.right > width + 1) errors.push('Element clipped: ' + i);
            });
            for (let i=0; i<rects.length; i++) for (let j=i+1; j<rects.length; j++) {
                const a=rects[i], b=rects[j];
                if (Math.min(a.right,b.right)>Math.max(a.left,b.left) &&
                    Math.min(a.bottom,b.bottom)>Math.max(a.top,b.top)) errors.push('Controls overlap');
            }
            return errors;
        """, controls, result)
        assert not errors, '; '.join(errors)
