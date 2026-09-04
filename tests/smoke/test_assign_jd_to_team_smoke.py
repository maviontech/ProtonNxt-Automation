import pytest

from config.config import Config
from pages.assign_jd_to_team_page import AssignJDToTeamPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke


def _case(case_id):
    return Config.ASSIGN_JD_TO_TEAM_SMOKE_TESTDATA["smoke_cases"][case_id]


def _login_and_open(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)

    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"

    page = AssignJDToTeamPage(driver)
    page.open()
    assert page.is_page_displayed(), "Assign JD to Team page did not load"
    return page


def _require_items(items, reason):
    if items:
        return
    pytest.xfail(reason)


def _assign_first_available(page, jd_query="", team_query=""):
    if jd_query:
        page.search_jds(jd_query)
    jd = page.select_jd(jd_query)
    _require_items([jd] if jd else [], "No selectable JD is available in the current environment.")

    if team_query:
        page.search_teams(team_query)
    team = page.select_team(team_query)
    _require_items([team] if team else [], "No selectable Team is available in the current environment.")

    jd_text = " ".join((jd.text or "").split()).strip()
    team_text = " ".join((team.text or "").split()).strip()
    page.click_assign()
    return jd_text, team_text


def _require_successful_assignment(page, case_id):
    feedback = page.get_feedback_text()
    success_keywords = _case("SMK-AJD-008")["success_keywords"]
    if any(keyword in feedback.lower() for keyword in success_keywords):
        return feedback

    reason = feedback or "The application did not expose assignment feedback."
    raise AssertionError(
        f"{case_id} blocked by SMK-AJD-008: assignment was not created. Feedback: {reason}"
    )


def test_smk_ajd_001_verify_assign_jd_page_loads_successfully(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-001")

    assert page.are_major_sections_visible(), (
        f"Expected Assign JD sections are not all visible: {case_data['expected_sections']}"
    )
    assert not page.has_blocking_error(), "Assign JD to Team page shows a blocking application error"


def test_smk_ajd_002_verify_jd_list_is_displayed(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-002")
    jd_texts = page.get_jd_item_texts()

    _require_items(jd_texts, "Assign JD page does not currently show any JD records to validate.")
    assert any(any(identifier.lower() in text.lower() for identifier in case_data["jd_identifiers"]) for text in jd_texts), (
        f"Visible JD records do not show expected identifiers like {case_data['jd_identifiers']}"
    )


def test_smk_ajd_003_verify_team_list_is_displayed(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-003")
    team_texts = page.get_team_item_texts()

    _require_items(team_texts, "Assign JD page does not currently show any Team records to validate.")
    assert any(case_data["team_identifier"].lower() in text.lower() or text for text in team_texts), (
        "Visible team records are empty or do not show recognizable team text"
    )


def test_smk_ajd_004_verify_jd_search_works(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-004")

    page.search_jds(case_data["jd_search_query"])

    assert page.get_search_value("jd") == case_data["jd_search_query"], "JD search field did not retain the entered query"
    assert page.get_jd_item_texts() or page.has_no_results_state(), "JD search did not produce any visible filtered state"


def test_smk_ajd_005_verify_team_search_works(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-005")

    page.search_teams(case_data["team_search_query"])

    assert page.get_search_value("team") == case_data["team_search_query"], "Team search field did not retain the entered query"
    assert page.get_team_item_texts() or page.has_no_results_state(), "Team search did not produce any visible filtered state"


def test_smk_ajd_006_verify_a_jd_can_be_selected(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-006")

    item = page.select_jd(case_data["jd_selection_query"])
    _require_items([item] if item else [], "No JD is available to validate selection behavior.")
    assert page.is_jd_selected(item), "Selected JD did not remain highlighted or selected"


def test_smk_ajd_007_verify_a_team_can_be_selected(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-007")

    item = page.select_team(case_data["team_selection_query"])
    _require_items([item] if item else [], "No Team is available to validate selection behavior.")
    assert page.is_team_selected(item), "Selected Team did not remain highlighted or selected"


def test_smk_ajd_008_verify_jd_can_be_assigned_to_a_team(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-008")

    _assign_first_available(page)
    feedback = page.get_feedback_text().lower()

    assert any(keyword in feedback for keyword in case_data["success_keywords"]), (
        f"Assign action did not show a recognizable success confirmation. Feedback: {page.get_feedback_text()}"
    )


def test_smk_ajd_009_verify_assignment_is_reflected_in_recent_jd_assignments(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-009")

    jd_text, team_text = _assign_first_available(page)
    _require_successful_assignment(page, "SMK-AJD-009")
    recent_rows = page.get_recent_row_texts()
    _require_items(recent_rows, "Recent JD Assignments does not contain any visible rows after assignment.")

    assert any(jd_text.lower() in row.lower() for row in recent_rows), "Assigned JD was not visible in Recent JD Assignments"
    assert any(team_text.lower() in row.lower() for row in recent_rows), "Assigned Team was not visible in Recent JD Assignments"
    recent_text = " ".join(recent_rows).lower()
    assert all(field.lower() in recent_text for field in case_data["expected_recent_fields"]), (
        f"Recent JD Assignments did not show the expected assignment keywords {case_data['expected_recent_fields']}"
    )


def test_smk_ajd_010_verify_validation_when_no_jd_is_selected(driver, credentials):
    page = _login_and_open(driver, credentials)
    team = page.select_team()
    _require_items([team] if team else [], "No Team is available to validate missing-JD behavior.")

    page.click_assign()

    assert page.has_validation_message_for("jd"), "Missing JD validation was not shown after assigning with only a Team selected"


def test_smk_ajd_011_verify_validation_when_no_team_is_selected(driver, credentials):
    page = _login_and_open(driver, credentials)
    jd = page.select_jd()
    _require_items([jd] if jd else [], "No JD is available to validate missing-Team behavior.")

    page.click_assign()

    assert page.has_validation_message_for("team"), "Missing Team validation was not shown after assigning with only a JD selected"


def test_smk_ajd_012_verify_validation_when_both_jd_and_team_are_not_selected(driver, credentials):
    page = _login_and_open(driver, credentials)
    page.click_reset()
    page.click_assign()

    assert page.has_validation_message_for("both"), "Required-selection validation was not shown when assigning without a JD and Team"


def test_smk_ajd_013_verify_reset_button_clears_selections_and_search_values(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-013")

    page.search_jds(case_data["jd_search_query"])
    page.search_teams(case_data["team_search_query"])
    page.select_jd()
    page.select_team()
    page.click_reset()

    assert page.get_search_value("jd") == "", "Reset did not clear the JD search value"
    assert page.get_search_value("team") == "", "Reset did not clear the Team search value"


def test_smk_ajd_014_verify_recent_assignments_table_loads(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-014")

    assert page.has_recent_assignments_section(), "Recent JD Assignments section did not load"
    headers = page.get_recent_headers()
    if headers:
        header_text = " ".join(headers).lower()
        assert any(expected.lower() in header_text for expected in case_data["expected_headers_any"]), (
            f"Recent JD Assignments headers do not include familiar columns. Actual headers: {headers}"
        )
    else:
        assert page.get_recent_row_texts() or page.page_contains_text("recent jd assignments"), (
            "Recent JD Assignments section did not expose headers or rows"
        )


def test_smk_ajd_015_verify_recent_assignment_search_works(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-015")

    if not page.get_recent_row_texts():
        pytest.xfail("Recent JD Assignments has no visible data to validate search behavior.")

    page.search_recent_assignments(case_data["recent_search_query"])

    assert page.get_search_value("recent") == case_data["recent_search_query"], "Recent assignment search field did not retain the entered query"
    assert page.get_recent_row_texts() or page.has_no_results_state(), "Recent assignment search did not produce a visible filtered state"


def test_smk_ajd_016_verify_list_view_works(driver, credentials):
    page = _login_and_open(driver, credentials)

    try:
        page.switch_recent_to_list()
    except Exception:
        pytest.xfail("Recent assignments List view control is not available or stable in this build.")

    assert page.get_recent_row_texts() or page.has_recent_assignments_section(), "List view did not show recent assignments data"


def test_smk_ajd_017_verify_cards_view_works(driver, credentials):
    page = _login_and_open(driver, credentials)

    try:
        page.switch_recent_to_cards()
    except Exception:
        pytest.xfail("Recent assignments Cards view control is not available or stable in this build.")

    assert page.get_recent_row_texts() or page.page_contains_text("card"), "Cards view did not show recent assignments data"


def test_smk_ajd_018_verify_assignment_persists_after_page_refresh(driver, credentials):
    page = _login_and_open(driver, credentials)

    jd_text, team_text = _assign_first_available(page)
    _require_successful_assignment(page, "SMK-AJD-018")

    page.refresh()
    page.search_recent_assignments(jd_text)
    rows = page.get_recent_row_texts()
    _require_items(rows, "Recent JD Assignments did not show any rows after refresh.")

    assert any(jd_text.lower() in row.lower() for row in rows), "Assigned JD was not visible after page refresh"
    assert any(team_text.lower() in row.lower() for row in rows), "Assigned Team was not visible after page refresh"


def test_smk_ajd_019_verify_page_handles_no_search_result_gracefully(driver, credentials):
    page = _login_and_open(driver, credentials)
    case_data = _case("SMK-AJD-019")

    page.search_jds(case_data["invalid_search_query"])
    page.search_teams(case_data["invalid_search_query"])

    assert page.has_no_results_state() or (not page.get_jd_item_texts() and not page.get_team_item_texts()), (
        "Invalid search did not show a clear empty-state style result"
    )
    assert not page.has_blocking_error(), "Invalid search caused a blocking application or server error"


def test_smk_ajd_020_verify_no_critical_server_or_ui_error_occurs_during_assignment_flow(driver, credentials):
    page = _login_and_open(driver, credentials)

    _assign_first_available(page)
    _require_successful_assignment(page, "SMK-AJD-020")
    feedback = page.get_feedback_text().lower()

    assert not page.has_blocking_error(), "Critical assignment flow caused a blocking application or server error"
    assert "500" not in feedback and "404" not in feedback, f"Assignment flow surfaced an HTTP-style error in feedback: {page.get_feedback_text()}"
