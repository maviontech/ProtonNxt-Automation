from datetime import date
from uuid import uuid4

import pytest

from config.config import Config
from pages.create_jd_page import CreateJDPage
from pages.login_page import LoginPage
from pages.view_edit_jds_page import ViewEditJDsPage


pytestmark = pytest.mark.sanity


def _login(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"


def _open_authenticated_page(page, driver, credentials, page_name):
    """Retry once when the application redirects a protected page to Login."""
    page.open()
    if any(element.is_displayed() for element in driver.find_elements(*LoginPage.LOGIN_FORM)):
        _login(driver, credentials)
        page.open()
    assert page.is_page_displayed(), f"{page_name} did not load after authentication"
    return page


def _open_list(driver, credentials):
    _login(driver, credentials)
    page = ViewEditJDsPage(driver)
    return _open_authenticated_page(page, driver, credentials, "View/Edit JDs page")


def _seed_data(**overrides):
    data = dict(Config.VIEW_JD_SANITY_TESTDATA["seed_jd"])
    company = (Config.CREATE_JD_COMPANY or "").strip()
    company_search = (Config.CREATE_JD_COMPANY_SEARCH or "").strip()
    if not company and not company_search:
        pytest.xfail(
            "View JD sanity setup requires PROTONNXT_CREATE_JD_COMPANY or PROTONNXT_CREATE_JD_COMPANY_SEARCH."
        )

    data["jd_summary"] = f"{data['title_prefix']} {uuid4().hex[:8]}"
    data["expected_company"] = company
    data["company_search"] = company_search or company
    data.update(overrides)
    return data


def _create_seeded_jd(driver, credentials, **overrides):
    data = _seed_data(**overrides)
    _login(driver, credentials)
    create_page = CreateJDPage(driver)
    _open_authenticated_page(create_page, driver, credentials, "Create JD page for View JD setup")
    form_fields = {
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
    create_page.submit_with_data(**{key: value for key, value in data.items() if key in form_fields})
    return data


def _open_seeded_jd(driver, credentials, **overrides):
    data = _create_seeded_jd(driver, credentials, **overrides)
    page = ViewEditJDsPage(driver)
    _open_authenticated_page(page, driver, credentials, "View/Edit JDs page for View JD setup")
    page.search(data["jd_summary"])
    row = page.find_matching_result(data["jd_summary"])
    if row is None:
        pytest.xfail("Created JD was not available in View/Edit JDs for View JD validation.")
    data["jd_id"] = page.get_result_details(row)["jd_id"]
    assert page.open_view_for_result(row), "View action did not open the selected JD"
    return page, data, row


def test_viewjd_san_001_view_action_is_available(driver, credentials):
    page = _open_list(driver, credentials)
    row = page.get_first_result()
    assert row is not None, "No JD is available for View action validation"
    assert page.is_action_available_for_result(row, "view"), "View action is not visible and enabled for the JD"


def test_viewjd_san_002_view_opens_selected_jd(driver, credentials):
    page = _open_list(driver, credentials)
    row = page.get_first_result()
    assert row is not None, "No JD is available for View action validation"
    assert page.open_view_for_result(row), "View action did not open the selected JD"
    assert page.is_details_modal_displayed(), "View JD modal did not open"


def test_viewjd_san_003_correct_jd_is_opened(driver, credentials):
    page, data, row = _open_seeded_jd(driver, credentials)
    modal_text = page.get_details_modal_text().lower()
    assert data["jd_summary"].lower() in modal_text, "View modal did not show the selected JD summary"
    assert data["jd_id"].lower() in modal_text, "View modal did not show the selected JD ID"


def test_viewjd_san_004_view_heading_and_close_navigation_are_displayed(driver, credentials):
    page, _, _ = _open_seeded_jd(driver, credentials)
    assert page.page_contains_text("view jd", "job description", "jd details"), "View JD heading is not displayed"
    assert page.is_close_control_displayed(), "View JD Close control is not displayed"


def test_viewjd_san_005_primary_jd_details_are_displayed(driver, credentials):
    page, data, row = _open_seeded_jd(driver, credentials)
    modal_text = page.get_details_modal_text().lower()
    expected_values = [data["jd_summary"], data["jd_status"], str(data["no_of_positions"]), data["jd_id"]]
    for value in expected_values:
        assert value.lower() in modal_text, f"Primary JD value is missing from View JD: {value}"


def test_viewjd_san_006_saved_jd_details_match_source_data(driver, credentials):
    page, data, _ = _open_seeded_jd(driver, credentials)
    modal_text = page.get_details_modal_text().lower()
    for field in ("jd_summary", "must_have_skills", "good_to_have_skills", "budget_ctc", "experience_required", "education_required", "location"):
        assert data[field].lower() in modal_text, f"Saved {field} is missing or mismatched in View JD"


def test_viewjd_san_007_multiline_description_is_readable(driver, credentials):
    page, data, _ = _open_seeded_jd(driver, credentials)
    modal_text = page.get_details_modal_text()
    for line in data["jd_description"].splitlines():
        assert line in modal_text, f"Description line is not readable in View JD: {line}"


def test_viewjd_san_008_long_content_remains_accessible(driver, credentials):
    page, data, _ = _open_seeded_jd(driver, credentials)
    assert len(data["jd_description"]) > 80, "Sanity seed does not contain long content"
    assert data["jd_description"].splitlines()[-1] in page.get_details_modal_text(), "Long View JD content is not accessible"


def test_viewjd_san_009_empty_optional_fields_are_handled(driver, credentials):
    page, _, _ = _open_seeded_jd(driver, credentials, good_to_have_skills="")
    modal_text = page.get_details_modal_text().lower()
    assert "preferred skills" in modal_text, "Optional Preferred Skills field is not displayed"
    assert "null" not in modal_text and "undefined" not in modal_text, "Empty optional field exposes an invalid value"


def test_viewjd_san_010_view_mode_is_read_only(driver, credentials):
    page, _, _ = _open_seeded_jd(driver, credentials)
    assert page.is_view_mode_read_only(), "View JD fields are editable before the user explicitly enters Edit mode"


def test_viewjd_san_011_active_jd_is_displayed_correctly(driver, credentials):
    page, data, _ = _open_seeded_jd(driver, credentials)
    modal_text = page.get_details_modal_text().lower()
    assert data["jd_status"] in modal_text, "Active JD status is not displayed"
    assert "not closed" in modal_text or "closure" in modal_text, "Active JD closure information is not displayed"


def test_viewjd_san_012_closed_or_inactive_jd_is_displayed_correctly(driver, credentials):
    data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    page.search(data["jd_summary"])
    row = page.find_matching_result(data["jd_summary"])
    assert row is not None, "Could not find the seeded JD for closing"
    data["jd_id"] = page.get_result_details(row)["jd_id"]
    assert page.open_edit_for_result(row), "Could not open the seeded JD for closing"

    create_page = CreateJDPage(driver)
    closure_date = date.today().isoformat()
    create_page.enable_edit_mode()
    create_page.select_status(value="closed")
    create_page.enter_closure_date(closure_date)
    assert "updated successfully" in create_page.save_edit().lower(), "Closed JD update was not confirmed"

    driver.get(f"{Config.BASE_URL.rstrip('/')}/view_jd/{data['jd_id']}/")
    page = ViewEditJDsPage(driver)
    assert page.is_details_modal_displayed(), "Closed JD View modal did not open"
    modal_text = page.get_details_modal_text().lower()
    assert "closed" in modal_text and closure_date in modal_text, "Closed JD status or closure date is not displayed"


def test_viewjd_san_013_positions_value_is_exact(driver, credentials):
    page, data, _ = _open_seeded_jd(driver, credentials)
    assert str(data["no_of_positions"]) in page.get_details_modal_text(), "Saved Positions value is not displayed exactly"


def test_viewjd_san_014_refresh_retains_the_correct_jd(driver, credentials):
    page, data, _ = _open_seeded_jd(driver, credentials)
    driver.refresh()
    assert page.is_details_modal_displayed(), "View JD did not reopen after refresh"
    assert data["jd_summary"].lower() in page.get_details_modal_text().lower(), "Refresh opened the wrong JD"


def test_viewjd_san_015_close_returns_to_view_edit_jds(driver, credentials):
    page, _, _ = _open_seeded_jd(driver, credentials)
    assert page.close_details_modal(), "View JD Close control could not be used"
    assert page.is_page_displayed(), "Closing View JD did not return to the View/Edit JDs list"


def test_viewjd_san_016_browser_back_returns_to_jd_list(driver, credentials):
    page, _, _ = _open_seeded_jd(driver, credentials)
    driver.back()
    assert page.is_page_displayed(), "Browser Back did not return to the View/Edit JDs list"


def test_viewjd_san_017_different_jds_do_not_show_stale_data(driver, credentials):
    page = _open_list(driver, credentials)
    rows = page.get_table_rows()
    if len(rows) < 2:
        pytest.xfail("At least two JDs are required for stale-data validation.")

    first_row = rows[0]
    second_row = rows[1]
    first_id = page.get_result_details(first_row)["jd_id"]
    second_id = page.get_result_details(second_row)["jd_id"]
    assert first_id and second_id and first_id != second_id, "Two distinct JD rows are required for stale-data validation"
    assert page.open_view_for_result(first_row), "Could not open the first JD"
    assert first_id.lower() in page.get_details_modal_text().lower(), "First View JD did not show its own ID"
    assert page.close_details_modal(), "Could not close the first View JD"

    second_row = page.wait_for_matching_result(second_id)
    assert second_row is not None, "The second JD was not available after closing the first View JD"
    assert page.open_view_for_result(second_row), "Could not open the second JD"
    second_text = page.get_details_modal_text().lower()
    assert second_id.lower() in second_text, "Second View JD did not show its own ID"
    assert first_id.lower() not in second_text, "Second View JD retained stale details from the first JD"


def test_viewjd_san_018_direct_valid_view_url_opens_jd(driver, credentials):
    data = _create_seeded_jd(driver, credentials)
    page = ViewEditJDsPage(driver)
    page.open()
    page.search(data["jd_summary"])
    row = page.find_matching_result(data["jd_summary"])
    assert row is not None, "Created JD was not found before direct URL validation"
    data["jd_id"] = page.get_result_details(row)["jd_id"]
    driver.get(f"{Config.BASE_URL.rstrip('/')}/view_jd/{data['jd_id']}/")
    page = ViewEditJDsPage(driver)
    assert page.is_details_modal_displayed(), "Valid direct View JD URL did not open the JD"
    assert data["jd_summary"].lower() in page.get_details_modal_text().lower(), "Direct View JD URL opened the wrong JD"


def test_viewjd_san_019_invalid_jd_id_is_handled(driver, credentials):
    _login(driver, credentials)
    driver.get(f"{Config.BASE_URL.rstrip('/')}/view_jd/INVALID_JD_999999/")
    body_text = driver.find_element("tag name", "body").text.lower()
    assert "not found" in body_text or "404" in body_text, "Invalid View JD URL did not show a not-found response"


def test_viewjd_san_020_unauthorized_user_cannot_view_jd_data(driver):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    login_page.clear_session_storage()
    login_page.open_path(ViewEditJDsPage.PAGE_PATH)
    page = ViewEditJDsPage(driver)
    assert not page.is_page_displayed(), "Unauthorized user can access View/Edit JDs data"
    assert login_page.is_authentication_screen_displayed() or page.page_contains_text("access denied", "permission", "unauthorized"), (
        "Unauthorized user was not redirected to login or shown an authorization response"
    )


def test_viewjd_san_021_expired_session_is_handled(driver, credentials):
    page, _, _ = _open_seeded_jd(driver, credentials)
    login_page = LoginPage(driver)
    assert login_page.clear_session_storage(), "Authenticated browser state could not be cleared"
    driver.refresh()

    unauthenticated_page = ViewEditJDsPage(driver)
    assert not unauthenticated_page.is_page_displayed(), "Expired session still exposes View JD data"
    assert login_page.is_authentication_screen_displayed() or unauthenticated_page.page_contains_text(
        "access denied", "permission", "unauthorized"
    ), "Expired session did not redirect to login or show an authorization response"


def test_viewjd_san_022_view_layout_is_usable_at_supported_sizes(driver, credentials):
    page, _, _ = _open_seeded_jd(driver, credentials)
    original_size = driver.get_window_size()
    try:
        for width, height in ((1440, 900), (900, 700)):
            driver.set_window_size(width, height)
            assert page.is_details_modal_displayed(), f"View JD modal is not usable at {width}x{height}"
            assert page.is_close_control_displayed(), f"View JD navigation is not usable at {width}x{height}"
    finally:
        driver.set_window_size(original_size["width"], original_size["height"])
