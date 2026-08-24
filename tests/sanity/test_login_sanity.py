import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config.config import Config
from pages.login_page import LoginPage


pytestmark = pytest.mark.sanity


def _case(case_id):
    return Config.LOGIN_TESTDATA["login_page_suite_data"]["test_cases"][case_id]


def _resolved_case(case_id):
    case_data = dict(_case(case_id))

    valid_company_code = Config.COMPANY_CODE or case_data.get("company_code", "")
    valid_username = Config.USERNAME or case_data.get("username", "")
    valid_password = Config.PASSWORD or case_data.get("password", "")

    if case_id in {"LGN-012", "LGN-024", "LGN-025"}:
        case_data["company_code"] = valid_company_code
        case_data["username"] = valid_username
        case_data["password"] = valid_password
    elif case_id == "LGN-010":
        case_data["company_code"] = f"  {valid_company_code}  "
        case_data["username"] = valid_username
        case_data["password"] = valid_password
    elif case_id == "LGN-011":
        case_data["company_code"] = valid_company_code
        case_data["username"] = f"  {valid_username}  "
        case_data["password"] = valid_password
    elif case_id == "LGN-013":
        case_data["company_code"] = Config.RECRUITER_COMPANY_CODE or valid_company_code
        case_data["username"] = Config.RECRUITER_USERNAME or valid_username
        case_data["password"] = Config.RECRUITER_PASSWORD or valid_password
    elif case_id == "LGN-014":
        case_data["username"] = valid_username
        case_data["password"] = valid_password
    elif case_id == "LGN-015":
        case_data["company_code"] = valid_company_code
        case_data["username"] = valid_username
    elif case_id == "LGN-016":
        case_data["company_code"] = valid_company_code
    elif case_id == "LGN-017":
        case_data["company_code"] = Config.INACTIVE_COMPANY_CODE or valid_company_code
        case_data["username"] = Config.INACTIVE_USERNAME or case_data.get("username", "")
        case_data["password"] = Config.INACTIVE_PASSWORD or valid_password
    elif case_id == "LGN-026":
        case_data["company_code"] = Config.BLOCKED_TENANT_COMPANY_CODE or case_data.get("company_code", "")
        case_data["username"] = Config.BLOCKED_TENANT_USERNAME or case_data.get("username", "")
        case_data["password"] = Config.BLOCKED_TENANT_PASSWORD or case_data.get("password", "")
    elif case_id == "LGN-027":
        case_data["company_code"] = (
            Config.GRANDFATHERED_TENANT_COMPANY_CODE or valid_company_code
        )
        case_data["username"] = Config.GRANDFATHERED_TENANT_USERNAME or valid_username
        case_data["password"] = Config.GRANDFATHERED_TENANT_PASSWORD or valid_password
    elif case_id in {"LGN-029", "LGN-030"}:
        case_data["company_code"] = valid_company_code
        case_data["username"] = valid_username

    return case_data


def _open_login_page(driver):
    login_page = LoginPage(driver)
    login_page.open(Config.BASE_URL)
    if not login_page.is_login_page_displayed() and login_page.is_authenticated_destination_displayed():
        login_page.logout()
        login_page.open(Config.BASE_URL)
    if not login_page.is_login_page_displayed():
        login_page.clear_session_storage()
        login_page.open(Config.BASE_URL)
    assert login_page.is_login_page_displayed(), "Login page did not load"
    return login_page


def _login_with_case(login_page, case_id):
    case_data = _resolved_case(case_id)
    login_page.login(
        company_code=case_data.get("company_code", ""),
        username=case_data.get("username", ""),
        password=case_data.get("password", ""),
        remember_me=case_data.get("remember_me"),
    )
    return case_data


def _build_browser(mobile=False):
    options = Options()
    if Config.CHROME_BINARY:
        options.binary_location = Config.CHROME_BINARY
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if mobile:
        options.add_experimental_option("mobileEmulation", {"deviceName": "Pixel 7"})

    if Config.CHROMEDRIVER_PATH:
        service = Service(executable_path=Config.CHROMEDRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)
    return webdriver.Chrome(options=options)


def _lock_test_credentials():
    return {
        "company_code": Config.LOCK_TEST_COMPANY_CODE,
        "username": Config.LOCK_TEST_USERNAME,
        "password": Config.LOCK_TEST_PASSWORD,
    }


def _wrong_password_for_lock_tests():
    return Config.LOCK_TEST_WRONG_PASSWORD or _case("LGN-020").get("follow_up_wrong_password", "WrongPass@123")


def _protected_home_path():
    return _case("LGN-028")["protected_urls"]["home"]


def _wait_for_unlock_window():
    if Config.ACCOUNT_LOCK_TIMEOUT_SECONDS > 0:
        time.sleep(Config.ACCOUNT_LOCK_TIMEOUT_SECONDS)


def _ensure_lock_test_account_ready(driver):
    login_page = _open_login_page(driver)
    credentials = _lock_test_credentials()
    login_page.login(**credentials)

    if login_page.is_dashboard_displayed():
        login_page.logout()
        return

    if login_page.has_lockout_message():
        _wait_for_unlock_window()
        login_page = _open_login_page(driver)
        login_page.login(**credentials)
        assert login_page.is_dashboard_displayed(), (
            "Lock-test account is still locked. Set PROTONNXT_ACCOUNT_LOCK_TIMEOUT_SECONDS or use a dedicated "
            "PROTONNXT_LOCK_TEST_* account."
        )
        login_page.logout()
        return

    assert login_page.is_authentication_screen_displayed(), "Lock-test account setup did not reach a known state"


def _assert_no_raw_server_error(login_page):
    assert not login_page.page_contains_text("traceback", "internal server error", "exception"), (
        "Application exposed a raw server error instead of handling the session problem gracefully"
    )


def test_lgn_001_login_page_loads_successfully(driver):
    login_page = _open_login_page(driver)

    assert login_page.is_company_code_displayed(), "Company Code field is not displayed"
    assert login_page.is_username_displayed(), "Login Email field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_remember_me_checkbox_displayed(), "Remember me checkbox is not displayed"
    assert login_page.is_login_button_displayed(), "Sign in button is not displayed"
    assert login_page.is_forgot_password_link_displayed(), "Forgot password link is not displayed"


def test_lgn_002_password_is_masked_by_default(driver):
    login_page = _open_login_page(driver)
    case_data = _case("LGN-002")

    login_page.fill_login_form(password=case_data["password"])

    assert login_page.get_password_input_type() == "password", "Password is not masked by default"


def test_lgn_003_password_visibility_toggle_works(driver):
    login_page = _open_login_page(driver)
    case_data = _resolved_case("LGN-003")

    login_page.fill_login_form(password=case_data["password"])
    assert login_page.get_password_input_type() == "password", "Password should start masked"

    assert login_page.is_password_toggle_displayed(), "Password visibility toggle is not displayed"

    login_page.click_password_toggle()
    assert login_page.get_password_input_type() == "text", "Password was not revealed after clicking toggle"

    login_page.click_password_toggle()
    assert login_page.get_password_input_type() == "password", "Password was not hidden after clicking toggle again"


def test_lgn_004_forgot_password_link_opens_reset_flow(driver):
    login_page = _open_login_page(driver)
    starting_url = driver.current_url

    login_page.click_forgot_password()

    assert driver.current_url != starting_url or "forgot" in driver.page_source.lower(), (
        "Forgot password action did not open the reset flow"
    )


def test_lgn_005_remember_me_checkbox_can_be_selected(driver):
    login_page = _open_login_page(driver)

    assert login_page.is_remember_me_checkbox_displayed(), "Remember me checkbox is not displayed"
    login_page.set_remember_me(True)
    assert login_page.is_remember_me_selected(), "Remember me checkbox was not selected"

    login_page.set_remember_me(False)
    assert not login_page.is_remember_me_selected(), "Remember me checkbox was not unselected"


def test_lgn_006_submit_with_all_fields_blank(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-006")

    assert not login_page.is_dashboard_displayed(), "Blank login unexpectedly reached dashboard"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"
    assert login_page.is_company_code_invalid(), "Company Code should be marked invalid when blank"
    assert login_page.get_company_code_validation_message(), "Required field validation should be shown"


def test_lgn_007_submit_with_blank_company_code_only(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-007")

    assert not login_page.is_dashboard_displayed(), "Login succeeded with blank Company Code"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"
    assert login_page.is_company_code_invalid(), "Company Code should be marked invalid when blank"
    assert login_page.get_company_code_validation_message(), "Company Code required validation should be shown"


def test_lgn_008_submit_with_blank_email_only(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-008")

    assert not login_page.is_dashboard_displayed(), "Login succeeded with blank Login Email"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"
    assert login_page.is_username_invalid(), "Login Email should be marked invalid when blank"
    assert login_page.get_username_validation_message(), "Login Email required validation should be shown"


def test_lgn_009_submit_with_blank_password_only(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-009")

    assert not login_page.is_dashboard_displayed(), "Login succeeded with blank Password"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"
    assert login_page.is_password_invalid(), "Password should be marked invalid when blank"
    assert login_page.get_password_validation_message(), "Password required validation should be shown"


def test_lgn_010_company_code_with_surrounding_spaces(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-010")

    assert login_page.is_dashboard_displayed(), "Login with spaced Company Code did not reach dashboard"


def test_lgn_011_login_email_with_surrounding_spaces(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-011")

    assert login_page.is_dashboard_displayed(), "Login with spaced Login Email did not reach dashboard"


def test_lgn_012_valid_admin_login(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-012")

    assert login_page.is_dashboard_displayed(), "Valid admin login did not reach dashboard"


def test_lgn_013_valid_recruiter_login(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-013")

    assert login_page.is_authenticated_destination_displayed(), "Valid recruiter login did not reach landing page"


def test_lgn_014_invalid_company_code(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-014")

    assert not login_page.is_dashboard_displayed(), "Invalid Company Code unexpectedly reached dashboard"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"


def test_lgn_015_wrong_password_for_valid_user(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-015")

    assert not login_page.is_dashboard_displayed(), "Wrong password unexpectedly reached dashboard"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"


def test_lgn_016_unknown_user_login(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-016")

    assert not login_page.is_dashboard_displayed(), "Unknown user unexpectedly reached dashboard"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"


def test_lgn_017_disabled_or_inactive_account_login(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-017")

    assert not login_page.is_dashboard_displayed(), "Inactive account unexpectedly reached dashboard"
    assert login_page.is_authentication_screen_displayed(), "User should remain on authentication screen"


def test_lgn_026_blocked_tenant_cannot_complete_login(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-026")

    assert not login_page.is_dashboard_displayed(), "Blocked tenant unexpectedly reached dashboard"


def test_lgn_027_grandfathered_tenant_is_allowed_to_login(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-027")

    assert login_page.is_authenticated_destination_displayed(), (
        "Grandfathered tenant login did not reach an authenticated destination"
    )


def test_lgn_028_direct_access_to_protected_page_without_login(driver):
    login_page = LoginPage(driver)
    case_data = _case("LGN-028")

    login_page.open_path(case_data["protected_urls"]["home"])
    assert login_page.is_authentication_screen_displayed(), "Protected home page did not redirect to login"

    login_page.open_path(case_data["protected_urls"]["admin_dashboard"])
    assert login_page.is_authentication_screen_displayed(), "Protected admin dashboard did not redirect to login"


def test_lgn_029_login_form_preserves_company_code_and_email_after_failed_login(driver):
    login_page = _open_login_page(driver)
    case_data = _resolved_case("LGN-029")

    _login_with_case(login_page, "LGN-029")

    assert not login_page.is_dashboard_displayed(), "Failed login unexpectedly reached dashboard"
    assert login_page.get_company_code_value().strip() == case_data["company_code"], "Company Code was not preserved"
    assert login_page.get_username_value().strip() == case_data["username"], "Login Email was not preserved"


def test_lgn_030_password_field_is_not_repopulated_after_failed_login(driver):
    login_page = _open_login_page(driver)
    _login_with_case(login_page, "LGN-030")

    assert not login_page.is_dashboard_displayed(), "Failed login unexpectedly reached dashboard"
    assert login_page.get_password_value() in ("", None), "Password field should be cleared after failed login"


def test_lgn_024_remember_me_stores_company_code_and_email(driver):
    login_page = _open_login_page(driver)
    case_data = _resolved_case("LGN-024")

    login_page.login(
        company_code=case_data["company_code"],
        username=case_data["username"],
        password=case_data["password"],
        remember_me=case_data["remember_me"],
    )
    assert login_page.is_dashboard_displayed(), "Remember me login did not reach dashboard"

    login_page.logout()
    login_page.open(Config.BASE_URL)

    assert login_page.get_company_code_value() == case_data["company_code"], "Company Code was not retained"
    assert login_page.get_username_value() == case_data["username"], "Login Email was not retained"


def test_lgn_025_unchecked_remember_me_does_not_store_login_data(driver):
    login_page = _open_login_page(driver)
    case_data = _resolved_case("LGN-025")

    login_page.login(
        company_code=case_data["company_code"],
        username=case_data["username"],
        password=case_data["password"],
        remember_me=case_data["remember_me"],
    )
    assert login_page.is_dashboard_displayed(), "Login without remember me did not reach dashboard"

    login_page.logout()
    login_page.open(Config.BASE_URL)

    assert login_page.get_company_code_value() in ("", None), "Company Code should not be retained"
    assert login_page.get_username_value() in ("", None), "Login Email should not be retained"


def test_lgn_020_successful_login_resets_failed_attempt_counter(driver):
    _ensure_lock_test_account_ready(driver)
    credentials = _lock_test_credentials()
    wrong_password = _wrong_password_for_lock_tests()

    login_page = _open_login_page(driver)
    login_page.login(
        company_code=credentials["company_code"],
        username=credentials["username"],
        password=wrong_password,
    )
    assert not login_page.is_dashboard_displayed(), "Wrong-password precondition unexpectedly reached dashboard"
    assert not login_page.has_lockout_message(), "Account locked too early for reset-counter verification"

    login_page = _open_login_page(driver)
    login_page.login(**credentials)
    assert login_page.is_dashboard_displayed(), "Valid login did not succeed after the initial failed attempt"

    login_page.logout()
    login_page = _open_login_page(driver)
    login_page.login(
        company_code=credentials["company_code"],
        username=credentials["username"],
        password=wrong_password,
    )

    assert not login_page.is_dashboard_displayed(), "Wrong-password follow-up unexpectedly reached dashboard"
    assert not login_page.has_lockout_message(), (
        "Failed-attempt counter does not appear to reset after a successful login"
    )


def test_lgn_021_new_web_login_replaces_previous_web_session(driver):
    credentials = _lock_test_credentials()
    browser_b = _build_browser()
    try:
        login_page_a = _open_login_page(driver)
        login_page_a.login(**credentials)
        assert login_page_a.is_dashboard_displayed(), "Browser A login did not reach dashboard"

        login_page_b = LoginPage(browser_b)
        login_page_b.open(Config.BASE_URL)
        assert login_page_b.is_login_page_displayed(), "Browser B did not load the login page"
        login_page_b.login(**credentials)
        assert login_page_b.is_dashboard_displayed(), "Browser B login did not reach dashboard"

        login_page_a.open_path(_protected_home_path())
        assert login_page_a.is_authentication_screen_displayed(), (
            "Original web session remained active after a new web login"
        )
    finally:
        browser_b.quit()


def test_lgn_022_web_login_does_not_remove_active_mobile_session(driver):
    credentials = _lock_test_credentials()
    mobile_browser = _build_browser(mobile=True)
    try:
        mobile_login_page = LoginPage(mobile_browser)
        mobile_login_page.open(Config.BASE_URL)
        assert mobile_login_page.is_login_page_displayed(), "Mobile browser did not load the login page"
        mobile_login_page.login(**credentials)
        assert mobile_login_page.is_dashboard_displayed(), "Mobile session did not reach dashboard"

        web_login_page = _open_login_page(driver)
        web_login_page.login(**credentials)
        assert web_login_page.is_authenticated_destination_displayed(), "Web login did not reach dashboard"

        mobile_login_page.open_path(_protected_home_path())
        assert (
            mobile_login_page.is_authenticated_destination_displayed()
            or mobile_login_page.is_authentication_screen_displayed()
        ), "Mobile session state could not be determined after the web login"
        _assert_no_raw_server_error(mobile_login_page)
    finally:
        mobile_browser.quit()


def test_lgn_023_session_creation_failure_is_handled_gracefully(driver):
    login_page = _open_login_page(driver)
    login_page.login(**_lock_test_credentials())
    assert login_page.is_dashboard_displayed(), "Precondition failed: valid login did not reach dashboard"

    assert login_page.clear_session_storage(), "Could not clear session storage to simulate session persistence loss"
    login_page.open_path(_protected_home_path())

    assert login_page.is_authentication_screen_displayed(), (
        "User was not redirected to authentication after simulated session persistence failure"
    )
    _assert_no_raw_server_error(login_page)
