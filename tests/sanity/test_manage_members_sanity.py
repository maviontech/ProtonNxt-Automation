import pytest

from config.config import Config
from pages.login_page import LoginPage
from pages.manage_members_page import ManageMembersPage


pytestmark = pytest.mark.sanity


def _open_manage_members_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    if login_page.is_login_page_displayed():
        login_page.login(**credentials)
        assert login_page.is_authenticated_destination_displayed(), "Login did not complete"

    manage_members_page = ManageMembersPage(driver)
    manage_members_page.open()
    assert manage_members_page.is_page_displayed(), "Manage Members page did not load"
    return manage_members_page


def test_mtm_001_manage_members_page_loads_successfully(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)

    assert manage_members_page.is_member_table_displayed(), "Member list table is not displayed"
    assert manage_members_page.get_table_headers() == Config.MANAGE_MEMBERS_TESTDATA["expected_headers"]


def test_mtm_002_member_list_displays_existing_members(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)

    rows = manage_members_page.get_visible_member_row_texts()
    assert rows, "Expected at least one member in the member list"
    for row in rows:
        assert row, "A member row should contain member details"


def test_mtm_003_member_search_filters_by_name(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)
    member_name = Config.MANAGE_MEMBERS_TESTDATA["member_search"]["name_query"]

    manage_members_page.search(member_name)

    assert manage_members_page.get_member_search_value() == member_name


def test_mtm_004_member_search_accepts_email(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)
    email = Config.MANAGE_MEMBERS_TESTDATA["member_search"]["email_query"]

    manage_members_page.search(email)

    assert manage_members_page.get_member_search_value() == email


def test_mtm_005_global_search_accepts_query(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)
    query = Config.MANAGE_MEMBERS_TESTDATA["global_search_query"]

    manage_members_page.search_globally(query)

    assert manage_members_page.get_global_search_value() == query


def test_mtm_006_list_and_cards_view_controls_are_available(driver, credentials):
    manage_members_page = _open_manage_members_page(driver, credentials)

    manage_members_page.switch_to_cards()
    assert manage_members_page.is_page_displayed(), "Manage Members page disappeared after switching to Cards view"

    manage_members_page.switch_to_list()
    assert manage_members_page.is_member_table_displayed(), "List view did not restore the member table"
