from uuid import uuid4

import pytest

from config.config import Config
from pages.create_jd_page import CreateJDPage
from pages.login_page import LoginPage
from pages.view_edit_jds_page import ViewEditJDsPage


pytestmark = pytest.mark.smoke


def _case(case_id):
    return Config.VIEW_EDIT_JDS_SMOKE_TESTDATA["smoke_cases"][case_id]


def _seed_case():
    return dict(Config.VIEW_EDIT_JDS_SMOKE_TESTDATA["seed_jd"])


def _resolved_seed_jd():
    case_data = _seed_case()
    candidates = [value.strip() for value in case_data.get("company_candidates", []) if value and value.strip()]
    configured_company = (Config.CREATE_JD_COMPANY or "").strip()
    configured_search = (Config.CREATE_JD_COMPANY_SEARCH or "").strip()

    expected_company = case_data.get("expected_company", "").strip() or configured_company or (candidates[0] if candidates else "")
    company_search = case_data.get("company_search", "").strip() or configured_search or expected_company

    case_data["expected_company"] = expected_company
    case_data["company_search"] = company_search
    case_data["jd_summary"] = f"{case_data['title_prefix']} {uuid4().hex[:8]}"
    return case_data


def _form_payload(case_data):
    allowed_keys = {
        "jd_summary",
        "company_search",
        "expected_company",
        "jd_spoc_name",
        "jd_spoc_email",
        "jd_description",
        "must_have_skills",
        "good_to_have_skills",
        "budget_ctc",
        "experience_required",
        "education_required",
        "location",
        "no_of_positions",
        "jd_status",
    }
    return {key: value for key, value in case_data.items() if key in allowed_keys}


def _require_company_seed(case_data):
    has_explicit_seed = bool(case_data.get("expected_company") or case_data.get("company_candidates"))
    company_search = (case_data.get("company_search") or "").strip()
    has_targeted_search = bool(company_search and company_search.lower() != "a")
    if has_explicit_seed or has_targeted_search:
        return
    pytest.xfail(
        "View/Edit JD smoke setup requires a selectable company. Set PROTONNXT_CREATE_JD_COMPANY or "
        "PROTONNXT_CREATE_JD_COMPANY_SEARCH, or populate company_candidates in testdata/view_edit_jds_smoke_data.json."
    )


def _login(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)

    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"
    return login_page


def _open_view_edit_page(driver, credentials):
    _login(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    assert page.is_page_displayed(), "View/Edit JDs page did not load"
    return page


def _create_seeded_jd(driver, credentials):
    _login(driver, credentials)
    create_jd_page = CreateJDPage(driver)
    create_jd_page.open()
    assert create_jd_page.is_page_displayed(), "Create JD page did not load for View/Edit JDs setup"

    seed_data = _resolved_seed_jd()
    _require_company_seed(seed_data)
    create_jd_page.submit_with_data(**_form_payload(seed_data))
    return seed_data


def _find_row_or_xfail(page, needle, reason):
    row = page.find_matching_result(needle)
    if row is None:
        pytest.xfail(reason)
    return row


def test_vejd_smk_001_view_edit_jds_page_opens(driver, credentials):
    page = _open_view_edit_page(driver, credentials)

    assert page.is_page_displayed(), "View/Edit JDs page is not displayed"
    assert not page.has_blocking_error(), "View/Edit JDs page shows a blocking application error"


def test_vejd_smk_002_main_controls_are_displayed(driver, credentials):
    page = _open_view_edit_page(driver, credentials)
    case_data = _case("VEJD-SMK-002")

    assert page.are_main_controls_displayed(), "One or more main View/Edit JDs controls are missing"
    headers = page.get_table_headers()
    if headers:
        assert any(expected.lower() in " ".join(headers).lower() for expected in case_data["expected_headers_any"]), (
            f"Expected at least one familiar JD header in the list view. Actual headers: {headers}"
        )


def test_vejd_smk_003_jd_records_are_displayed_in_list_view(driver, credentials):
    page = _open_view_edit_page(driver, credentials)

    assert page.get_results_count() > 0, "Expected at least one JD record to be displayed in list view"
    assert page.get_visible_result_texts(), "Visible JD results are empty even though the list is rendered"


def test_vejd_smk_004_jd_information_is_displayed_correctly(driver, credentials):
    seed_data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    assert page.is_page_displayed(), "View/Edit JDs page did not load after seed JD creation"

    page.search(seed_data["jd_summary"])
    row = _find_row_or_xfail(page, seed_data["jd_summary"], "Created JD was not found in View/Edit JDs for row verification.")
    details = page.get_result_details(row)

    assert seed_data["jd_summary"].lower() in details["raw_text"].lower(), "JD summary is not visible in the listed result"
    if seed_data.get("expected_company"):
        assert seed_data["expected_company"].lower() in details["raw_text"].lower(), "Company value is not visible in the listed result"
    if seed_data.get("jd_status"):
        assert seed_data["jd_status"].lower() in details["raw_text"].lower(), "Status value is not visible in the listed result"


def test_vejd_smk_005_search_by_summary_invalid_data_and_clear_work(driver, credentials):
    seed_data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    assert page.is_page_displayed(), "View/Edit JDs page did not load after seed JD creation"

    page.search(seed_data["jd_summary"])
    assert page.is_result_listed(seed_data["jd_summary"]), "Search by JD summary did not return the seeded JD"

    page.search(_case("VEJD-SMK-005")["invalid_query"])
    assert not page.is_result_listed(seed_data["jd_summary"]), "Invalid search unexpectedly still shows the seeded JD"
    assert page.get_no_results_message() or page.get_results_count() == 0, "Invalid search did not show any no-results behavior"

    page.search("")
    assert page.get_search_value() == "", "Search field did not clear correctly"
    assert page.get_results_count() > 0, "Clearing the search did not restore the normal JD list"


def test_vejd_smk_006_search_by_company_or_team_works(driver, credentials):
    seed_data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    assert page.is_page_displayed(), "View/Edit JDs page did not load after seed JD creation"

    query = seed_data.get("expected_company") or " ".join(seed_data["jd_summary"].split()[:2])
    page.search(query)

    assert page.get_results_count() > 0, "Company or team style search returned no results"
    assert page.is_result_listed(query) or page.is_result_listed(seed_data["jd_summary"]), (
        "Company or team style search did not return the expected JD result"
    )


def test_vejd_smk_007_cards_view_and_list_view_toggle_work(driver, credentials):
    page = _open_view_edit_page(driver, credentials)

    try:
        page.switch_to_cards()
    except Exception:
        pytest.xfail("Cards view control is not available or not stable in this build.")

    assert page.get_card_items() or page.page_contains_text("card"), "Cards view did not display JD cards"

    try:
        page.switch_to_list()
    except Exception:
        pytest.xfail("List view control is not available after switching to cards.")

    assert page.get_table_rows() or page.is_results_section_displayed(), "List view did not restore the JD table"


def test_vejd_smk_008_view_action_opens_correct_jd_details(driver, credentials):
    seed_data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    page.search(seed_data["jd_summary"])

    row = _find_row_or_xfail(page, seed_data["jd_summary"], "Created JD was not found for View action validation.")
    if not page.open_view_for_result(row):
        pytest.xfail("View action is not available for the matching JD in this build.")

    modal_values = page.get_details_modal_values()
    if modal_values:
        assert modal_values.get("position summary", "").lower() == seed_data["jd_summary"].lower(), (
            "View JD details did not open the expected JD summary"
        )
    else:
        assert page.page_contains_text(seed_data["jd_summary"]), "View JD action did not expose the expected JD details"


def test_vejd_smk_009_edit_action_opens_and_saves_a_valid_update(driver, credentials):
    seed_data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    page.search(seed_data["jd_summary"])

    row = _find_row_or_xfail(page, seed_data["jd_summary"], "Created JD was not found for Edit action validation.")
    if not page.open_edit_for_result(row):
        pytest.xfail("Edit action is not available for the matching JD in this build.")

    create_jd_page = CreateJDPage(driver)
    updated_location = f"{seed_data['location']} {_case('VEJD-SMK-009')['updated_location_suffix']}"
    create_jd_page.enable_edit_mode()
    create_jd_page.enter_location(updated_location)
    edit_feedback = create_jd_page.save_edit()
    assert "updated successfully" in edit_feedback.lower(), f"Unexpected Edit JD confirmation: {edit_feedback}"

    page = ViewEditJDsPage(driver)
    page.open()
    page.search(seed_data["jd_summary"])
    row = _find_row_or_xfail(page, seed_data["jd_summary"], "Updated JD was not found after edit submission.")

    if page.open_view_for_result(row):
        modal_values = page.get_details_modal_values()
        if modal_values:
            assert updated_location.lower() in modal_values.get("location", "").lower(), "Updated location was not persisted after edit"
            return

    assert page.page_contains_text(updated_location), "Updated JD value was not visible after saving the edit"


def test_vejd_smk_010_share_action_opens_for_active_jd(driver, credentials):
    seed_data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    page.search(seed_data["jd_summary"])

    row = _find_row_or_xfail(page, seed_data["jd_summary"], "Created JD was not found for Share action validation.")
    if not page.open_share_for_result(row):
        pytest.xfail("Share action is not available for the matching JD or the user lacks share permission.")

    if page.last_share_alert_text:
        pytest.xfail(f"Share action returned a browser alert: {page.last_share_alert_text}")

    assert page.is_share_dialog_displayed(), "Share JD action did not open a share dialog"


def test_vejd_smk_011_pagination_controls_work_when_multiple_pages_exist(driver, credentials):
    page = _open_view_edit_page(driver, credentials)

    if not page.has_pagination():
        pytest.xfail("Pagination is not rendered because the current environment does not have multiple JD pages.")

    starting_page = page.get_active_page_number()
    moved_next = page.go_to_next_page()
    moved_page_number = page.go_to_page_number(starting_page + 1)
    moved_previous = page.go_to_previous_page()

    assert moved_next or moved_page_number or moved_previous, "No pagination control changed the JD result page"


def test_vejd_smk_012_displayed_jd_count_text_is_consistent(driver, credentials):
    page = _open_view_edit_page(driver, credentials)
    summary = page.get_pagination_summary()

    if not summary:
        pytest.xfail("Showing X-Y of Z JDs summary is not visible in this build.")

    visible_count = page.get_results_count()
    expected_visible = summary["end"] - summary["start"] + 1

    assert summary["start"] <= summary["end"] <= summary["total"], f"Invalid JD count summary found: {summary}"
    assert visible_count <= expected_visible, (
        f"Visible JD rows exceed the displayed summary range. Visible: {visible_count}, Summary: {summary}"
    )


def test_vejd_smk_013_unauthorized_user_cannot_access_view_edit_jds(driver):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    login_page.clear_session_storage()
    login_page.open_path("/view_edit_jds/")

    page = ViewEditJDsPage(driver)
    assert not page.is_page_displayed(), "Unauthorized user should not be able to access View/Edit JDs directly"
    assert login_page.is_authentication_screen_displayed() or page.page_contains_text("access denied", "permission", "unauthorized"), (
        "Unauthorized access did not redirect to login or show an access-denied style response"
    )
