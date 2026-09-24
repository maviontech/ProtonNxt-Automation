"""Smoke coverage for the Calendar and MavionMeet account settings page."""

import os
from urllib.parse import urlparse

import pytest
from selenium.webdriver.common.by import By

from pages.calendar_settings_page import CalendarSettingsPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke


@pytest.fixture
def page(driver, credentials):
    login = LoginPage(driver)
    login.login(**credentials)
    assert login.is_authenticated_destination_displayed(), "Admin login failed"
    return CalendarSettingsPage(driver).open()


def test_cm_001_settings_page_and_controls(page):
    assert page.driver.find_element(*page.HEADING).is_displayed()
    assert page.email_input().is_enabled()
    assert page.key_input().is_enabled()
    assert page.connect_button().is_displayed()
    assert page.driver.find_element(*page.BACK).is_displayed()


def test_cm_002_existing_connection(page):
    assert page.connection_is_confirmed(), "MavionMeet account is not connected"
    assert page.connected_email(), "Connected account email is missing"
    assert page.driver.find_element(*page.REVOKE).is_displayed()


def test_cm_003_key_is_not_exposed(page):
    key_field = page.key_input()
    assert not key_field.get_attribute("value"), "Saved API key was exposed in the input"
    assert "mm_live_" in (key_field.get_attribute("placeholder") or ""), "API key format hint is missing"


def test_cm_004_back_to_calendar(page):
    href = page.back_to_calendar()
    assert urlparse(href).path == "/interview/calendar/"
    assert urlparse(page.driver.current_url).path == "/interview/calendar/"


def test_cm_005_connect_and_verify(page):
    """Opt-in integration check; never rotate an existing account's key."""
    email = os.getenv("MAVIONMEET_TEST_EMAIL", "").strip()
    api_key = os.getenv("MAVIONMEET_TEST_API_KEY", "").strip()
    if not email or not api_key:
        pytest.skip("Set MAVIONMEET_TEST_EMAIL and MAVIONMEET_TEST_API_KEY for a dedicated disconnected test account")
    if page.is_connected():
        pytest.skip("Account is already connected; use a dedicated disconnected test account")
    page.connect(email, api_key)
    assert page.connection_is_confirmed(), "MavionMeet verification did not succeed"
    assert page.connected_email().casefold() == email.casefold()
    page.driver.refresh()
    assert page.connection_is_confirmed(), "Connection did not persist after refresh"
