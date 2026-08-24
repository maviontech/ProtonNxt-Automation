from uuid import uuid4

import pytest
from selenium.common.exceptions import TimeoutException

from config.config import Config
from pages.create_team_page import CreateTeamPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke


def _open_create_team_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)

    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"

    create_team_page = CreateTeamPage(driver)
    create_team_page.open()
    assert create_team_page.is_page_displayed(), "Create Team page did not load"
    return create_team_page


def _unique_team_name():
    prefix = Config.CREATE_TEAM_SMOKE_TESTDATA["smoke_cases"]["CTS-003"]["unique_team_prefix"]
    return f"{prefix} {uuid4().hex[:8]}"


def test_cts_001_application_login_and_create_team_page_load(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    case_data = Config.CREATE_TEAM_SMOKE_TESTDATA["smoke_cases"]["CTS-001"]

    assert create_team_page.is_team_name_required(), "Team Name should be mandatory"
    assert create_team_page.get_team_name_maxlength() == case_data["team_name_maxlength"], (
        "Team Name maxlength mismatch"
    )


def test_cts_002_create_team_controls_are_visible_and_clickable(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    case_data = Config.CREATE_TEAM_SMOKE_TESTDATA["smoke_cases"]["CTS-002"]

    create_team_page.search_members(case_data["member_search_query"])
    assert create_team_page.get_member_search_value() == case_data["member_search_query"]

    create_team_page.search_teams(case_data["team_search_query"])
    assert create_team_page.get_team_search_value() == case_data["team_search_query"]


def test_cts_003_basic_team_can_be_created(driver, credentials):
    create_team_page = _open_create_team_page(driver, credentials)
    team_name = _unique_team_name()
    case_data = Config.CREATE_TEAM_SMOKE_TESTDATA["smoke_cases"]["CTS-003"]

    assert create_team_page.has_available_members(), (
        "Create Team smoke requires at least one available member row before submission."
    )

    create_team_page.create_team(team_name)

    try:
        result = create_team_page.wait_for_team_creation_result(
            team_name,
            case_data["expected_success_keyword"],
        )
    except TimeoutException as error:
        raise AssertionError(
            f"Team '{team_name}' did not reach a success or error state in time. "
            f"Visible alerts: {create_team_page.get_alert_texts() or 'None'}. "
            f"Current page text: {create_team_page.get_page_text()}"
        ) from error

    assert result["status"] == "success", (
        f"Create Team smoke failed for '{team_name}'. "
        f"Detected result: {result['details']}"
    )
    assert create_team_page.page_contains_text(case_data["expected_success_keyword"]), (
        f"Expected success keyword was not shown. Current page text: {create_team_page.get_page_text()}"
    )
    assert create_team_page.is_team_listed(team_name), (
        f"New team '{team_name}' is missing from Existing Teams. Current page text: "
        f"{create_team_page.get_page_text()}"
    )
