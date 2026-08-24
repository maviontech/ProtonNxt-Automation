import pytest

from config.config import Config
from pages.login_page import LoginPage
from pages.manage_members_page import ManageMembersPage


pytestmark = pytest.mark.smoke


def _open_manage_members_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)

    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"

    manage_members_page = ManageMembersPage(driver)
    manage_members_page.open()
    assert manage_members_page.is_page_displayed(), "Manage Members page did not load"
    return manage_members_page


def test_mms_001_application_login_and_manage_members_page_load(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)
    case_data = Config.MANAGE_MEMBERS_SMOKE_TESTDATA["smoke_cases"]["MMS-001"]

    assert "member_table" in case_data["expected_elements"], "Smoke data is missing member table expectation"
    assert manage_members_page.is_member_table_displayed(), "Member list table is not displayed"
    assert manage_members_page.get_table_headers() == case_data["expected_headers"]


def test_mms_002_manage_members_controls_are_visible_and_clickable(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)
    case_data = Config.MANAGE_MEMBERS_SMOKE_TESTDATA["smoke_cases"]["MMS-002"]

    assert "member_search" in case_data["expected_controls"], "Smoke data is missing member search expectation"
    manage_members_page.search(case_data["member_search_query"])
    assert manage_members_page.get_member_search_value() == case_data["member_search_query"]

    assert "global_search" in case_data["expected_controls"], "Smoke data is missing global search expectation"
    manage_members_page.search_globally(case_data["global_search_query"])
    assert manage_members_page.get_global_search_value() == case_data["global_search_query"]

    assert "cards_view_button" in case_data["expected_controls"], "Smoke data is missing cards view expectation"
    manage_members_page.switch_to_cards()
    assert manage_members_page.is_page_displayed(), "Manage Members page disappeared after switching to Cards view"

    assert "list_view_button" in case_data["expected_controls"], "Smoke data is missing list view expectation"
    manage_members_page.switch_to_list()
    assert manage_members_page.is_member_table_displayed(), "List view did not restore the member table"


def test_mms_003_critical_member_search_works_without_blocking_error(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)
    case_data = Config.MANAGE_MEMBERS_SMOKE_TESTDATA["smoke_cases"]["MMS-003"]

    rows = manage_members_page.get_visible_member_row_texts()
    assert rows, "Expected at least one member in the member list"

    manage_members_page.search(case_data["email_search_query"])
    assert manage_members_page.get_member_search_value() == case_data["email_search_query"]
