import pytest

from pages.candidate_page import CandidatePage
from pages.login_page import LoginPage


BLOCKED_REASON = (
    "Candidate Management sanity automation is blocked until the actual ProtonNxt "
    "module path, locators, and approved test data are provided."
)


def _is_value_present(value):
    return isinstance(value, str) and value.strip() != ""


def _candidate_data_is_ready(candidate_testdata):
    module_details = candidate_testdata.get("module_details", {})
    search_candidate = candidate_testdata.get("search_candidate", {})

    return _is_value_present(module_details.get("navigation_path")) and (
        _is_value_present(search_candidate.get("candidate_name"))
        or _is_value_present(search_candidate.get("candidate_id"))
        or _is_value_present(search_candidate.get("email"))
    )


def _skip_if_candidate_suite_not_ready(candidate_testdata):
    if not _candidate_data_is_ready(candidate_testdata):
        pytest.skip(BLOCKED_REASON)


@pytest.mark.sanity
def test_candidate_management_page_load(driver, credentials, candidate_testdata):
    _skip_if_candidate_suite_not_ready(candidate_testdata)

    login_page = LoginPage(driver)
    candidate_page = CandidatePage(driver)

    login_page.login(**credentials)
    candidate_page.open_from_navigation()

    assert candidate_page.is_page_loaded(), "Candidate Management page did not load successfully"


@pytest.mark.sanity
def test_candidate_search(driver, credentials, candidate_testdata):
    _skip_if_candidate_suite_not_ready(candidate_testdata)

    login_page = LoginPage(driver)
    candidate_page = CandidatePage(driver)

    login_page.login(**credentials)
    candidate_page.open_from_navigation()
    candidate_page.search_candidate(candidate_testdata["search_candidate"]["candidate_name"])

    pytest.skip(BLOCKED_REASON)


@pytest.mark.sanity
def test_candidate_profile_open(driver, credentials, candidate_testdata):
    _skip_if_candidate_suite_not_ready(candidate_testdata)

    login_page = LoginPage(driver)
    candidate_page = CandidatePage(driver)

    login_page.login(**credentials)
    candidate_page.open_from_navigation()
    candidate_page.open_candidate(candidate_testdata["search_candidate"]["candidate_name"])

    pytest.skip(BLOCKED_REASON)


@pytest.mark.sanity
def test_candidate_create_flow(driver, credentials, candidate_testdata):
    _skip_if_candidate_suite_not_ready(candidate_testdata)

    login_page = LoginPage(driver)
    candidate_page = CandidatePage(driver)

    login_page.login(**credentials)
    candidate_page.open_from_navigation()
    candidate_page.create_candidate(candidate_testdata["create_candidate"])

    pytest.skip(BLOCKED_REASON)


@pytest.mark.sanity
def test_candidate_update_flow(driver, credentials, candidate_testdata):
    _skip_if_candidate_suite_not_ready(candidate_testdata)

    login_page = LoginPage(driver)
    candidate_page = CandidatePage(driver)

    login_page.login(**credentials)
    candidate_page.open_from_navigation()
    candidate_page.update_candidate(candidate_testdata["update_candidate"])

    pytest.skip(BLOCKED_REASON)


@pytest.mark.sanity
def test_candidate_required_field_validation(driver, credentials, candidate_testdata):
    _skip_if_candidate_suite_not_ready(candidate_testdata)

    login_page = LoginPage(driver)
    candidate_page = CandidatePage(driver)

    login_page.login(**credentials)
    candidate_page.open_from_navigation()

    pytest.skip(BLOCKED_REASON)
