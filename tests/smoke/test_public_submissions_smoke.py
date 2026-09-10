"""One independent automated test for each SMK-PS case in the supplied workbook."""
import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from uuid import uuid4
from xml.sax.saxutils import escape
from zipfile import ZipFile

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from config.config import Config
from pages.login_page import LoginPage
from pages.public_submissions_page import PublicSubmissionsPage


pytestmark = pytest.mark.smoke
DATA = json.loads((Path(__file__).resolve().parents[2] / "testdata/public_submissions_smoke_data.json").read_text(encoding="utf-8"))


@pytest.fixture
def admin(driver, credentials):
    login = LoginPage(driver)
    login.open(Config.BASE_URL)
    login.login(**credentials)
    assert login.is_authenticated_destination_displayed(), "Admin login failed"
    return PublicSubmissionsPage(driver).open(DATA["admin_path"])


@pytest.fixture
def public_browser(request):
    options = webdriver.ChromeOptions()
    if Config.CHROME_BINARY:
        options.binary_location = Config.CHROME_BINARY
    if request.config.getoption("--headless"):
        options.add_argument("--headless=new")
    options.add_argument("--incognito")
    options.add_argument("--window-size=1440,900")
    service = Service(Config.CHROMEDRIVER_PATH) if Config.CHROMEDRIVER_PATH else Service()
    browser = webdriver.Chrome(service=service, options=options)
    try:
        yield PublicSubmissionsPage(browser)
    finally:
        browser.quit()


@pytest.fixture
def active_url(admin):
    existing = admin.url
    url = existing or admin.generate()
    try:
        yield url
    finally:
        if not existing:
            admin.open(DATA["admin_path"])
            if admin.url == url:
                admin.revoke()


@pytest.fixture
def lifecycle(admin):
    if admin.url:
        if os.getenv("PROTONNXT_PS_ALLOW_REVOKE_EXISTING", "").lower() != "true":
            pytest.skip("Active link preserved. Use a dedicated tenant without a link, or explicitly set PROTONNXT_PS_ALLOW_REVOKE_EXISTING=true.")
        admin.revoke()
    try:
        yield admin
    finally:
        # This fixture owns links generated after the initial empty state.
        admin.open(DATA["admin_path"])
        if admin.url:
            admin.revoke()


@pytest.fixture
def candidate(tmp_path):
    return _make_candidate(tmp_path)


def _make_candidate(tmp_path):
    seed = DATA["candidate"]
    token = uuid4().hex[:12]
    data = {
        "name": f"{seed['name_prefix']} {token}",
        "email": f"{seed['email_prefix']}.{token}@{seed['email_domain']}",
        "phone": "9" + str(int(token, 16) % 10**9).zfill(9),
        "skills": seed["skills"],
    }
    resume = tmp_path / f"candidate_resume_{token}.docx"
    paragraphs = [data['name'], data['email'], data['phone'], data['skills'],
                  'Software Engineer with five years of Python and Django experience.',
                  'Education: Bachelor of Engineering. Location: Bengaluru.']
    with ZipFile(resume, "w") as doc:
        doc.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        doc.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        doc.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + ''.join(f'<w:p><w:r><w:t>{escape(p)}</w:t></w:r></w:p>' for p in paragraphs) + '<w:sectPr/></w:body></w:document>')
    return data, resume


@pytest.fixture
def submission(admin, active_url, public_browser, candidate):
    data, resume = candidate
    before = admin.count
    public_browser.open_public(active_url)
    public_browser.submit_candidate(data, resume)
    admin.refresh()
    return data, before


def test_smk_ps_001_admin_page_loads(admin):
    body = admin.driver.find_element(By.TAG_NAME, "body").text
    assert "Public Submission URL" in body and "Recent Submissions" in body
    assert admin.url or admin.visible("ps-generate-btn")


def test_smk_ps_002_generate_confirmation(lifecycle):
    alert = lifecycle.confirmation("generate")
    try:
        assert "generate" in alert.text.lower() and "url" in alert.text.lower()
    finally:
        alert.dismiss()


def test_smk_ps_003_cancel_generation(lifecycle):
    lifecycle.confirmation("generate").dismiss()
    lifecycle.refresh()
    assert not lifecycle.url and lifecycle.visible("ps-generate-btn")


def test_smk_ps_004_generate_url(lifecycle):
    assert lifecycle.generate()
    assert lifecycle.visible("ps-copy-btn") and lifecycle.visible("ps-revoke-btn")
    assert lifecycle.count == 0, "New link must start with zero submissions"


def test_smk_ps_005_copy_url(admin, active_url):
    origin = urlparse(admin.driver.current_url)
    admin.driver.execute_cdp_cmd("Browser.grantPermissions", {
        "origin": f"{origin.scheme}://{origin.netloc}",
        "permissions": ["clipboardReadWrite", "clipboardSanitizedWrite"],
    })
    admin.click("ps-copy-btn")
    admin.wait.until(lambda _: "Copied" in admin.element("ps-copy-btn").text)
    value = admin.driver.execute_async_script("const done=arguments[0]; navigator.clipboard.readText().then(v=>done({value:v}),e=>done({error:String(e)}));")
    assert value.get("value") == active_url, f"Clipboard mismatch: {value}"


def test_smk_ps_006_public_url_without_login(active_url, public_browser):
    assert not public_browser.driver.get_cookies(), "Public browser must start without cookies"
    public_browser.open_public(active_url)
    assert public_browser.visible("ps-submit-btn")


def test_smk_ps_007_valid_candidate_submission(submission):
    # Fixture asserts a visible success confirmation after the real form submission.
    assert submission[0]["email"]


def test_smk_ps_008_recent_submission_details(admin, submission):
    data, _ = submission
    admin.search(data["email"])
    rows = admin.row_values()
    assert len(rows) == 1, f"Expected one candidate, found {len(rows)}"
    assert rows[0][:4] == [data[k] for k in ("name", "email", "phone", "skills")]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", rows[0][4]), "Submitted date is missing"
    assert rows[0][5] and rows[0][5] != "-", "Status is missing"
    assert admin.rows()[0].find_elements(By.CSS_SELECTOR, "td:nth-child(7) button"), "Actions missing"
    headers = [e.text.strip().lower() for e in admin.driver.find_elements(By.CSS_SELECTOR, ".ps-tbl thead th")]
    assert all(h.lower() in headers for h in DATA["expected_headers"])


def test_smk_ps_009_submission_counter(admin, submission):
    _, before = submission
    assert admin.count == before + 1, "Counter did not increase by exactly one"


def test_smk_ps_010_search_matching_submission(admin, submission):
    data, _ = submission
    for query in (data["name"], data["email"], data["phone"], "Python"):
        admin.search(query)
        rows = admin.row_values()
        assert rows, f"Search returned no results for {query}"
        assert all(query.lower() in " ".join(row[:4]).lower() for row in rows), "Unrelated search result"
        if query != "Python":
            assert any(row[1] == data["email"] for row in rows)
    admin.search(uuid4().hex)
    assert not admin.rows(), "Nonmatching search returned records"


def test_smk_ps_011_page_size_and_pagination(admin, active_url, public_browser, tmp_path):
    size = DATA["page_size"]
    admin.set_page_size(100 if size != 100 else 50)
    missing = max(0, size + 1 - len(admin.rows()))
    for _ in range(missing):
        data, resume = _make_candidate(tmp_path)
        public_browser.open_public(active_url)
        public_browser.submit_candidate(data, resume)
    if missing:
        admin.refresh()
        admin.set_page_size(100 if size != 100 else 50)
    assert len(admin.rows()) > size, "Seeded submissions did not populate pagination"
    baseline = [r[1] for r in admin.row_values()]
    admin.set_page_size(size)
    assert Select(admin.element("ps-pagesize-select")).first_selected_option.get_attribute("value") == str(size)
    assert len(admin.rows()) == size
    seen = [r[1] for r in admin.row_values()]
    while admin.element("ps-page-next").is_enabled():
        admin.next_page()
        rows = admin.row_values()
        assert 0 < len(rows) <= size
        seen.extend(row[1] for row in rows)
    assert len(seen) == len(set(seen)), "Duplicate candidate across pages"
    assert seen[:len(baseline)] == baseline, "Rows missing or reordered after page-size change"
    summary = admin.element("ps-pagination-info").text
    total = re.search(r"of\s+(\d+)", summary)
    assert total and len(seen) == int(total[1]), f"Missing rows: {summary}"


def test_smk_ps_012_revoke_url(lifecycle, public_browser):
    old = lifecycle.generate()
    lifecycle.revoke()
    assert not lifecycle.url and not lifecycle.visible("ps-copy-btn")
    public_browser.assert_revoked(old)


def test_smk_ps_013_regenerate_after_revocation(lifecycle, public_browser):
    old = lifecycle.generate()
    lifecycle.revoke()
    new = lifecycle.generate()
    assert new != old
    public_browser.open_public(new)
    public_browser.assert_revoked(old)


def test_smk_ps_014_refresh_persistence(admin, active_url, submission):
    data, _ = submission
    admin.search(data["email"])
    before = admin.row_values()
    count = admin.count
    admin.refresh()
    assert admin.url == active_url and admin.count == count
    admin.search(data["email"])
    assert admin.row_values() == before and len(before) == 1


def test_smk_ps_015_unauthorized_access(driver):
    username = os.getenv("PROTONNXT_PS_UNAUTHORIZED_USERNAME", "")
    password = os.getenv("PROTONNXT_PS_UNAUTHORIZED_PASSWORD", "")
    company = os.getenv("PROTONNXT_PS_UNAUTHORIZED_COMPANY_CODE", Config.COMPANY_CODE)
    if not username or not password:
        pytest.skip("Configure PROTONNXT_PS_UNAUTHORIZED_USERNAME and PROTONNXT_PS_UNAUTHORIZED_PASSWORD for a non-admin account")
    assert (company, username) != (Config.COMPANY_CODE, Config.USERNAME), "Unauthorized account must differ from admin"
    login = LoginPage(driver)
    login.login(company, username, password)
    assert login.is_authenticated_destination_displayed(), "Unauthorized account login failed; access check was not reached"
    target = urljoin(Config.BASE_URL, DATA["admin_path"])
    driver.get(target)
    page = PublicSubmissionsPage(driver)
    body = driver.find_element(By.TAG_NAME, "body").text.lower()
    denied = any(term in body for term in ("forbidden", "access denied", "permission denied", "not authorized", "unauthorized"))
    assert urlparse(driver.current_url).path != urlparse(target).path or denied, "Non-admin accessed the admin page"
    assert not any(page.visible(i) for i in ("ps-generate-btn", "ps-revoke-btn", "ps-copy-btn", "ps-url-text", "ps-submissions-tbody")), "Admin controls or data exposed"
