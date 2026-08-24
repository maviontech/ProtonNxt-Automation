import time
from datetime import date

import pytest

from config.config import Config
from pages.add_member_page import AddMemberPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke


def _resolved_valid_member_case():
    case_data = dict(Config.ADD_MEMBER_SMOKE_TESTDATA["smoke_cases"]["AMS-003"])
    unique_seed = int(time.time() * 1000)

    for key, value in list(case_data.items()):
        if value == "__TODAY__":
            case_data[key] = date.today().isoformat()
        elif value == "__UNIQUE__":
            case_data[key] = f"smoke.atm002.{unique_seed}@example.com"

    return case_data


def _open_add_member_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)

    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"

    add_member_page = AddMemberPage(driver)
    add_member_page.open()
    assert add_member_page.is_page_displayed(), "Add Member page did not load"
    return add_member_page


def test_ams_001_application_login_and_add_member_page_load(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    expected_elements = Config.ADD_MEMBER_SMOKE_TESTDATA["smoke_cases"]["AMS-001"]["expected_elements"]

    assert "add_member_form" in expected_elements, "Smoke data is missing add member form expectation"
    assert add_member_page.is_form_displayed(), "Add Member form is not displayed"


def test_ams_002_add_member_controls_are_visible_and_clickable(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = Config.ADD_MEMBER_SMOKE_TESTDATA["smoke_cases"]["AMS-002"]
    placeholders = case_data["expected_placeholders"]
    expected_controls = case_data["expected_controls"]

    assert "submit_button" in expected_controls, "Smoke data is missing submit button expectation"
    assert add_member_page.is_submit_button_displayed(), "Add Member button is not displayed"
    assert add_member_page.get_field_placeholder("first_name") == placeholders["first_name"], "First Name placeholder mismatch"
    assert add_member_page.get_field_placeholder("last_name") == placeholders["last_name"], "Last Name placeholder mismatch"
    assert add_member_page.get_field_placeholder("email") == placeholders["email"], "Email placeholder mismatch"
    assert add_member_page.get_field_placeholder("phone") == placeholders["phone"], "Phone placeholder mismatch"
    assert add_member_page.get_field_placeholder("role") == placeholders["role"], "Role placeholder mismatch"


def test_ams_003_basic_member_can_be_added(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_valid_member_case()
    expected_result = Config.ADD_MEMBER_SMOKE_TESTDATA["smoke_cases"]["AMS-003"]["expected_result"]

    add_member_page.submit_with_data(**case_data)

    assert add_member_page.is_page_displayed(), "Add Member page did not stay accessible after submit"
    assert add_member_page.is_validation_summary_visible() is expected_result["validation_summary_visible"], (
        f"Validation summary appeared during smoke add flow: "
        f"{add_member_page.get_validation_summary_text() or 'No summary text returned'}"
    )
    assert add_member_page.has_success_feedback() is expected_result["success_feedback"], (
        "Success feedback was not shown after adding a basic member"
    )
