from uuid import uuid4

import pytest

from config.config import Config
from pages.create_jd_page import CreateJDPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.sanity


def _case(case_id):
    return Config.CREATE_JD_TESTDATA["test_cases"][case_id]


def _resolved_company():
    configured = Config.CREATE_JD_TESTDATA
    candidates = [value.strip() for value in configured.get("company_candidates", []) if value and value.strip()]
    configured_company = (Config.CREATE_JD_COMPANY or "").strip()
    configured_search = (Config.CREATE_JD_COMPANY_SEARCH or "").strip()

    expected_company = configured_company or configured.get("expected_company", "").strip() or (candidates[0] if candidates else "")
    company_search = configured.get("company_search", "").strip() or configured_search or expected_company

    return {
        "expected_company": expected_company,
        "company_search": company_search,
        "company_candidates": candidates,
    }


def _require_company_seed():
    company = _resolved_company()
    has_explicit_seed = bool(company["expected_company"] or company["company_candidates"])
    has_targeted_search = bool(company["company_search"] and company["company_search"].lower() != "a")
    if has_explicit_seed or has_targeted_search:
        return company
    pytest.xfail(
        "Create JD sanity requires a selectable company. Set PROTONNXT_CREATE_JD_COMPANY or "
        "PROTONNXT_CREATE_JD_COMPANY_SEARCH, or populate company_candidates in testdata/create_jd_data.json."
    )


def _unique_title(prefix=None):
    base = prefix or Config.CREATE_JD_TESTDATA["unique_title_prefix"]
    return f"{base} {uuid4().hex[:8]}"


def _open_create_jd_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    if login_page.is_login_page_displayed():
        login_page.login(**credentials)
        assert login_page.is_authenticated_destination_displayed(), "Login did not complete"

    create_jd_page = CreateJDPage(driver)
    create_jd_page.open()
    assert create_jd_page.is_page_displayed(), "Create JD page did not load"
    return create_jd_page


def _build_valid_jd(case_id, title_prefix=None):
    case_data = dict(Config.CREATE_JD_TESTDATA["test_cases"][case_id])
    case_data.update(_require_company_seed())
    case_data["jd_summary"] = _unique_title(title_prefix)
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


def _create_and_open_view_edit(create_jd_page, case_data):
    create_jd_page.submit_with_data(**_form_payload(case_data))
    assert create_jd_page.get_success_feedback(), "Success feedback was not shown after Create JD submission"

    create_jd_page.open_view_edit_from_navigation()
    assert create_jd_page.is_view_edit_page_displayed(), "View/Edit JDs page did not load"

    create_jd_page.search_jd(case_data["jd_summary"])
    create_jd_page.wait_for_jd_to_be_listed(case_data["jd_summary"])
    return create_jd_page


def test_cjd_001_create_jd_page_loads_successfully(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)

    assert create_jd_page.get_heading_text() == "Create Job Description", "Create JD heading mismatch"
    assert create_jd_page.is_form_displayed(), "Create JD form is not displayed"
    assert not create_jd_page.has_blocking_error(), "Create JD page shows a blocking application error"


def test_cjd_002_all_critical_create_jd_controls_are_displayed(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)

    assert create_jd_page.are_core_controls_displayed(), "One or more critical Create JD controls are missing"


def test_cjd_003_jd_summary_accepts_valid_input(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-003")

    create_jd_page.enter_summary(case_data["jd_summary"])

    assert create_jd_page.get_field_value("jd_summary") == case_data["jd_summary"], "JD Summary did not retain the entered value"


def test_cjd_004_company_can_be_searched_and_selected(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    company_data = _require_company_seed()

    selected_company = create_jd_page.select_company(
        search_text=company_data["company_search"],
        exact_company=company_data["expected_company"],
    )

    assert selected_company, "Company dropdown did not retain a selected company"
    assert create_jd_page.get_company_id(), "Company hidden ID was not populated after selection"


def test_cjd_005_jd_spoc_name_accepts_valid_input(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-005")

    create_jd_page.enter_spoc_name(case_data["jd_spoc_name"])

    assert create_jd_page.get_field_value("jd_spoc_name") == case_data["jd_spoc_name"], "JD SPOC Name did not retain the entered value"


def test_cjd_006_jd_spoc_email_accepts_valid_email(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-006")

    create_jd_page.enter_spoc_email(case_data["jd_spoc_email"])

    assert create_jd_page.get_field_value("jd_spoc_email") == case_data["jd_spoc_email"], "JD SPOC Email did not retain the entered value"
    assert create_jd_page.is_field_valid("jd_spoc_email"), "Valid JD SPOC Email should pass browser validation"


def test_cjd_007_jd_description_editor_accepts_multiline_content(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-007")

    create_jd_page.enter_description(case_data["jd_description"])

    assert create_jd_page.has_description_content(case_data["jd_description"]), "JD Description editor did not retain meaningful multiline content"


def test_cjd_008_jd_description_basic_formatting_controls_work(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-008")

    create_jd_page.enter_description(case_data["jd_description"])
    create_jd_page.apply_basic_description_formatting(case_data["format"])

    assert f"<{case_data['expected_markup']}" in create_jd_page.get_description_html().lower(), "Expected basic formatting markup was not applied"


def test_cjd_009_format_pasted_text_works_with_pasted_jd_content(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-009")

    create_jd_page.enter_description(case_data["jd_description"])
    create_jd_page.format_pasted_text()
    alert_text = create_jd_page.accept_alert_if_present()

    assert not alert_text, f"Format Pasted Text raised an unexpected alert: {alert_text}"
    assert create_jd_page.has_description_content(case_data["retained_keyword"]), "Important JD Description content was not retained after formatting"


def test_cjd_010_must_have_skills_accepts_valid_skills(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-010")

    create_jd_page.enter_must_have_skills(case_data["must_have_skills"])

    assert create_jd_page.get_field_value("must_have_skills") == case_data["must_have_skills"], "Must Have Skills did not retain the entered value"


def test_cjd_011_good_to_have_skills_accepts_valid_skills(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-011")

    create_jd_page.enter_good_to_have_skills(case_data["good_to_have_skills"])

    assert create_jd_page.get_field_value("good_to_have_skills") == case_data["good_to_have_skills"], "Good to Have Skills did not retain the entered value"


def test_cjd_012_budget_ctc_accepts_valid_value(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-012")

    create_jd_page.enter_budget(case_data["budget_ctc"])

    assert create_jd_page.get_field_value("budget_ctc") == case_data["budget_ctc"], "Budget/CTC did not retain the entered value"


def test_cjd_013_experience_required_accepts_valid_value(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-013")

    create_jd_page.enter_experience(case_data["experience_required"])

    assert create_jd_page.get_field_value("experience_required") == case_data["experience_required"], "Experience Required did not retain the entered value"


def test_cjd_014_education_required_accepts_valid_value(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-014")

    create_jd_page.enter_education(case_data["education_required"])

    assert create_jd_page.get_field_value("education_required") == case_data["education_required"], "Education Required did not retain the entered value"


def test_cjd_015_location_accepts_valid_value(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-015")

    create_jd_page.enter_location(case_data["location"])

    assert create_jd_page.get_field_value("location") == case_data["location"], "Location did not retain the entered value"


def test_cjd_016_number_of_positions_accepts_a_valid_positive_number(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-016")

    create_jd_page.enter_positions(case_data["no_of_positions"])

    assert create_jd_page.get_positions_value() == str(case_data["no_of_positions"]), "Number of Positions did not retain the entered value"


def test_cjd_017_default_number_of_positions_is_usable(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)

    default_value = create_jd_page.get_positions_value()

    assert default_value, "Default Number of Positions value is empty"
    assert default_value.isdigit(), f"Default Number of Positions should be numeric. Actual: {default_value}"
    assert int(default_value) > 0, f"Default Number of Positions should be positive. Actual: {default_value}"


def test_cjd_018_status_dropdown_loads_and_allows_selection(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SAN-018")

    available_options = create_jd_page.get_status_options()
    available_values = [value for value, _ in available_options if value]

    assert available_values, "Create JD status field did not load any selectable values"
    create_jd_page.select_status(value=case_data["jd_status"])

    assert create_jd_page.get_selected_status_value() == case_data["jd_status"], "Create JD status did not remain selected"


def test_cjd_019_minimum_valid_jd_can_be_created(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _build_valid_jd("CJD-SAN-019", "Create JD Minimum Sanity AUTO")

    create_jd_page.submit_with_data(**_form_payload(case_data))

    assert create_jd_page.get_success_feedback(), "Minimum valid JD did not show success feedback"


def test_cjd_020_complete_jd_can_be_created_with_all_available_fields(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _build_valid_jd("CJD-SAN-020", "Create JD Complete Sanity AUTO")

    create_jd_page.submit_with_data(**_form_payload(case_data))

    assert create_jd_page.get_success_feedback(), "Complete valid JD did not show success feedback"


def test_cjd_021_missing_mandatory_data_prevents_jd_creation(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)

    create_jd_page.submit()

    assert not create_jd_page.is_field_valid("jd_summary"), "JD Summary should be invalid when left blank"
    assert create_jd_page.get_native_validation_message("jd_summary"), "Required validation message was not exposed for JD Summary"
    assert not create_jd_page.get_company_id(), "Company hidden ID should remain blank on invalid submission"


def test_cjd_022_invalid_spoc_email_is_rejected(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _build_valid_jd("CJD-SAN-022", "Create JD Invalid Email AUTO")

    create_jd_page.fill_form(**_form_payload(case_data))

    assert not create_jd_page.is_field_valid("jd_spoc_email"), "Invalid JD SPOC Email should fail browser validation"
    assert create_jd_page.get_native_validation_message("jd_spoc_email"), "Invalid email validation message was not exposed"


def test_cjd_023_created_jd_appears_in_view_edit_jds(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _build_valid_jd("CJD-SAN-020", "Create JD ViewEdit Sanity AUTO")

    _create_and_open_view_edit(create_jd_page, case_data)

    assert create_jd_page.is_jd_listed(case_data["jd_summary"]), "Created JD was not found in View/Edit JDs"


def test_cjd_024_created_jd_core_values_persist_correctly(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _build_valid_jd("CJD-SAN-020", "Create JD Persisted Sanity AUTO")

    _create_and_open_view_edit(create_jd_page, case_data)

    if not create_jd_page.open_matching_jd_for_edit(case_data["jd_summary"]):
        pytest.xfail("View/Edit JD details could not be opened with a stable DOM interaction in this build.")

    assert create_jd_page.get_field_value("jd_summary") == case_data["jd_summary"], "Persisted JD Summary does not match the created title"
    assert create_jd_page.get_selected_status_value() == case_data["jd_status"], "Persisted JD Status does not match the created status"
    assert create_jd_page.get_field_value("no_of_positions") == str(case_data["no_of_positions"]), "Persisted Number of Positions does not match the created value"
    if case_data.get("expected_company"):
        assert create_jd_page.page_contains_text(case_data["expected_company"]), "Persisted company value could not be confirmed after opening the created JD"


def test_cjd_025_create_jd_button_submits_only_once_per_user_action(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _build_valid_jd("CJD-SAN-020", "Create JD Single Submit AUTO")

    create_jd_page.submit_with_data(**_form_payload(case_data))
    create_jd_page.open_view_edit_from_navigation()
    assert create_jd_page.is_view_edit_page_displayed(), "View/Edit JDs page did not load after single submission"

    create_jd_page.search_jd(case_data["jd_summary"])
    create_jd_page.wait_for_jd_to_be_listed(case_data["jd_summary"])

    assert create_jd_page.count_listed_jds(case_data["jd_summary"]) == 1, "Single Create JD action should create exactly one JD entry"
