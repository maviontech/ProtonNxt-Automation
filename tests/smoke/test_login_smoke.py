import pytest

from config.config import Config
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_with_provided_credentials(driver, credentials):
    login_page = LoginPage(driver)
    case_data = Config.LOGIN_SMOKE_TESTDATA["smoke_cases"]["LSM-001"]

    assert "login_page" in case_data["expected_elements"], "Smoke data is missing login page expectation"
    assert login_page.is_login_page_displayed(), "Login page did not load"
    assert login_page.is_company_code_displayed(), "Company code field is not displayed"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_remember_me_checkbox_displayed(), "Remember me checkbox is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"

    login_page.login(**credentials)

    assert Config.LOGIN_SMOKE_TESTDATA["smoke_cases"]["LSM-002"]["expected_destination"] == "dashboard"
    assert login_page.is_dashboard_displayed(), (
        "Login failed. Company code, username/email, or password may be invalid."
    )


@pytest.mark.smoke
def test_logout(driver, credentials):
    login_page = LoginPage(driver)

    login_page.login(**credentials)
    assert login_page.is_dashboard_displayed(), "Precondition failed: login did not reach the dashboard"

    login_page.logout()

    assert (
        Config.LOGIN_SMOKE_TESTDATA["smoke_cases"]["LSM-003"]["expected_post_logout_destination"]
        == "authentication_screen"
    )
    assert login_page.is_authentication_screen_displayed(), (
        "User was not returned to the authentication screen after logout"
    )
