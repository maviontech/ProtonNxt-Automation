import re
from urllib.parse import urljoin, urlparse

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.config import Config


class PublicSubmissionsPage:
    """Selectors verified against the Public Submissions admin and careers forms."""

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout, ignored_exceptions=(StaleElementReferenceException,))

    def visible(self, element_id):
        for element in self.driver.find_elements(By.ID, element_id):
            try:
                if element.is_displayed():
                    return True
            except StaleElementReferenceException:
                # Successful submission replaces the form while we are polling.
                continue
        return False

    def element(self, element_id):
        return self.wait.until(EC.visibility_of_element_located((By.ID, element_id)))

    def click(self, element_id):
        self.wait.until(EC.element_to_be_clickable((By.ID, element_id))).click()

    def open(self, path="/public-submissions/admin/"):
        self.driver.get(urljoin(Config.BASE_URL, path))
        self.wait_ready()
        return self

    def wait_ready(self):
        self.element("ps-url-text")
        self.wait.until(lambda _: not self.visible("ps-url-spinner"))
        self.wait.until(lambda _: self.url or self.visible("ps-generate-btn"))
        text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "unable to load" not in text and "error loading status" not in text, text

    @property
    def url(self):
        value = self.element("ps-url-text").text.strip()
        parsed = urlparse(value)
        return value if parsed.scheme in ("http", "https") and parsed.netloc else ""

    @property
    def count(self):
        match = re.fullmatch(r"(\d+) submissions?", self.element("ps-count").text.strip())
        assert match, "Submission count is missing or invalid"
        return int(match[1])

    def confirmation(self, action):
        self.click(f"ps-{action}-btn")
        return self.wait.until(EC.alert_is_present())

    def generate(self):
        self.confirmation("generate").accept()
        return self.wait.until(lambda _: self.url)

    def revoke(self):
        self.confirmation("revoke").accept()
        self.wait.until(lambda _: not self.url and self.visible("ps-generate-btn"))

    def refresh(self):
        self.driver.refresh()
        self.wait_ready()

    def rows(self):
        return [row for row in self.driver.find_elements(By.CSS_SELECTOR, "#ps-submissions-tbody tr")
                if len(row.find_elements(By.TAG_NAME, "td")) >= 7]

    def row_values(self):
        return [[cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
                for row in self.rows()]

    def search(self, query):
        old = self.element("ps-submissions-tbody").find_element(By.TAG_NAME, "tr")
        field = self.element("ps-search")
        field.clear()
        field.send_keys(query)
        # Search is debounced and replaces the rows, including the empty-state row.
        self.wait.until(EC.staleness_of(old))

    def set_page_size(self, size):
        old = self.element("ps-submissions-tbody").find_element(By.TAG_NAME, "tr")
        Select(self.element("ps-pagesize-select")).select_by_value(str(size))
        self.wait.until(EC.staleness_of(old))

    def next_page(self):
        old = self.rows()[0]
        button = self.element("ps-page-next")
        assert button.is_enabled(), "Next page is unexpectedly disabled"
        button.click()
        self.wait.until(EC.staleness_of(old))

    def open_public(self, url):
        self.driver.get(url)
        self.element("ps-form")
        assert not self.visible("login-form"), "Public URL requires authentication"

    def submit_candidate(self, candidate, resume):
        for key in ("name", "email", "phone", "skills"):
            self.element(f"ps-{key}").send_keys(candidate[key])
        self.driver.find_element(By.ID, "ps-file-input").send_keys(str(resume.resolve()))
        self.click("ps-submit-btn")
        self.wait.until(lambda _: self.visible("ps-error") or any(
            e.is_displayed() for e in self.driver.find_elements(By.CSS_SELECTOR, ".ps-success")))
        assert not self.visible("ps-error"), self.element("ps-error").text if self.visible("ps-error") else ""
        success = self.driver.find_element(By.CSS_SELECTOR, ".ps-success")
        assert success.is_displayed() and success.text.strip(), "No submission success confirmation"

    def assert_revoked(self, url):
        self.driver.get(url)
        text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        assert any(word in text for word in ("revoked", "expired", "invalid", "not found", "no longer", "unavailable")), text
        assert not self.visible("ps-form") and not self.visible("ps-submit-btn"), "Revoked URL still accepts submissions"
