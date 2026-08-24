from uuid import uuid4

import pytest

from config.config import Config
from pages.create_team_page import CreateTeamPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.sanity


def _open_create_team_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    if login_page.is_login_page_displayed():
        login_page.login(**credentials)
        assert login_page.is_authenticated_destination_displayed(), "Login did not complete"

    create_team_page = CreateTeamPage(driver)
    create_team_page.open()
    assert create_team_page.is_page_displayed(), "Create Team page did not load"
    return create_team_page


def _unique_team_name():
    prefix = Config.CREATE_TEAM_TESTDATA["unique_team_prefix"]
    return f"{prefix} {uuid4().hex[:8]}"


def test_ctm_001_create_team_page_loads_successfully(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)

    assert create_team_page.is_team_name_required(), "Team Name should be mandatory"
    assert create_team_page.get_team_name_maxlength() == "100", "Team Name maxlength should be 100"


def test_ctm_002_blank_team_name_is_rejected(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    create_team_page.fill_team_name("")

    assert not create_team_page.is_team_name_valid(), "Blank Team Name should be invalid"
    assert create_team_page.get_team_name_validation_message(), "Required validation message is missing"


def test_ctm_003_member_is_required_to_create_a_team(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    create_team_page.fill_team_name(_unique_team_name())
    create_team_page.select_first_team_lead()
    create_team_page.submit()

    create_team_page.wait_for_page_text("Select at least one member")
    assert create_team_page.page_contains_text("Select at least one member")


def test_ctm_004_team_lead_is_required_to_create_a_team(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    create_team_page.fill_team_name(_unique_team_name())
    create_team_page.select_first_member()
    create_team_page.submit()

    create_team_page.wait_for_page_text("Team lead must be selected")
    assert create_team_page.page_contains_text("Team lead must be selected")


def test_ctm_005_valid_team_can_be_created(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    team_name = _unique_team_name()
    create_team_page.create_team(team_name)

    create_team_page.wait_for_page_text("created successfully")
    assert create_team_page.page_contains_text(f"Team '{team_name}' created successfully")
    assert create_team_page.is_team_listed(team_name), "New team is missing from Existing Teams"


def test_ctm_006_duplicate_team_name_is_rejected(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    team_name = _unique_team_name()
    create_team_page.create_team(team_name)
    create_team_page.wait_for_page_text("created successfully")

    create_team_page.create_team(team_name)
    create_team_page.wait_for_page_text("already exists")
    assert create_team_page.page_contains_text("A team with this name already exists")


def test_ctm_007_member_search_accepts_query(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    query = Config.CREATE_TEAM_TESTDATA["member_search_query"]

    create_team_page.search_members(query)

    assert create_team_page.get_member_search_value() == query


def test_ctm_008_existing_team_search_accepts_query(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    query = Config.CREATE_TEAM_TESTDATA["team_search_query"]

    create_team_page.search_teams(query)

    assert create_team_page.get_team_search_value() == query
