import pytest

from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_page_load(driver):
    login_page = LoginPage(driver)

    assert login_page.is_login_page_displayed(), "Login page did not load"
    assert login_page.is_username_displayed(), "Username field is not displayed"
    assert login_page.is_password_displayed(), "Password field is not displayed"
    assert login_page.is_login_button_displayed(), "Login button is not displayed"


@pytest.mark.smoke
def test_valid_login(driver, credentials):
    login_page = LoginPage(driver)

    login_page.login(**credentials)

    assert login_page.is_dashboard_displayed(), "User did not reach the ProtonNxt dashboard after login"


@pytest.mark.smoke
def test_logout(driver, credentials):
    login_page = LoginPage(driver)

    login_page.login(**credentials)
    assert login_page.is_dashboard_displayed(), "Precondition failed: login did not reach the dashboard"

    login_page.logout()

    assert login_page.is_authentication_screen_displayed(), (
        "User was not returned to the authentication screen after logout"
    )
