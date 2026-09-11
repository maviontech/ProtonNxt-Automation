from pathlib import Path
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import Config


class TalentIntakeMatchingPage:
    """Controls for the Talent Intake & Matching page."""

    PATH = '/view_parse_resumes_page/'
    JD_SEARCH = (By.ID, 'jd-search')
    JD_OPTIONS = (By.CSS_SELECTOR, '#jd-dropdown .jd-dropdown-option[data-value]:not([data-value=""])')
    SELECTED_JD = (By.ID, 'jd-select')
    UPLOAD = (By.ID, 'upload-btn')
    EXPORT = (By.ID, 'export-btn')
    TABLE = (By.ID, 'resume-table')
    TABLE_BODY = (By.ID, 'resumes-tbody')
    CARDS = (By.ID, 'resumes-cards')
    UPLOAD_MODAL = (By.ID, 'resume-upload-modal')
    UPLOAD_CLOSE = (By.ID, 'upload-close-btn')
    UPLOAD_SAVE = (By.ID, 'upload-save-btn')
    RESUME_FILE = (By.ID, 'resume-file')
    ZIP_FILE = (By.ID, 'resume-zip-file')
    EXISTING_SEARCH = (By.ID, 'existing-candidate-search')
    UPLOAD_MESSAGE = (By.ID, 'upload-message')
    ACTION_RESULT = (By.ID, 'action-result-modal')
    ACTION_MESSAGE = (By.ID, 'action-result-message')
    ACTION_CLOSE = (By.ID, 'action-result-close-btn')

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self):
        self.driver.get(urljoin(Config.BASE_URL, self.PATH))
        self.wait_ready()
        return self

    def wait_ready(self):
        self.wait.until(EC.visibility_of_element_located(self.JD_SEARCH))
        self.wait.until(EC.element_to_be_clickable(self.UPLOAD))
        self.wait.until(EC.visibility_of_element_located(self.TABLE))
        assert self.PATH in self.driver.current_url

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def jd_options(self):
        return [option for option in self.driver.find_elements(*self.JD_OPTIONS) if option.is_displayed()]

    def open_jd_picker(self):
        self.visible(self.JD_SEARCH).click()
        return self.wait.until(lambda _: self.jd_options())

    def select_jd(self, query=None, index=0):
        field = self.visible(self.JD_SEARCH)
        field.click()
        field.send_keys(Keys.CONTROL, 'a')
        field.send_keys(Keys.BACKSPACE)
        if query:
            field.send_keys(query)
        options = self.wait.until(lambda _: self.jd_options())
        option = options[index]
        label = option.get_attribute('title') or option.text
        option.click()
        self.wait.until(lambda _: self.driver.find_element(*self.SELECTED_JD).get_attribute('value'))
        self.wait.until(lambda _: field.get_attribute('value').strip())
        return label, self.driver.find_element(*self.SELECTED_JD).get_attribute('value')

    def clear_jd(self):
        field = self.visible(self.JD_SEARCH)
        field.click()
        field.send_keys(Keys.CONTROL, 'a')
        field.send_keys(Keys.BACKSPACE)
        self.wait.until(lambda _: self.jd_options())
        self.driver.find_element(By.CSS_SELECTOR, '#jd-dropdown .jd-dropdown-option[data-value=""]').click()
        self.wait.until(lambda _: not self.driver.find_element(*self.SELECTED_JD).get_attribute('value'))

    @property
    def selected_jd_id(self):
        return self.driver.find_element(*self.SELECTED_JD).get_attribute('value')

    def open_upload(self):
        self.click(self.UPLOAD)
        # Selecting no JD shows the shared result dialog instead of the upload modal.
        return self.wait.until(lambda _: self.is_visible(self.UPLOAD_MODAL) or self.is_visible(self.ACTION_RESULT))

    def close_action_result(self):
        if self.is_visible(self.ACTION_RESULT):
            self.click(self.ACTION_CLOSE)
            self.wait.until(lambda _: not self.is_visible(self.ACTION_RESULT))

    def close_upload(self):
        self.click(self.UPLOAD_CLOSE)
        self.wait.until(lambda _: not self.is_visible(self.UPLOAD_MODAL))

    def is_visible(self, locator):
        elements = self.driver.find_elements(*locator)
        return bool(elements and elements[0].is_displayed())

    def choose_upload_tab(self, label):
        button = self.wait.until(lambda d: next((item for item in d.find_elements(
            By.CSS_SELECTOR, '#resume-upload-modal .upload-tab-btn')
            if item.is_displayed() and item.text.strip().casefold() == label.casefold()), False))
        button.click()

    def choose_upload_source(self, label):
        button = self.wait.until(lambda d: next((item for item in d.find_elements(
            By.CSS_SELECTOR, '#resume-upload-modal .upload-source-btn')
            if item.is_displayed() and item.text.strip().casefold() == label.casefold()), False))
        button.click()

    def upload_file(self, file_path, zip_archive=False):
        locator = self.ZIP_FILE if zip_archive else self.RESUME_FILE
        # The native file controls are intentionally hidden behind the drop zone.
        # Selenium can attach a file to a hidden <input type=file>; waiting for
        # visibility here incorrectly times out before the upload begins.
        file_input = self.wait.until(EC.presence_of_element_located(locator))
        file_input.send_keys(str(Path(file_path).resolve()))
        self.click(self.UPLOAD_SAVE)
        self.wait.until(lambda _: self.is_visible(self.UPLOAD_MESSAGE) or self.is_visible(self.ACTION_RESULT))

    def upload_message(self):
        text = ' '.join(element.text for element in self.driver.find_elements(*self.UPLOAD_MESSAGE) if element.is_displayed())
        if not text and self.is_visible(self.ACTION_RESULT):
            text = self.visible(self.ACTION_MESSAGE).text
        return text.strip()

    def rows(self):
        return [row for row in self.driver.find_elements(By.CSS_SELECTOR, '#resumes-tbody tr') if row.is_displayed()]

    def view_toggle(self, label):
        return self.wait.until(lambda d: next((item for item in d.find_elements(
            By.CSS_SELECTOR, '.pn-view-toggle__btn')
            if item.is_displayed() and item.text.strip().casefold() == label.casefold()), False))
