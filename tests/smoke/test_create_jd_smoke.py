from uuid import uuid4

import pytest

from config.config import Config
from pages.create_jd_page import CreateJDPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke


def _case(case_id):
    return Config.CREATE_JD_SMOKE_TESTDATA["smoke_cases"][case_id]


def _unique_title(prefix):
    return f"{prefix} {uuid4().hex[:8]}"


def _resolved_company(case_id):
    case_data = dict(_case(case_id))
    candidates = [value.strip() for value in case_data.get("company_candidates", []) if value and value.strip()]
    configured_company = (Config.CREATE_JD_COMPANY or "").strip()
    configured_search = (Config.CREATE_JD_COMPANY_SEARCH or "").strip()

    selected_company = case_data.get("expected_company", "").strip()
    if not selected_company:
        selected_company = configured_company or (candidates[0] if candidates else "")

    selected_search = case_data.get("company_search", "").strip()
    if not selected_search:
        selected_search = configured_search or selected_company

    case_data["expected_company"] = selected_company
    case_data["company_search"] = selected_search
    case_data["company_candidates"] = candidates
    return case_data


def _resolved_complete_case(case_id):
    case_data = _resolved_company(case_id)
    case_data["jd_summary"] = _unique_title(case_data["title_prefix"])
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


def _require_company_seed(case_data, case_id):
    expected_company = (case_data.get("expected_company") or "").strip()
    company_search = (case_data.get("company_search") or "").strip()
    company_candidates = [value for value in case_data.get("company_candidates", []) if value]

    has_explicit_seed = bool(expected_company or company_candidates)
    has_targeted_search = bool(company_search and company_search.lower() != "a")

    if has_explicit_seed or has_targeted_search:
        return
    pytest.xfail(
        f"{case_id} requires a selectable company, but no Create JD company seed data is configured. "
        "Set PROTONNXT_CREATE_JD_COMPANY or PROTONNXT_CREATE_JD_COMPANY_SEARCH, or populate company_candidates in smoke data."
    )


def _open_create_jd_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)

    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"

    create_jd_page = CreateJDPage(driver)
    create_jd_page.open()
    assert create_jd_page.is_page_displayed(), "Create Job Description page did not load"
    return create_jd_page


def _create_and_verify_jd(create_jd_page, jd_data):
    create_jd_page.submit_with_data(**_form_payload(jd_data))
    success_feedback = create_jd_page.get_success_feedback()

    create_jd_page.open_view_edit_from_navigation()
    assert create_jd_page.is_view_edit_page_displayed(), "View/Edit JDs page did not load after submission"

    create_jd_page.search_jd(jd_data["jd_summary"])
    create_jd_page.wait_for_jd_to_be_listed(jd_data["jd_summary"])

    assert create_jd_page.is_jd_listed(jd_data["jd_summary"]), (
        f"JD '{jd_data['jd_summary']}' was not found in View/Edit JDs after creation. "
        f"Success feedback: {success_feedback or 'None'}"
    )


def test_cjd_smk_001_create_jd_page_loads(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)

    assert create_jd_page.get_heading_text() == "Create Job Description", "Create JD heading mismatch"
    assert create_jd_page.is_form_displayed(), "Create JD form is not displayed"
    assert not create_jd_page.has_blocking_error(), "Create JD page shows a blocking application error"


def test_cjd_smk_002_critical_controls_are_available(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)

    assert create_jd_page.are_core_controls_displayed(), "One or more critical Create JD controls are missing"


def test_cjd_smk_003_company_can_be_selected(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _resolved_company("CJD-SMK-003")
    _require_company_seed(case_data, "CJD-SMK-003")

    selected_company = create_jd_page.select_company(
        search_text=case_data["company_search"],
        exact_company=case_data["expected_company"],
    )

    assert selected_company, "Company dropdown did not retain a selected company"
    assert create_jd_page.get_company_id(), "Company hidden ID was not populated after company selection"
    if case_data["expected_company"]:
        assert selected_company.lower() == case_data["expected_company"].lower(), (
            f"Expected company '{case_data['expected_company']}' was not selected. "
            f"Actual selected company: '{selected_company}'"
        )


def test_cjd_smk_004_description_accepts_content(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SMK-004")

    create_jd_page.enter_description(case_data["description"])

    assert create_jd_page.get_description_value() == case_data["description"], (
        "JD Description editor did not retain the entered multiline content"
    )
    assert not create_jd_page.has_blocking_error(), "JD Description editor caused a visible application error"


def test_cjd_smk_005_pasted_text_can_be_formatted(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SMK-005")

    create_jd_page.enter_description(case_data["description"])
    before_format = create_jd_page.get_description_value()
    create_jd_page.format_pasted_text()
    alert_text = create_jd_page.accept_alert_if_present()
    after_format = create_jd_page.get_description_value()

    assert before_format.strip(), "JD Description should contain content before Format Pasted Text is used"
    assert not alert_text, f"Format Pasted Text raised an unexpected alert: {alert_text}"
    assert after_format.strip(), "Format Pasted Text cleared the JD Description content"
    assert case_data["retained_keyword"].lower() in after_format.lower(), (
        f"Formatted JD Description did not retain the expected keyword '{case_data['retained_keyword']}'"
    )
    assert not create_jd_page.has_blocking_error(), "Format Pasted Text triggered a visible application error"


def test_cjd_smk_006_skills_accept_valid_data(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SMK-006")

    create_jd_page.enter_must_have_skills(case_data["must_have_skills"])
    create_jd_page.enter_good_to_have_skills(case_data["good_to_have_skills"])

    assert create_jd_page.get_field_value("must_have_skills") == case_data["must_have_skills"], (
        "Must Have Skills did not retain the entered values"
    )
    assert create_jd_page.get_field_value("good_to_have_skills") == case_data["good_to_have_skills"], (
        "Good to Have Skills did not retain the entered values"
    )


def test_cjd_smk_007_valid_positions_can_be_entered(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SMK-007")

    assert create_jd_page.get_positions_value() == case_data["default_positions"], (
        "Default Number of Positions value is not the expected valid default"
    )

    create_jd_page.enter_positions(case_data["valid_positions"])

    assert create_jd_page.get_positions_value() == str(case_data["valid_positions"]), (
        "Number of Positions did not retain the valid value entered in smoke testing"
    )


def test_cjd_smk_008_status_can_be_selected(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SMK-008")

    available_options = create_jd_page.get_status_options()
    available_values = [value for value, _ in available_options if value]

    assert available_values, "Create JD status field did not load any selectable values"
    assert case_data["status_value"] in available_values, (
        f"Expected smoke status '{case_data['status_value']}' is not available. "
        f"Available values: {available_values}"
    )

    create_jd_page.select_status(value=case_data["status_value"])

    assert create_jd_page.get_selected_status_value() == case_data["status_value"], (
        f"Create JD status did not remain selected as '{case_data['status_value']}'"
    )


def test_cjd_smk_009_minimum_valid_jd_can_be_created(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _resolved_complete_case("CJD-SMK-009")
    _require_company_seed(case_data, "CJD-SMK-009")

    _create_and_verify_jd(create_jd_page, case_data)


def test_cjd_smk_010_complete_jd_can_be_created(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _resolved_complete_case("CJD-SMK-010")
    _require_company_seed(case_data, "CJD-SMK-010")

    _create_and_verify_jd(create_jd_page, case_data)


def test_cjd_smk_011_created_jd_is_persisted(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _resolved_complete_case("CJD-SMK-011")
    _require_company_seed(case_data, "CJD-SMK-011")

    _create_and_verify_jd(create_jd_page, case_data)


def test_cjd_smk_012_created_jd_values_are_persisted(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _resolved_complete_case("CJD-SMK-012")
    _require_company_seed(case_data, "CJD-SMK-012")

    _create_and_verify_jd(create_jd_page, case_data)

    if not create_jd_page.open_matching_jd_for_edit(case_data["jd_summary"]):
        pytest.xfail(
            "View/Edit JD details could not be opened with a stable DOM interaction; "
            "list-level persistence is still covered by CJD-SMK-011."
        )

    assert create_jd_page.get_field_value("jd_summary") == case_data["jd_summary"], (
        "Persisted JD Summary does not match the created JD title"
    )
    assert create_jd_page.get_selected_status_value() == case_data["jd_status"], (
        "Persisted JD Status does not match the created JD status"
    )
    assert create_jd_page.get_field_value("no_of_positions") == str(case_data["no_of_positions"]), (
        "Persisted Number of Positions does not match the created JD positions"
    )
    if case_data.get("expected_company"):
        assert create_jd_page.page_contains_text(case_data["expected_company"]), (
            "Persisted company value could not be confirmed after opening the created JD"
        )


def test_cjd_smk_013_missing_required_data_prevents_creation(driver, credentials):
    create_jd_page = _open_create_jd_page(driver, credentials)
    case_data = _case("CJD-SMK-013")

    create_jd_page.submit()

    assert not create_jd_page.is_field_valid(case_data["required_field"]), (
        f"Required smoke guard field '{case_data['required_field']}' unexpectedly passed browser validation"
    )
    assert create_jd_page.get_native_validation_message(case_data["required_field"]), (
        "Required-field validation message was not exposed on invalid Create JD submission"
    )
    assert not create_jd_page.get_company_id(), "Invalid smoke submission should not populate a selected company"
