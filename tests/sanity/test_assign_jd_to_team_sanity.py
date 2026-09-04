import pytest

from config.config import Config
from pages.assign_jd_to_team_page import AssignJDToTeamPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.sanity


def _case(case_id):
    return Config.ASSIGN_JD_TO_TEAM_SANITY_TESTDATA["sanity_cases"][case_id]


def _login_and_open(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"

    page = AssignJDToTeamPage(driver)
    page.open()
    assert page.is_page_displayed(), "Assign JD to Team page did not load"
    return page


def _require_item(item, message):
    assert item is not None, message
    return item


def _assign_first_available(page, jd_query="", team_query=""):
    if jd_query:
        page.search_jds(jd_query)
    jd = _require_item(page.select_jd(jd_query), "No selectable JD is available.")

    if team_query:
        page.search_teams(team_query)
    team = _require_item(page.select_team(team_query), "No selectable Team is available.")

    jd_text = " ".join((jd.text or "").split()).strip()
    team_text = " ".join((team.text or "").split()).strip()
    page.click_assign()
    return jd_text, team_text


def test_san_ajd_001_verify_assign_jd_to_team_page_loads_successfully(driver, credentials):
    page = _login_and_open(driver, credentials)

    assert page.are_major_sections_visible(), "Assignment Details and Recent JD Assignments sections are not visible"
    assert not page.has_blocking_error(), "Assign JD to Team page shows a blocking application error"


def test_san_ajd_002_verify_jd_list_is_displayed_and_selectable(driver, credentials):
    page = _login_and_open(driver, credentials)
    item = _require_item(page.select_jd(_case("SAN-AJD-002")["jd_selection_query"]), "No active JD is available.")

    assert page.is_jd_selected(item), "Selected JD is not highlighted or selected"


def test_san_ajd_003_verify_jd_search_filters_the_jd_list(driver, credentials):
    page = _login_and_open(driver, credentials)
    query = _case("SAN-AJD-003")["jd_search_query"]
    page.search_jds(query)
    items = page.get_jd_item_texts()

    assert items, "JD search returned no matching records"
    assert all(query.lower() in item.lower() for item in items), "JD search returned a non-matching record"
    assert page.is_jd_selected(_require_item(page.select_jd(query), "Matching JD cannot be selected."))


def test_san_ajd_004_verify_team_list_is_displayed_and_selectable(driver, credentials):
    page = _login_and_open(driver, credentials)
    item = _require_item(page.select_team(_case("SAN-AJD-004")["team_selection_query"]), "No Team is available.")

    assert page.is_team_selected(item), "Selected Team is not highlighted or selected"


def test_san_ajd_005_verify_team_search_filters_the_team_list(driver, credentials):
    page = _login_and_open(driver, credentials)
    query = _case("SAN-AJD-005")["team_search_query"]
    page.search_teams(query)
    items = page.get_team_item_texts()

    assert items, "Team search returned no matching records"
    assert all(query.lower() in item.lower() for item in items), "Team search returned a non-matching record"
    assert page.is_team_selected(_require_item(page.select_team(query), "Matching Team cannot be selected."))


def test_san_ajd_006_verify_valid_jd_to_team_assignment(driver, credentials):
    page = _login_and_open(driver, credentials)
    _assign_first_available(page)

    assert not page.has_blocking_error(), "Assignment produced a blocking application error"


def test_san_ajd_007_verify_success_confirmation_after_assignment(driver, credentials):
    page = _login_and_open(driver, credentials)
    _assign_first_available(page)
    feedback = page.get_feedback_text().lower()

    assert any(keyword in feedback for keyword in _case("SAN-AJD-007")["success_keywords"]), (
        f"Assignment did not show a recognizable success confirmation. Feedback: {page.get_feedback_text()}"
    )


def test_san_ajd_008_verify_assigned_team_is_reflected_in_recent_jd_assignments(driver, credentials):
    page = _login_and_open(driver, credentials)
    jd_text, team_text = _assign_first_available(page)
    rows = page.get_recent_row_texts()

    assert any(jd_text.lower() in row.lower() and team_text.lower() in row.lower() for row in rows), (
        "The assigned JD and Team are not shown together in Recent JD Assignments"
    )


def test_san_ajd_009_verify_validation_when_team_is_selected_but_jd_is_missing(driver, credentials):
    page = _login_and_open(driver, credentials)
    _require_item(page.select_team(), "No Team is available.")
    page.click_assign()

    assert page.has_validation_message_for("jd"), "Missing JD validation was not shown"


def test_san_ajd_010_verify_validation_when_jd_is_selected_but_team_is_missing(driver, credentials):
    page = _login_and_open(driver, credentials)
    _require_item(page.select_jd(), "No JD is available.")
    page.click_assign()

    assert page.has_validation_message_for("team"), "Missing Team validation was not shown"


def test_san_ajd_011_verify_validation_when_both_jd_and_team_are_missing(driver, credentials):
    page = _login_and_open(driver, credentials)
    page.click_reset()
    page.click_assign()

    assert page.has_validation_message_for("both"), "Required-selection validation was not shown"


def test_san_ajd_012_verify_reset_clears_current_selections_and_searches(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SAN-AJD-012")
    page.search_jds(case_data["jd_search_query"])
    page.search_teams(case_data["team_search_query"])
    _require_item(page.select_jd(), "No JD is available.")
    _require_item(page.select_team(), "No Team is available.")
    page.click_reset()

    assert page.get_search_value("jd") == "", "Reset did not clear the JD search"
    assert page.get_search_value("team") == "", "Reset did not clear the Team search"
    assert not page.has_jd_selection(), "Reset did not clear the JD selection"
    assert not page.has_team_selection(), "Reset did not clear the Team selection"


def test_san_ajd_013_verify_recent_jd_assignments_search(driver, credentials):
    page = _login_and_open(driver, credentials)
    assert page.get_recent_row_texts(), "Recent assignment records are required for this sanity check"
    query = _case("SAN-AJD-013")["recent_search_query"]
    page.search_recent_assignments(query)

    assert page.get_search_value("recent") == query, "Recent-assignment search did not retain the query"
    assert page.get_recent_row_texts() or page.has_no_results_state(), "Recent-assignment search did not show a filtered state"


def test_san_ajd_014_verify_list_and_cards_view_toggle(driver, credentials):
    page = _login_and_open(driver, credentials)
    page.switch_recent_to_cards()
    assert page.page_contains_text("card"), "Cards view did not open"
    page.switch_recent_to_list()

    assert page.has_recent_assignments_section(), "List view did not open correctly"
    assert not page.has_blocking_error(), "View toggle caused a blocking application error"


def test_san_ajd_015_verify_page_remains_stable_after_assignment_and_reset(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SAN-AJD-015")
    _assign_first_available(page)
    page.click_reset()
    page.search_jds(case_data["jd_search_query"])
    page.search_teams(case_data["team_search_query"])
    _require_item(page.select_jd(), "JD could not be selected after Reset.")
    _require_item(page.select_team(), "Team could not be selected after Reset.")

    assert not page.has_blocking_error(), "Assignment/reset operations left the page in a broken state"
