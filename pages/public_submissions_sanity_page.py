import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.public_submissions_page import PublicSubmissionsPage


class PublicSubmissionsSanityPage(PublicSubmissionsPage):
    """Sanity controls verified against the admin page on 2026-09-08."""

    def status(self):
        result = self.driver.execute_async_script("""
            const done = arguments[0];
            fetch('/api/public-submissions/status/', {credentials: 'same-origin'})
              .then(async r => done({status: r.status, data: await r.json()}))
              .catch(e => done({error: String(e)}));
        """)
        assert result.get('status') == 200, f"Status API failed: {result.get('status', result.get('error'))}"
        assert result['data'].get('success'), 'Status API returned unsuccessful response'
        return result['data']

    @property
    def total(self):
        text = self.element('ps-summary').text
        match = re.search(r'\((\d+) total\)', text)
        assert match, f'Invalid total submission summary: {text}'
        return int(match[1])

    def previous_page(self):
        old = self.rows()[0]
        assert self.element('ps-page-prev').is_enabled()
        self.click('ps-page-prev')
        self.wait.until(EC.staleness_of(old))

    def all_rows(self):
        """Traverse every page, retaining stable record values for comparison."""
        result = self.row_values()
        for _ in range(1000):
            if not self.element('ps-page-next').is_enabled():
                return result
            self.next_page()
            result.extend(self.row_values())
        raise AssertionError('Pagination did not terminate within 1000 pages')

    def candidate_row(self, email):
        self.search(email)
        rows = self.rows()
        assert len(rows) == 1, f'Expected exactly one row for synthetic candidate, found {len(rows)}'
        assert rows[0].find_elements(By.TAG_NAME, 'td')[1].text == email
        return rows[0]

    def action(self, row, action):
        button = row.find_element(By.CSS_SELECTOR, f'.ps-{action}-btn')
        assert button.is_enabled(), f'{action} action is disabled'
        button.click()

    def checkboxes(self):
        return self.driver.find_elements(By.CSS_SELECTOR, '#ps-submissions-tbody .ps-bulk-cb')
