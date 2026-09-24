"""Automation for workbook cases BS-001 through BS-016."""
import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from pages.bulk_scheduling_page import BulkSchedulingPage, InterviewCalendarPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.smoke
DATA = json.loads(
    (Path(__file__).resolve().parents[2] / "testdata/bulk_scheduling_smoke_data.json").read_text(encoding="utf-8")
)


@pytest.fixture
def page(driver, credentials):
    login = LoginPage(driver)
    login.login(**credentials)
    assert login.is_authenticated_destination_displayed(), "Admin login failed"
    scheduled_page = BulkSchedulingPage(driver).open()
    yield scheduled_page
    scheduled_page.cancel_created_interviews()


def _require_data(key, description):
    value = str(DATA.get(key, "")).strip()
    if not value:
        pytest.fail(f"Missing required test data: set {key} in bulk_scheduling_smoke_data.json to {description}")
    return value


def _select_configured_jd(page, key, description):
    query = _require_data(key, description)
    try:
        return page.select_jd(query)
    except ValueError as error:
        pytest.fail(f"Configured prerequisite is unavailable: {error}")


def _candidate_page(page, minimum=1):
    selected = _select_configured_jd(page, "candidate_jd_query", "a JD containing at least two selected candidates")
    try:
        page.wait.until(lambda _: len(page.candidate_cards()) >= minimum)
    except TimeoutException:
        pass
    cards = page.candidate_cards()
    if len(cards) < minimum:
        pytest.fail(f"JD {selected['value']} needs at least {minimum} selected candidate(s); found {len(cards)}")
    return selected


def _schedule(page, candidate_index, slot_index):
    expected_candidate = page.open_schedule(candidate_index)
    times = DATA["interview_times"]
    interview_time = times[slot_index % len(times)]
    interview_date = date.fromisoformat(page.future_date(DATA["future_day_offset"] + slot_index))
    # MavionMeet can return the same meeting for a repeated candidate/level/slot
    # request. Even canceled interviews must reserve their original test slot.
    used_slots = {
        row.get("scheduled_date", "")[:16].replace(" ", "T")
        for row in InterviewCalendarPage(page.driver).interviews()
        if str(row.get("candidate_id")) == str(expected_candidate["id"])
        and str(row.get("interview_level", "")).casefold() == DATA["interview_level"].casefold()
    }
    while f"{interview_date.isoformat()}T{interview_time}" in used_slots:
        interview_date += timedelta(days=1)
    details = {
        "level": DATA["interview_level"],
        "interview_date": interview_date.isoformat(),
        "interview_time": interview_time,
        "duration": DATA["duration_minutes"],
        "interviewer_name": DATA["interviewer"]["name"],
        "interviewer_email": DATA["interviewer"]["email"],
        "meeting_source": DATA["meeting_source"],
    }
    page.fill_schedule(**details)
    details["_used_slots"] = used_slots
    return expected_candidate, details


def _calendar(page):
    calendar = InterviewCalendarPage(page.driver).open(page.open_calendar_url())
    assert calendar.is_available(), "Open Calendar leads to a missing or invalid Calendar route"
    return calendar


def test_bs_001_open_bulk_scheduling(page):
    assert "Bulk Scheduling" in page.driver.find_element(By.TAG_NAME, "body").text
    assert page.driver.find_element(*page.JD_SELECT).is_displayed()
    assert page.driver.find_element(*page.OPEN_CALENDAR).is_displayed()


def test_bs_002_verify_initial_state(page):
    assert page.selected_jd_id == ""
    assert "select a jd to view candidates" in page.empty_message().casefold()
    assert not page.candidate_cards()


def test_bs_003_load_jd_dropdown(page):
    options = page.jd_options()
    assert options, "No Job Descriptions were loaded"
    assert all(option["value"] and " - " in option["label"] for option in options)


def test_bs_004_load_candidates_for_a_jd(page):
    selected = _candidate_page(page)
    candidates = [page.candidate_details(index) for index in range(len(page.candidate_cards()))]
    assert candidates and all(candidate["id"] for candidate in candidates)
    assert page.selected_jd_id == selected["value"]


def test_bs_005_change_selected_jd(page):
    first = _candidate_page(page)
    first_ids = {card.get_attribute("data-candidate") for card in page.candidate_cards()}
    second = _select_configured_jd(page, "alternate_jd_query", "a different JD")
    assert second["value"] != first["value"], "alternate_jd_query must identify a different JD"
    second_ids = {card.get_attribute("data-candidate") for card in page.candidate_cards()}
    assert page.selected_jd_id == second["value"]
    assert first_ids.isdisjoint(second_ids), "Candidates from the previous JD remained after changing the selection"


def test_bs_006_jd_without_candidates(page):
    _select_configured_jd(page, "empty_jd_query", "a JD with no selected candidates")
    assert not page.candidate_cards()
    assert "no selected candidates" in page.empty_message().casefold()


def test_bs_007_open_interview_scheduling_form(page):
    selected = _candidate_page(page)
    expected = page.open_schedule(0)
    assert page.modal_candidate() == expected
    assert page.selected_jd_id == selected["value"]


def test_bs_008_required_field_validation(page):
    _candidate_page(page)
    page.open_schedule(0)
    page.clear_required_fields()
    assert not page.form_is_valid(), "The empty scheduling form unexpectedly passes required-field validation"
    page.submit()
    assert page.modal_is_open(), "Invalid form submission closed the scheduling dialog"
    assert "scheduled successfully" not in page.message().casefold()


def test_bs_009_schedule_an_interview(page):
    _candidate_page(page)
    candidate, details = _schedule(page, 0, 0)
    page.submit()
    message = page.wait_for_success(details)
    assert candidate["name"] and "scheduled successfully" in message.casefold()
    assert details["interview_date"] > page.future_date(0)


def test_bs_010_schedule_multiple_candidates(page):
    _candidate_page(page, minimum=2)
    candidate_ids = [page.candidate_details(index)["id"] for index in range(2)]
    scheduled = []
    for candidate_id, slot in zip(candidate_ids, (1, 2)):
        # A successfully scheduled candidate can disappear from the live card
        # list. Re-find the intended candidate instead of reusing its old index.
        index = next(
            (
                index
                for index, card in enumerate(page.candidate_cards())
                if str(card.get_attribute("data-candidate")) == str(candidate_id)
            ),
            None,
        )
        assert index is not None, f"Candidate {candidate_id} disappeared before it could be scheduled"
        candidate, details = _schedule(page, index, slot)
        page.submit()
        page.wait_for_success(details)
        scheduled.append(candidate["id"])
        page.wait.until(lambda _: not page.modal_is_open())
    assert len(set(scheduled)) == 2


def test_bs_011_prevent_duplicate_submission(page):
    _candidate_page(page)
    _, details = _schedule(page, 0, 3)
    page.begin_request_counting()
    page.submit_twice()
    page.wait_for_success(details)
    assert page.schedule_request_count() == 1, "A rapid double click sent more than one scheduling request"


def test_bs_012_verify_saved_interview_persists(page):
    selected = _candidate_page(page)
    candidate, details = _schedule(page, 0, 4)
    page.submit()
    page.wait_for_success(details)
    interview_id = page.scheduled_interview_id()
    page.driver.refresh()
    page.wait_ready()
    calendar = _calendar(page)
    record = calendar.interview(interview_id)
    assert str(record["candidate_id"]) == str(candidate["id"])
    assert record["jd_id"] == selected["value"]
    assert details["interview_date"] in record["scheduled_date"]
    assert details["interview_time"] in record["scheduled_date"]
    calendar.open_interview(interview_id, details["interview_date"])
    assert candidate["name"].casefold() in calendar.driver.find_element(By.ID, "detail-modal").text.casefold()


def test_bs_013_open_calendar(page):
    calendar = _calendar(page)
    assert "login" not in calendar.driver.current_url.casefold()


def test_bs_014_verify_calendar_integration(page):
    selected = _candidate_page(page)
    candidate, details = _schedule(page, 0, 5)
    page.submit()
    page.wait_for_success(details)
    interview_id = page.scheduled_interview_id()
    calendar = _calendar(page)
    record = calendar.interview(interview_id)
    assert str(record["candidate_id"]) == str(candidate["id"])
    assert record["jd_id"] == selected["value"]
    assert details["interview_date"] in record["scheduled_date"]
    assert details["interview_time"] in record["scheduled_date"]
    calendar.open_interview(interview_id, details["interview_date"])


def test_bs_015_reschedule_through_calendar(page):
    _candidate_page(page)
    candidate, details = _schedule(page, 0, 6)
    page.submit()
    page.wait_for_success(details)
    interview_id = page.scheduled_interview_id()
    calendar = _calendar(page)
    before = len(calendar.interviews())
    calendar.interview(interview_id)
    calendar.open_interview(interview_id, details["interview_date"])
    new_time = DATA["interview_times"][(6 + 1) % len(DATA["interview_times"])]
    assert new_time != details["interview_time"]
    calendar.reschedule_time(new_time)
    calendar.driver.refresh()
    record = calendar.interview(interview_id)
    assert str(record["candidate_id"]) == str(candidate["id"])
    assert new_time in record["scheduled_date"]
    assert len(calendar.interviews()) == before, "Rescheduling created a duplicate Calendar event"


def test_bs_016_verify_access_restriction(page, base_url):
    login = LoginPage(page.driver)
    login.logout()
    page.driver.get(base_url.rstrip("/") + page.PATH)
    try:
        protected = page.driver.find_element(*page.CARDS_HOST).is_displayed()
    except Exception:
        protected = False
    assert login.ensure_login_form_displayed() or not protected
    assert not page.driver.find_elements(*page.CANDIDATE_CARDS), "Candidate information is exposed after logout"
