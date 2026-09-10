import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pytest
from selenium.webdriver.common.by import By

from pages.employee_view_page import EmployeeViewPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke
DATA = json.loads((Path(__file__).resolve().parents[2] / 'testdata/employee_view_smoke_data.json').read_text(encoding='utf-8'))


def member_data(key):
    member = DATA[key]
    if not member.get('name') or not member.get('email'):
        pytest.skip(f'Configure {key}.name and {key}.email in testdata/employee_view_smoke_data.json')
    return member


@pytest.fixture
def logged_in(driver, credentials):
    login = LoginPage(driver)
    login.login(**credentials)
    assert login.is_dashboard_displayed(), 'Login did not reach authenticated navigation'
    return EmployeeViewPage(driver)


@pytest.fixture
def page(logged_in):
    logged_in.open()
    return logged_in


def test_smk_ev_001_open_employee_view(logged_in):
    logged_in.open_from_menu()


def test_smk_ev_002_essential_controls(page):
    field = page.visible(page.INPUT)
    assert field.is_enabled()
    hint = field.get_attribute('placeholder').lower()
    assert all(word in hint for word in ('3', 'name', 'email'))
    assert page.visible((By.CSS_SELECTOR, "label[for='member-search-box']")).text.lower() == 'search member'
    page.visible(page.SEARCH)
    assert page.visible(page.RESET).is_enabled()


def test_smk_ev_003_search_full_name(page):
    member = member_data('member')
    page.search_member(member['name'], member)


def test_smk_ev_004_search_email(page):
    member = member_data('member')
    page.search_member(member['email'], member)


def test_smk_ev_005_search_three_characters(page):
    member = member_data('member')
    query = member['name'][:3]
    assert len(query) == 3
    page.search_member(query, member)


@pytest.mark.parametrize('query', ['a', 'ab'], ids=['one_character', 'two_characters'])
def test_smk_ev_006_short_search(page, query):
    page.type_query(query)
    button = page.visible(page.SEARCH)
    button.click()  # A native disabled button must not load results.
    assert not button.is_enabled(), 'Short search must be blocked'
    assert not page.options()
    assert not page.result_text()


def test_smk_ev_007_empty_search(page):
    page.type_query('')
    button = page.visible(page.SEARCH)
    button.click()
    assert not button.is_enabled()
    assert not page.options()
    assert not page.result_text()


def test_smk_ev_008_no_matching_member(page):
    member = member_data('member')
    page.search_member(member['email'], member)
    page.type_query(DATA['no_match_query'])
    assert not page.options(), 'The configured no-match query matches an existing member'
    assert not page.visible(page.SEARCH).is_enabled()
    assert not page.member_details(), 'Stale member details remain'
    # Preserve the source requirement for an explicit no-results message.
    page.wait.until(lambda _: any(phrase in (
        page.driver.find_element(By.ID, 'employee-search-form').text + ' ' + page.result_text()
    ).lower() for phrase in ('no results', 'no members', 'no matching', 'not found')))


def test_smk_ev_009_correct_assignments(page):
    member = member_data('assigned_member')
    expected = member.get('expected_jds')
    if not expected:
        pytest.skip('Configure assigned_member.expected_jds from independently known assignment records')
    assert all(set(row) == {'jd_id', 'summary', 'status', 'team', 'company'} for row in expected)
    page.search_member(member['email'], member)
    actual = page.assigned_jds()
    assert sorted(actual, key=lambda r: tuple(r.values())) == sorted(expected, key=lambda r: tuple(r[k] for k in ('jd_id', 'summary', 'status', 'team', 'company')))


def test_smk_ev_010_no_assignments(page):
    member = member_data('unassigned_member')
    page.search_member(member['email'], member)
    assert page.assigned_jds() == []
    assert 'No JDs assigned to this member.' in page.visible(page.ASSIGNED).text


def test_smk_ev_011_reset_search(page):
    member = member_data('member')
    page.search_member(member['email'], member)
    assert page.result_text()
    page.reset()


def test_smk_ev_012_search_after_reset(page):
    first, second = member_data('member'), member_data('second_member')
    assert first['email'] != second['email'], 'Two distinct members are required'
    page.search_member(first['email'], first)
    page.reset()
    page.search_member(second['email'], second)
    assert first['email'] not in page.result_text()


def test_smk_ev_013_requires_login(driver, base_url):
    # The function-scoped driver is a fresh, unauthenticated browser session.
    driver.get(urljoin(base_url, EmployeeViewPage.PATH))
    assert LoginPage(driver).is_login_page_displayed()
    assert urlparse(driver.current_url).path != EmployeeViewPage.PATH
    assert not driver.find_elements(*EmployeeViewPage.RESULT)
    assert not driver.find_elements(*EmployeeViewPage.INPUT)
