import time
from datetime import date

import pytest

from config.config import Config
from pages.add_member_page import AddMemberPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.sanity
VALID_MEMBER_CASE_IDS = ("ATM-002", "ATM-012", "ATM-013")


def _case(case_id):
    return Config.ADD_MEMBER_TESTDATA["test_cases"][case_id]


def _resolved_case(case_id):
    case_data = dict(_case(case_id))
    unique_seed = int(time.time() * 1000)

    for key, value in list(case_data.items()):
        if value == "__TODAY__":
            case_data[key] = date.today().isoformat()
        elif value == "__UNIQUE__":
            case_data[key] = f"automation.{case_id.lower()}.{unique_seed}@example.com"

    return case_data


def _open_add_member_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    if login_page.is_login_page_displayed():
        login_page.login(**credentials)
        assert login_page.is_authenticated_destination_displayed(), "Login did not complete before opening Add Member"

    add_member_page = AddMemberPage(driver)
    add_member_page.open()
    if not add_member_page.is_page_displayed():
        add_member_page.open()
    assert add_member_page.is_page_displayed(), "Add Member page did not load"
    return add_member_page


def _assert_member_created(add_member_page):
    validation_summary = add_member_page.get_validation_summary_text()

    assert add_member_page.is_page_displayed(), "Add Member page did not stay accessible after submit"
    assert not add_member_page.is_validation_summary_visible(), (
        f"Validation summary appeared for valid member data: {validation_summary or 'No summary text returned'}"
    )
    assert add_member_page.has_success_feedback(), "Success feedback was not shown after adding a valid member"


def test_atm_001_add_member_page_loads_successfully(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)

    assert add_member_page.is_form_displayed(), "Add Member form is not displayed"
    assert add_member_page.is_submit_button_displayed(), "Add Member submit button is not displayed"
    assert add_member_page.get_field_placeholder("first_name") == "e.g., John", "First Name placeholder mismatch"
    assert add_member_page.get_field_placeholder("last_name") == "e.g., Doe", "Last Name placeholder mismatch"
    assert add_member_page.get_field_placeholder("email") == "e.g., user@example.com", "Email placeholder mismatch"
    assert (
        add_member_page.get_field_placeholder("phone") == "e.g., +1 555 123 4567 or 1234567890"
    ), "Phone placeholder mismatch"
    assert (
        add_member_page.get_field_placeholder("role") == "e.g., HR Specialist, Manager"
    ), "Role placeholder mismatch"


def test_atm_002_required_fields_and_status_options_are_configured(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)

    for field_name in ("first_name", "last_name", "email", "role", "date_joined"):
        assert add_member_page.is_field_required(field_name), f"{field_name} should be required"

    status_options = add_member_page.get_status_options()
    expected_options = [
        (option["value"], option["label"])
        for option in Config.ADD_MEMBER_TESTDATA["status_options"]
    ]
    assert status_options == expected_options, "Status options do not match the configured list"


def test_atm_003_valid_member_can_be_added(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-002")

    add_member_page.submit_with_data(**case_data)
    _assert_member_created(add_member_page)


def test_atm_014_all_valid_member_profiles_can_be_added(driver, credentials):
    for case_id in VALID_MEMBER_CASE_IDS:
        add_member_page = _open_add_member_page(driver, credentials)
        case_data = _resolved_case(case_id)

        add_member_page.submit_with_data(**case_data)
        _assert_member_created(add_member_page)


def test_atm_004_first_name_is_required(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-003")
    add_member_page.fill_form(**case_data)

    assert add_member_page.is_field_invalid("first_name"), "First Name should be invalid when left blank"


def test_atm_005_last_name_is_required(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-004")
    add_member_page.fill_form(**case_data)

    assert add_member_page.is_field_invalid("last_name"), "Last Name should be invalid when left blank"


def test_atm_006_email_is_required(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-005")
    add_member_page.fill_form(**case_data)

    assert add_member_page.is_field_invalid("email"), "Email should be invalid when left blank"


def test_atm_007_email_format_is_validated(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-006")
    add_member_page.fill_form(**case_data)

    assert add_member_page.is_field_invalid("email"), "Invalid email format should be rejected"
    assert add_member_page.get_native_validation_message("email"), "Email field should expose a validation message"




def test_atm_009_role_is_required(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-008")
    add_member_page.fill_form(**case_data)

    assert add_member_page.is_field_invalid("role"), "Role should be invalid when left blank"

def test_atm_008_phone_pattern_is_validated(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-007")

    add_member_page.fill_form(**case_data)
    add_member_page.submit()

    phone_error = add_member_page.get_field_error_text("phone")

    assert phone_error, (
        "Invalid phone value should show a validation error"
    )

    assert "digits" in phone_error.lower(), (
        f"Unexpected phone validation message: {phone_error}"
    )


def test_atm_010_date_joined_is_required(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-009")
    add_member_page.fill_form(**case_data)

    assert add_member_page.is_field_invalid("date_joined"), "Date Joined should be invalid when left blank"


def test_atm_011_date_joined_bounds_are_enforced(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    min_case = _resolved_case("ATM-010")
    max_case = _resolved_case("ATM-011")
    bounds = add_member_page.get_date_bounds()

    assert bounds["min"] == "1980-01-01", "Date Joined min bound mismatch"
    assert bounds["max"] == date.today().isoformat(), "Date Joined max bound mismatch"

    add_member_page.fill_form(**min_case)
    assert add_member_page.is_field_invalid(
        "date_joined"
    ), "Past out-of-range date should be invalid"

    add_member_page.fill_form(**max_case)
    assert add_member_page.is_field_invalid(
        "date_joined"
    ), "Future date should be invalid"

def test_atm_012_max_length_and_status_selection_work(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-012")

    assert add_member_page.get_field_attribute("first_name", "maxlength") == "50", "First Name maxlength mismatch"
    assert add_member_page.get_field_attribute("last_name", "maxlength") == "50", "Last Name maxlength mismatch"
    assert add_member_page.get_field_attribute("email", "maxlength") == "100", "Email maxlength mismatch"
    assert add_member_page.get_field_attribute("phone", "maxlength") == "20", "Phone maxlength mismatch"
    assert add_member_page.get_field_attribute("role", "maxlength") == "100", "Role maxlength mismatch"

    add_member_page.fill_form(**case_data)
    assert add_member_page.get_field_value("status") == "inactive", "Inactive status was not selected"
    assert add_member_page.is_field_valid("phone"), "Valid phone format should pass validation"


def test_atm_013_whitespace_and_alternate_status_values_are_accepted(driver, credentials):
    add_member_page = _open_add_member_page(driver, credentials)
    case_data = _resolved_case("ATM-013")

    add_member_page.fill_form(**case_data)

    assert add_member_page.get_field_value("first_name") == case_data["first_name"], "First Name input changed unexpectedly"
    assert add_member_page.get_field_value("last_name") == case_data["last_name"], "Last Name input changed unexpectedly"
    assert add_member_page.get_field_value("role") == case_data["role"], "Role input changed unexpectedly"
    assert add_member_page.get_field_value("status") == "on_leave", "On Leave status was not selected"
