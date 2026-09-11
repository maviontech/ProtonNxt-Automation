"""Independent Selenium coverage for SAN-PS-001 through SAN-PS-022."""
import base64
import json
from datetime import date
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape
from zipfile import ZipFile

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.config import Config
from pages.login_page import LoginPage
from pages.public_submissions_sanity_page import PublicSubmissionsSanityPage


pytestmark = pytest.mark.sanity
DATA = json.loads((Path(__file__).resolve().parents[2] / 'testdata/public_submissions_sanity_data.json').read_text())


@pytest.fixture
def admin(driver, credentials):
    login = LoginPage(driver)
    login.open(Config.BASE_URL)
    login.login(**credentials)
    assert login.is_authenticated_destination_displayed(), 'Admin login failed'
    return PublicSubmissionsSanityPage(driver).open(DATA['admin_path'])


@pytest.fixture
def empty_link(admin):
    if admin.url:
        pytest.skip('Requires a test tenant with no active public URL; existing links are preserved')
    try:
        yield admin
    finally:
        admin.open(DATA['admin_path'])
        if admin.url:
            admin.revoke()


@pytest.fixture
def active_url(admin):
    existing = admin.url
    url = existing or admin.generate()
    try:
        yield url
    finally:
        if not existing:
            admin.open(DATA['admin_path'])
            if admin.url == url:
                admin.revoke()


@pytest.fixture
def public_browser(request):
    options = webdriver.ChromeOptions()
    if Config.CHROME_BINARY:
        options.binary_location = Config.CHROME_BINARY
    if request.config.getoption('--headless'):
        options.add_argument('--headless=new')
    options.add_argument('--incognito')
    options.add_argument('--window-size=1440,900')
    service = Service(Config.CHROMEDRIVER_PATH) if Config.CHROMEDRIVER_PATH else Service()
    browser = webdriver.Chrome(service=service, options=options)
    try:
        yield PublicSubmissionsSanityPage(browser)
    finally:
        browser.quit()


@pytest.fixture
def create_candidate(admin, active_url, public_browser, tmp_path):
    def create():
        token = uuid4().hex[:12]
        candidate = {
            'name': f"{DATA['candidate']['name_prefix']} {token}",
            'email': f"sanity.ps.{token}@{DATA['candidate']['email_domain']}",
            'phone': '9' + str(int(token, 16) % 10**9).zfill(9),
            'skills': DATA['candidate']['skills'],
        }
        resume = tmp_path / f'sanity_resume_{token}.docx'
        paragraphs = list(candidate.values()) + [
            'Software Engineer with five years of Python and Django experience.',
            'Bachelor of Engineering. Location: Bengaluru.',
        ]
        with ZipFile(resume, 'w') as doc:
            doc.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            doc.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
            doc.writestr('word/document.xml', '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + ''.join(f'<w:p><w:r><w:t>{escape(p)}</w:t></w:r></w:p>' for p in paragraphs) + '<w:sectPr/></w:body></w:document>')
        public_browser.open_public(active_url)
        public_browser.submit_candidate(candidate, resume)
        admin.refresh()
        return candidate, resume
    return create


@pytest.fixture
def submission(create_candidate):
    return create_candidate()


@pytest.fixture
def populated(admin, create_candidate):
    # Existing data can satisfy pagination; seed only the shortfall.
    count = len(admin.status()['submissions'])
    for _ in range(max(0, DATA['alternate_page_size'] + 1 - count)):
        create_candidate()
    return admin


def test_san_ps_001_page_loads(admin):
    body = admin.driver.find_element(By.TAG_NAME, 'body').text
    assert 'Public Submission URL' in body and 'Recent Submissions' in body
    assert admin.url or admin.visible('ps-generate-btn')
    assert not any(term in body.lower() for term in ('server error', 'unable to load', 'error loading'))


def test_san_ps_002_generate_button_empty_state(empty_link):
    assert not empty_link.url
    assert empty_link.element('ps-generate-btn').is_enabled()
    assert 'no public url' in empty_link.element('ps-url-text').text.lower()


def test_san_ps_003_generate_url(empty_link, public_browser):
    url = empty_link.generate()
    assert empty_link.visible('ps-copy-btn') and empty_link.visible('ps-revoke-btn')
    public_browser.open_public(url)
    assert public_browser.visible('ps-submit-btn')


def test_san_ps_004_url_survives_refresh(admin, active_url):
    admin.refresh()
    assert admin.url == active_url


def test_san_ps_005_list_columns(admin, submission):
    headers = [e.text.strip() for e in admin.driver.find_elements(By.CSS_SELECTOR, '.ps-tbl thead th')]
    assert [h.lower() for h in headers[:7]] == [h.lower() for h in DATA['expected_headers']]
    assert admin.rows()
    assert all(len(row) == 8 for row in admin.row_values())


def test_san_ps_006_total_matches_backend(populated):
    expected = len(populated.status()['submissions'])
    assert populated.total == expected
    assert len(populated.all_rows()) == expected


def test_san_ps_007_matching_search(admin, submission):
    candidate, _ = submission
    for query in (candidate['name'], candidate['email'], candidate['phone'], 'Python'):
        admin.search(query)
        rows = admin.row_values()
        assert rows, f'No search results for {query}'
        assert all(query.lower() in ' '.join(row[:4]).lower() for row in rows)
        assert any(row[1] == candidate['email'] for row in rows)


def test_san_ps_008_short_search_does_not_filter(populated):
    before = populated.row_values()
    assert 'min 3' in populated.element('ps-search').get_attribute('placeholder').lower()
    for query in ('z', 'zz'):
        populated.search(query)
        assert populated.row_values() == before, 'Search filtered below three characters'


def test_san_ps_009_no_results(admin, submission):
    admin.search(f'zzzz_no_match_{uuid4().hex}')
    assert not admin.rows()
    assert 'no submissions match' in admin.element('ps-submissions-tbody').text.lower()


def test_san_ps_010_default_page_size(populated):
    assert Select(populated.element('ps-pagesize-select')).first_selected_option.get_attribute('value') == str(DATA['default_page_size'])
    assert len(populated.rows()) == DATA['default_page_size']
    assert populated.element('ps-page-next').is_enabled()


def test_san_ps_011_change_page_size(populated):
    baseline = populated.all_rows()
    populated.set_page_size(DATA['alternate_page_size'])
    assert len(populated.rows()) == DATA['alternate_page_size']
    assert Select(populated.element('ps-pagesize-select')).first_selected_option.get_attribute('value') == str(DATA['alternate_page_size'])
    assert populated.all_rows() == baseline, 'Page-size change lost or reordered submissions'


def test_san_ps_012_next_previous_pages(populated):
    first = populated.row_values()
    first_info = populated.element('ps-pagination-info').text
    populated.next_page()
    second = populated.row_values()
    assert second and not ({r[1] for r in first} & {r[1] for r in second})
    assert populated.element('ps-pagination-info').text != first_info
    populated.previous_page()
    assert populated.row_values() == first
    assert populated.element('ps-pagination-info').text == first_info
    assert len(populated.all_rows()) == len(populated.status()['submissions'])


def test_san_ps_013_candidate_data_mapping(admin, submission):
    candidate, _ = submission
    row = admin.candidate_row(candidate['email'])
    cells = row.find_elements(By.TAG_NAME, 'td')
    assert [c.text for c in cells[:3]] == [candidate[k] for k in ('name', 'email', 'phone')]
    assert cells[3].get_attribute('title') == candidate['skills']
    date.fromisoformat(cells[4].text)
    assert cells[5].text == 'Pool'
    record = next(r for r in admin.status()['submissions'] if r['email'] == candidate['email'])
    assert all(record[k] == candidate[k] for k in ('name', 'email', 'phone', 'skills'))
    assert cells[4].text == record['created_at'].split('T')[0]


def test_san_ps_014_status_matches_new_record(admin, submission):
    assert all(row[5] in DATA['valid_statuses'] for row in admin.row_values())
    candidate, _ = submission
    row = admin.candidate_row(candidate['email'])
    assert row.find_elements(By.TAG_NAME, 'td')[5].text == 'Pool'
    record = next(r for r in admin.status()['submissions'] if r['email'] == candidate['email'])
    assert record.get('screen_status') != 'rejected'
    assert '[Reassigned' not in (record.get('recruiter_comments') or '')


def test_san_ps_015_resume_document(admin, submission):
    candidate, resume = submission
    row = admin.candidate_row(candidate['email'])
    rid = row.find_element(By.CSS_SELECTOR, '.ps-view-btn').get_attribute('data-rid')
    record = next(r for r in admin.status()['submissions'] if r['email'] == candidate['email'])
    assert str(record['resume_id']) == rid
    handles = admin.driver.window_handles
    admin.action(row, 'view')
    admin.wait.until(EC.new_window_is_opened(handles))
    original = admin.driver.current_window_handle
    try:
        admin.driver.switch_to.window(next(h for h in admin.driver.window_handles if h not in handles))
        admin.wait.until(lambda d: f'/view_resume/{rid}/' in d.current_url)
    finally:
        admin.driver.close()
        admin.driver.switch_to.window(original)
    result = admin.driver.execute_async_script("""
        const rid=arguments[0], done=arguments[1];
        fetch('/view_resume/'+rid+'/', {credentials:'same-origin'})
          .then(async r => {const b=new Uint8Array(await r.arrayBuffer());
            let s=''; for(const v of b) s+=String.fromCharCode(v);
            done({status:r.status, type:r.headers.get('content-type'), data:btoa(s)});})
          .catch(e=>done({error:String(e)}));
    """, rid)
    assert result.get('status') == 200, 'Resume endpoint failed'
    content = base64.b64decode(result['data'])
    assert content == resume.read_bytes(), 'Returned document differs from this candidate\'s uploaded resume'


def test_san_ps_016_assign_workflow(admin, submission):
    candidate, _ = submission
    admin.action(admin.candidate_row(candidate['email']), 'assign')
    admin.element('ps-reassign-overlay')
    assert admin.element('ps-reassign-name').text == candidate['name']
    options = Select(admin.element('ps-reassign-jd')).options
    assert options and not any('unable to load' in o.text.lower() for o in options)
    assert admin.visible('ps-reassign-member') and admin.visible('ps-reassign-confirm')
    admin.click('ps-reassign-cancel')
    admin.wait.until(lambda _: not admin.visible('ps-reassign-overlay'))
    assert admin.candidate_row(candidate['email']).find_elements(By.TAG_NAME, 'td')[5].text == 'Pool'


def test_san_ps_017_ai_matching(admin, submission):
    candidate, _ = submission
    admin.action(admin.candidate_row(candidate['email']), 'ai')
    assert candidate['name'] in admin.element('ps-ai-title').text
    WebDriverWait(admin.driver, DATA['ai_timeout_seconds']).until(
        lambda _: not admin.driver.find_elements(By.CSS_SELECTOR, '#ps-ai-body .ai-spinner'))
    body = admin.element('ps-ai-body').text
    assert body.strip(), 'AI result is empty'
    assert 'found across' in admin.element('ps-ai-subtitle').text, f'AI matching failed: {body}'
    assert not admin.driver.find_elements(By.CSS_SELECTOR, '#ps-ai-body .fa-exclamation-circle'), body
    admin.click('ps-ai-close')


def test_san_ps_018_drop_cancel_then_confirm(admin, submission):
    candidate, _ = submission
    row = admin.candidate_row(candidate['email'])
    before = {str(r['candidate_id']): r for r in admin.status()['submissions']}
    target_id = row.find_element(By.CSS_SELECTOR, '.ps-drop-btn').get_attribute('data-id')
    admin.action(row, 'drop')
    alert = admin.wait.until(EC.alert_is_present())
    try:
        assert candidate['name'] in alert.text
    finally:
        alert.dismiss()
    admin.refresh()
    assert {str(r['candidate_id']): r for r in admin.status()['submissions']} == before, 'Cancel changed backend data'
    admin.action(admin.candidate_row(candidate['email']), 'drop')
    alert = admin.wait.until(EC.alert_is_present())
    alert.send_keys('Automated sanity test synthetic candidate')
    alert.accept()
    admin.wait.until(lambda _: any(r[1] == candidate['email'] and r[5] == 'Dropped' for r in admin.row_values()))
    after = {str(r['candidate_id']): r for r in admin.status()['submissions']}
    assert after[target_id]['screen_status'] == 'rejected'
    assert {k: v for k, v in after.items() if k != target_id} == {k: v for k, v in before.items() if k != target_id}, 'Drop changed another candidate'


def test_san_ps_019_individual_selection(admin, submission):
    boxes = admin.checkboxes()
    assert boxes, 'No selectable candidate rows'
    assert not any(b.is_selected() for b in boxes)
    boxes[0].click()
    assert boxes[0].is_selected() and not any(b.is_selected() for b in boxes[1:])
    boxes[0].click()
    assert not any(b.is_selected() for b in boxes)


def test_san_ps_020_select_all_visible(admin, create_candidate):
    first, _ = create_candidate()
    second, _ = create_candidate()
    admin.search(DATA['candidate']['name_prefix'])
    boxes = admin.checkboxes()
    assert len(boxes) >= 2
    assert {first['email'], second['email']} <= {r[1] for r in admin.row_values()}
    admin.click('ps-select-all')
    assert admin.element('ps-select-all').is_selected()
    assert all(b.is_selected() for b in boxes)
    admin.click('ps-select-all')
    assert not admin.element('ps-select-all').is_selected()
    assert not any(b.is_selected() for b in boxes)


def test_san_ps_021_sidebar_navigation(admin):
    driver = admin.driver

    def click_visible_sidebar_link(path):
        """Click the displayed sidebar item, not a hidden duplicate navigation link."""
        selector = f'a[href="{path}"]'
        link = admin.wait.until(
            lambda d: next(
                (
                    item for item in d.find_elements(By.CSS_SELECTOR, selector)
                    if item.is_displayed() and item.is_enabled()
                ),
                False,
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
        admin.wait.until(lambda _: link.is_displayed() and link.is_enabled())
        link.click()

    click_visible_sidebar_link('/view_edit_jds/')
    admin.wait.until(lambda d: '/view_edit_jds/' in d.current_url)
    click_visible_sidebar_link(DATA['admin_path'])
    admin.wait_ready()
    link = next(
        item for item in driver.find_elements(By.CSS_SELECTOR, f'a[href="{DATA["admin_path"]}"]')
        if item.is_displayed()
    )
    assert link.get_attribute('aria-current') == 'page'
    assert driver.current_url.rstrip('/').endswith(DATA['admin_path'].rstrip('/'))


def test_san_ps_022_refresh_retains_data(admin, active_url, submission):
    before = admin.status()['submissions']
    rows = admin.all_rows()
    admin.refresh()
    assert admin.url == active_url
    assert admin.status()['submissions'] == before, 'Refresh duplicated or changed backend submissions'
    assert admin.all_rows() == rows
