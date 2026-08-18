from selenium.webdriver.support.ui import WebDriverWait


class CandidatePage:
    """
    Candidate Management page-object scaffold.

    Real ProtonNxt locators and workflows must be supplied before these
    methods can be implemented.
    """

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_from_navigation(self):
        raise NotImplementedError(
            "Candidate Management navigation locator is required before automation can be implemented."
        )

    def is_page_loaded(self):
        raise NotImplementedError(
            "Candidate Management page-load locator is required before automation can be implemented."
        )

    def search_candidate(self, candidate_name):
        raise NotImplementedError(
            "Candidate Management search locators are required before automation can be implemented."
        )

    def open_candidate(self, candidate_name):
        raise NotImplementedError(
            "Candidate row and open-action locators are required before automation can be implemented."
        )

    def create_candidate(self, candidate_data):
        raise NotImplementedError(
            "Candidate creation locators and approved test data are required before automation can be implemented."
        )

    def update_candidate(self, candidate_data):
        raise NotImplementedError(
            "Candidate update locators and approved test data are required before automation can be implemented."
        )
