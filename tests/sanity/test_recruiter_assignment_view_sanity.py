"""Automation mapped to SNT-RAV-001 through SNT-RAV-020; not executed on creation."""

import json
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from pages.recruiter_assignment_view_page import RecruiterAssignmentViewPage


pytestmark = pytest.mark.sanity
DATA = json.loads((Path(__file__).resolve().parents[2] /
                   'testdata/recruiter_assignment_view_sanity_data.json').read_text(encoding='utf-8'))
def member(key='member'):
    target = DATA.get(key, {})
    if not target.get('name') or not target.get('email'):
        pytest.skip(f'Configure {key} in recruiter_assignment_view_sanity_data.json')
    return target


def expected_assignments(target):
    expected = target.get('expected_jds')
    if expected is None:
        pytest.skip('Configure independently known expected_jds for this member')
    return expected


def canonical(rows):
    return sorted(json.dumps(row, sort_keys=True) for row in rows)


@pytest.fixture
def logged_in(driver, credentials):
    login = LoginPage(driver)
    login.login(**credentials)
    assert login.is_dashboard_displayed(), 'Authorized login failed'
    return RecruiterAssignmentViewPage(driver)


@pytest.fixture
def page(logged_in):
    logged_in.open()
    return logged_in


def test_snt_rav_001_open_recruiter_assignment_view(logged_in):
    logged_in.open(from_menu=True)
    for locator in (logged_in.INPUT, logged_in.SEARCH, logged_in.RESET):
        logged_in.visible(locator)
    logged_in.assert_no_server_error()


def test_snt_rav_002_authorized_access(page):
    target = member()
    page.search(target['email'], target)
    page.visible(page.ASSIGNED)
    page.visible(page.TEAMS)


def test_snt_rav_003_exact_name(page):
    target = member('assigned_member')
    expected = expected_assignments(target)
    page.search(target['name'], target)
    assert canonical(page.assigned_jds()) == canonical(expected)


def test_snt_rav_004_partial_name(page):
    target = member()
    query = target['name'][:3]
    assert len(query) == 3
    page.assert_matches(query, page.read_members())
    page.search(query, target)


def test_snt_rav_005_exact_email(page):
    target = member('assigned_member')
    expected = expected_assignments(target)
    page.search(target['email'], target)
    assert canonical(page.assigned_jds()) == canonical(expected)


def test_snt_rav_006_partial_email(page):
    target = member()
    query = target['email'][:3]
    page.assert_matches(query, page.read_members())
    page.search(query, target)


def test_snt_rav_007_case_insensitive(page):
    target = member()
    snapshots = []
    for query in (target['email'].upper(), target['email'].lower()):
        page.search(query, target)
        snapshots.append((page.member_details(), canonical(page.assigned_jds())))
    assert snapshots[0] == snapshots[1]


@pytest.mark.parametrize('query', ['a', 'ab'], ids=['one_character', 'two_characters'])
def test_snt_rav_008_minimum_length(page, query):
    before = page.request_count()
    page.type_query(query)
    page.visible(page.SEARCH).click()
    assert not page.options() and not page.result_text()
    assert not page.visible(page.SEARCH).is_enabled(), 'Short search must be blocked'
    assert page.request_count() == before, 'Short query submitted a report request'


def test_snt_rav_009_blank_search(page):
    before = page.request_count()
    page.type_query('')
    page.visible(page.SEARCH).click()
    assert not page.options() and not page.result_text()
    assert not page.visible(page.SEARCH).is_enabled()
    assert page.request_count() == before


def test_snt_rav_010_no_match(page):
    target = member()
    page.search(target['email'], target)
    before = page.request_count()
    page.type_query(DATA['no_match_query'])
    page.visible(page.SEARCH).click()
    assert not page.options() and not page.member_details()
    assert not page.visible(page.SEARCH).is_enabled(), 'A no-match query must not be searchable'
    assert page.request_count() == before, 'A no-match query submitted a report request'
    page.assert_no_server_error()


def test_snt_rav_011_trim_spaces(page):
    target = member()
    page.search('  ' + target['email'] + '  ', target)


def test_snt_rav_012_reset(page):
    target = member()
    page.search(target['email'], target)
    assert page.result_text()
    page.reset()


def test_snt_rav_013_new_search_replaces_results(page):
    first, second = member(), member('second_member')
    assert first['email'] != second['email'], 'Configure two distinct members'
    page.search(first['email'], first)
    page.search(second['email'], second)
    assert first['email'] not in page.result_text()


def test_snt_rav_014_enter_search(page):
    target = member()
    page.search(target['email'], target)
    expected = page.result_text()
    page.reset()
    before = page.request_count()
    page.search(target['email'], target, enter=True)
    assert page.result_text() == expected
    assert page.request_count() == before + 1, 'Enter must issue exactly one search'


@pytest.mark.parametrize('query', ['!@#$%^&*', '<svg onload="window.__rav_probe=1">'],
                         ids=['special_characters', 'script_like_input'])
def test_snt_rav_015_special_characters(page, query):
    page.driver.execute_script('window.__rav_probe = 0')
    before = page.request_count()
    page.type_query(query)
    page.visible(page.SEARCH).click()
    assert not page.options()
    assert not page.visible(page.SEARCH).is_enabled(), 'Invalid input must not be searchable'
    assert page.request_count() == before, 'Invalid input submitted a report request'
    assert page.driver.execute_script('return window.__rav_probe') == 0, 'Input executed as script'
    assert not page.member_details()
    page.assert_no_server_error()


def test_snt_rav_016_result_data_accuracy(page):
    target = member('assigned_member')
    expected = expected_assignments(target)
    if target.get('expected_details') is None or target.get('expected_teams') is None:
        pytest.skip('Configure independently saved assigned_member.expected_details and expected_teams')
    page.search(target['email'], target)
    assert page.member_details() == target['expected_details']
    assert canonical(page.assigned_jds()) == canonical(expected)
    normalize_teams = lambda teams: sorted((t['name'], canonical(t['jds'])) for t in teams)
    assert normalize_teams(page.teams()) == normalize_teams(target['expected_teams'])


def test_snt_rav_017_member_without_assignments(page):
    target = member('unassigned_member')
    page.search(target['email'], target)
    assert page.assigned_jds() == []
    assert page.teams() == []
    assert 'No JDs assigned to this member.' in page.result_text()
    assert 'Member is not part of any team.' in page.result_text()
    page.assert_no_server_error()


def test_snt_rav_018_multiple_matches(page):
    page.assert_matches(DATA['multiple_match_query'], page.read_members(), minimum=2)


def test_snt_rav_019_repeated_search_stability(page):
    snapshots = {}
    for target in [member(), member('second_member')] * 3:
        before = page.request_count()
        page.search(target['email'], target)
        assert page.request_count() == before + 1
        assert len(page.driver.find_elements(By.CSS_SELECTOR, '#employee-result > .ev-section')) == 3
        actual = (page.member_details(), canonical(page.assigned_jds()))
        if target['email'] in snapshots:
            assert actual == snapshots[target['email']]
        snapshots[target['email']] = actual
        page.reset()


@pytest.mark.parametrize('size', [(1440, 900), (768, 1024), (390, 844)], ids=['desktop', 'tablet', 'mobile'])
def test_snt_rav_020_responsive_layout(page, size):
    page.driver.set_window_size(*size)
    target = member()
    page.search(target['email'], target)
    page.assert_layout()
    page.reset()
