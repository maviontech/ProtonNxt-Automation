from uuid import uuid4

import pytest

from config.config import Config
from pages.create_customer_page import CreateCustomerPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke


def _case(case_id):
    return Config.CREATE_CUSTOMER_SMOKE_TESTDATA["smoke_cases"][case_id]


def _resolved_customer_case(case_id):
    source_data = dict(_case(case_id))
    suffix = uuid4().hex[:8]
    return {
        "company_name": f"{source_data['company_name_prefix']} {suffix}",
        "contact_person_name": source_data["contact_person_name"],
        "contact_email": f"{source_data['contact_email_prefix']}.{suffix}@example.com",
        "contact_phone": source_data["contact_phone"],
    }


def _open_create_customer_page(driver, credentials):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)

    assert login_page.is_login_page_displayed(), "Application did not open the login page"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)
    assert login_page.is_authenticated_destination_displayed(), "Login did not complete successfully"

    create_customer_page = CreateCustomerPage(driver)
    create_customer_page.open()
    assert create_customer_page.is_page_displayed(), "Create Customer page did not load"
    return create_customer_page


def test_cc_smk_001_create_customer_page_loads(driver, credentials):
    create_customer_page = _open_create_customer_page(driver, credentials)

    assert create_customer_page.get_heading_text() == "Create Customer", "Create Customer heading mismatch"
    assert create_customer_page.is_form_displayed(), "Create Customer form is not displayed"
    assert create_customer_page.is_list_displayed(), "Customer List section is not displayed"
    assert not create_customer_page.has_blocking_error(), "Create Customer page shows a blocking application error"


def test_cc_smk_002_critical_controls_are_available(driver, credentials):
    create_customer_page = _open_create_customer_page(driver, credentials)
    case_data = _case("CC-SMK-002")

    assert create_customer_page.are_core_controls_displayed(), "One or more critical Create Customer controls are missing"
    assert create_customer_page.get_field_placeholder("company_name") == case_data["expected_placeholders"]["company_name"]
    assert create_customer_page.get_field_placeholder("contact_person_name") == case_data["expected_placeholders"]["contact_person_name"]
    assert create_customer_page.get_field_placeholder("contact_email") == case_data["expected_placeholders"]["contact_email"]
    assert create_customer_page.get_field_placeholder("contact_phone") == case_data["expected_placeholders"]["contact_phone"]
    assert create_customer_page.get_search_placeholder() == case_data["expected_placeholders"]["search"]


def test_cc_smk_003_fields_accept_valid_data(driver, credentials):
    create_customer_page = _open_create_customer_page(driver, credentials)
    case_data = _resolved_customer_case("CC-SMK-003")

    create_customer_page.fill_form(**case_data)

    assert create_customer_page.get_field_value("company_name") == case_data["company_name"]
    assert create_customer_page.get_field_value("contact_person_name") == case_data["contact_person_name"]
    assert create_customer_page.get_field_value("contact_email") == case_data["contact_email"]
    assert create_customer_page.get_field_value("contact_phone") == case_data["contact_phone"]


def test_cc_smk_004_valid_customer_can_be_created(driver, credentials):
    create_customer_page = _open_create_customer_page(driver, credentials)
    case_data = _resolved_customer_case("CC-SMK-004")

    create_customer_page.submit_with_data(**case_data)
    success_feedback = create_customer_page.get_success_feedback()

    assert "created successfully" in success_feedback.lower(), (
        f"Create Customer success feedback was not shown. Feedback: {success_feedback or 'None'}"
    )
    assert create_customer_page.is_customer_listed(case_data["company_name"]), (
        f"Created customer '{case_data['company_name']}' was not listed after submission."
    )


def test_cc_smk_005_created_customer_is_searchable(driver, credentials):
    create_customer_page = _open_create_customer_page(driver, credentials)
    case_data = _resolved_customer_case("CC-SMK-005")

    create_customer_page.submit_with_data(**case_data)
    create_customer_page.search_customer(case_data["company_name"])
    create_customer_page.wait_for_customer_to_be_listed(case_data["company_name"])

    table_text = create_customer_page.get_table_text()
    assert case_data["company_name"] in table_text, "Created customer is missing from filtered Customer List results"
    assert case_data["contact_person_name"] in table_text, "Contact person is missing from filtered Customer List results"
    assert case_data["contact_email"] in table_text, "Contact email is missing from filtered Customer List results"


def test_cc_smk_006_missing_required_data_prevents_creation(driver, credentials):
    create_customer_page = _open_create_customer_page(driver, credentials)
    case_data = _case("CC-SMK-006")

    create_customer_page.submit()

    assert not create_customer_page.is_field_valid(case_data["required_field"]), (
        f"Required smoke guard field '{case_data['required_field']}' unexpectedly passed browser validation"
    )
    assert create_customer_page.get_native_validation_message(case_data["required_field"]), (
        "Required-field validation message was not exposed on invalid Create Customer submission"
    )
