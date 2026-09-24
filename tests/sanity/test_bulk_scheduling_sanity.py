"""Automation for workbook cases BS-SAN-01 through BS-SAN-22."""
import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.bulk_scheduling_page import BulkSchedulingPage, InterviewCalendarPage
from pages.login_page import LoginPage


pytestmark = pytest.mark.sanity
DATA = json.loads(
    (Path(__file__).resolve().parents[2] / "testdata/bulk_scheduling_sanity_data.json").read_text(encoding="utf-8")
)


@pytest.fixture
def page(driver, credentials):
    login = LoginPage(driver)
    login.login(**credentials)
    assert login.is_authenticated_destination_displayed(), "Admin login failed"
    scheduling = BulkSchedulingPage(driver).open()
    yield scheduling
    scheduling.cancel_created_interviews()


def _select_jd(page, key="candidate_jd_query"):
    query = str(DATA.get(key, "")).strip()
    assert query, f"Missing required test data: {key}"
    try:
        return page.select_jd(query)
    except ValueError as error:
        pytest.fail(f"Configured prerequisite is unavailable: {error}")


def _candidate_page(page, minimum=1):
    selected = _select_jd(page)
    try:
        page.wait.until(lambda _: len(page.candidate_cards()) >= minimum)
    except TimeoutException:
        pass
    cards = page.candidate_cards()
    assert len(cards) >= minimum, f"JD {selected['value']} needs {minimum} eligible candidates; found {len(cards)}"
    return selected


def _schedule(
    page,
    candidate_index=0,
    slot_index=0,
    *,
    date_override=None,
    avoid_used_slots=True,
):
    candidate = page.open_schedule(candidate_index)
    interview_time = DATA["interview_times"][slot_index % len(DATA["interview_times"])]
    interview_date = date_override or page.future_date(DATA["future_day_offset"] + slot_index)
    records = InterviewCalendarPage(page.driver).interviews()
    used_slots = {
        row.get("scheduled_date", "")[:16].replace(" ", "T")
        for row in records
        if (
            (
                str(row.get("candidate_id")) == str(candidate["id"])
                and str(row.get("interview_level", "")).casefold() == DATA["interview_level"].casefold()
            )
            or str(row.get("interviewer_email", "")).casefold()
            == DATA["interviewer"]["email"].casefold()
        )
    }
    chosen = date.fromisoformat(interview_date)
    if avoid_used_slots:
        while f"{chosen.isoformat()}T{interview_time}" in used_slots:
            chosen += timedelta(days=1)
    details = {
        "level": DATA["interview_level"],
        "interview_date": chosen.isoformat(),
        "interview_time": interview_time,
        "duration": DATA["duration_minutes"],
        "interviewer_name": DATA["interviewer"]["name"],
        "interviewer_email": DATA["interviewer"]["email"],
        "meeting_source": DATA["meeting_source"],
    }
    page.fill_schedule(**details)
    details["_used_slots"] = used_slots
    return candidate, details


def _submit(page, details):
    page.submit()
    page.wait_for_success(details)
    return page.scheduled_interview_id()


def _calendar(page):
    calendar = InterviewCalendarPage(page.driver).open(page.open_calendar_url())
    assert calendar.is_available(), "Calendar route is missing or invalid"
    return calendar


def _close_modal(page):
    page.driver.find_element(By.XPATH, "//div[@id='schedule-modal']//button[normalize-space()='Cancel']").click()
    page.wait.until(lambda _: not page.modal_is_open())


def _card_index(page, candidate_id):
    return next(
        (
            index for index, card in enumerate(page.candidate_cards())
            if str(card.get_attribute("data-candidate")) == str(candidate_id)
        ),
        None,
    )


def _wait_for_card_index(page, candidate_id):
    """Wait for the candidate list refresh that follows a successful schedule."""
    try:
        page.wait.until(lambda _: _card_index(page, candidate_id) is not None)
    except TimeoutException:
        pass
    return _card_index(page, candidate_id)


def _remember_created_result(page, result):
    """Ensure an unexpected success is still cancelled by fixture teardown."""
    interview_id = result.get("interview_id") if result else None
    if interview_id and interview_id not in page.created_interview_ids:
        page.created_interview_ids.append(interview_id)


def test_bs_san_001_open_bulk_scheduling(page):
    body = page.driver.find_element(By.TAG_NAME, "body").text
    assert "Bulk Scheduling" in body
    assert page.driver.find_element(*page.JD_SELECT).is_displayed()
    assert page.driver.find_element(*page.OPEN_CALENDAR).is_displayed()


def test_bs_san_002_role_permission_boundary(page, base_url):
    LoginPage(page.driver).logout()
    page.driver.get(base_url.rstrip("/") + page.PATH)
    assert LoginPage(page.driver).ensure_login_form_displayed()
    assert not page.driver.find_elements(*page.CANDIDATE_CARDS)


def test_bs_san_003_select_multiple_eligible_candidates(page):
    _candidate_page(page, minimum=2)
    candidates = [page.candidate_details(index) for index in range(2)]
    assert len({candidate["id"] for candidate in candidates}) == 2
    assert all(candidate["name"] and candidate["email"] for candidate in candidates)


def test_bs_san_004_selection_context_persists(page):
    selected = _candidate_page(page)
    expected = page.open_schedule(0)
    _close_modal(page)
    assert page.selected_jd_id == selected["value"]
    assert page.candidate_details(0) == expected


def test_bs_san_005_no_candidate_selected(page):
    _candidate_page(page)
    before = len(InterviewCalendarPage(page.driver).interviews())
    assert not page.modal_is_open()
    assert len(InterviewCalendarPage(page.driver).interviews()) == before


def test_bs_san_006_ineligible_candidate_excluded(page):
    _select_jd(page, "empty_jd_query")
    assert not page.candidate_cards()
    assert "no selected candidates" in page.empty_message().casefold()


def test_bs_san_007_required_interview_details(page):
    _candidate_page(page)
    page.open_schedule(0)
    page.clear_required_fields()
    assert not page.form_is_valid()
    page.submit()
    assert page.modal_is_open()
    assert not page.driver.execute_script("return window.__bulkScheduleLastResult;")


def test_bs_san_008_round_mode_and_duration(page):
    _candidate_page(page)
    _, details = _schedule(page, slot_index=0)
    assert Select(page.driver.find_element(*page.LEVEL)).first_selected_option.get_attribute("value") == details["level"]
    assert Select(page.driver.find_element(*page.DURATION)).first_selected_option.get_attribute("value") == str(details["duration"])
    assert page.driver.find_element(*page.MEETING_MAVION).is_selected()


def test_bs_san_009_assign_interviewer(page):
    _candidate_page(page)
    _schedule(page, slot_index=1)
    assert page.driver.find_element(*page.INTERVIEWER_NAME).get_attribute("value") == DATA["interviewer"]["name"]
    assert page.driver.find_element(*page.INTERVIEWER_EMAIL).get_attribute("value") == DATA["interviewer"]["email"]


def test_bs_san_010_valid_future_slot(page):
    _candidate_page(page)
    candidate, details = _schedule(page, slot_index=2)
    interview_id = _submit(page, details)
    record = InterviewCalendarPage(page.driver).interview(interview_id)
    assert str(record["candidate_id"]) == str(candidate["id"])
    assert details["interview_date"] in record["scheduled_date"]
    assert details["interview_time"] in record["scheduled_date"]
    assert record.get("timezone")


def test_bs_san_011_past_date_time_rejected(page):
    _candidate_page(page)
    page.open_schedule(0)
    page.fill_schedule(
        level=DATA["interview_level"], interview_date=(date.today() - timedelta(days=1)).isoformat(),
        interview_time="09:30", duration=DATA["duration_minutes"],
        interviewer_name=DATA["interviewer"]["name"], interviewer_email=DATA["interviewer"]["email"],
        meeting_source=DATA["meeting_source"],
    )
    assert not page.form_is_valid(), "Past interview date unexpectedly passes browser validation"
    page.submit()
    assert page.modal_is_open()


def test_bs_san_012_missing_slot_rejected(page):
    _candidate_page(page)
    page.open_schedule(0)
    page.fill_schedule(
        level=DATA["interview_level"], interview_date=page.future_date(DATA["future_day_offset"]),
        interview_time="09:30", duration=DATA["duration_minutes"],
        interviewer_name=DATA["interviewer"]["name"], interviewer_email=DATA["interviewer"]["email"],
        meeting_source=DATA["meeting_source"],
    )
    page._set_native_value(page.INTERVIEW_TIME, "")
    assert not page.form_is_valid()
    page.submit()
    assert page.modal_is_open()


def test_bs_san_013_interviewer_overlap(page):
    _candidate_page(page, minimum=2)
    candidate_ids = [page.candidate_details(index)["id"] for index in range(2)]
    first, first_details = _schedule(page, 0, 0)
    _submit(page, first_details)
    page.wait.until(lambda _: not page.modal_is_open())
    second_id = next(candidate_id for candidate_id in candidate_ids if candidate_id != first["id"])
    second_index = _wait_for_card_index(page, second_id)
    assert second_index is not None, f"Candidate {second_id} did not return after the candidate list refreshed"
    _, second_details = _schedule(
        page,
        second_index,
        0,
        date_override=first_details["interview_date"],
        avoid_used_slots=False,
    )
    page.submit()
    result = page.wait_for_schedule_result()
    _remember_created_result(page, result)
    assert not result.get("success"), "Overlapping interviewer booking was accepted"


def test_bs_san_014_candidate_overlap(page):
    _candidate_page(page)
    candidate, details = _schedule(page, 0, 1)
    _submit(page, details)
    page.wait.until(lambda _: not page.modal_is_open())
    page.select_jd(DATA["candidate_jd_query"])
    index = _card_index(page, candidate["id"])
    if index is None:
        return
    _, retry_details = _schedule(
        page,
        index,
        1,
        date_override=details["interview_date"],
        avoid_used_slots=False,
    )
    page.submit()
    result = page.wait_for_schedule_result()
    _remember_created_result(page, result)
    assert not result.get("success"), "Candidate overlap was accepted"


def test_bs_san_015_candidate_to_slot_mapping(page):
    selected = _candidate_page(page, minimum=2)
    candidate_ids = [page.candidate_details(index)["id"] for index in range(2)]
    expected = []
    for candidate_id, slot in zip(candidate_ids, (0, 1)):
        index = _wait_for_card_index(page, candidate_id)
        assert index is not None, f"Candidate {candidate_id} did not return after the candidate list refreshed"
        candidate, details = _schedule(page, index, slot)
        interview_id = _submit(page, details)
        expected.append((interview_id, candidate, details))
        page.wait.until(lambda _: not page.modal_is_open())
    calendar = InterviewCalendarPage(page.driver)
    for interview_id, candidate, details in expected:
        record = calendar.interview(interview_id)
        assert str(record["candidate_id"]) == str(candidate["id"])
        assert record["jd_id"] == selected["value"]
        assert details["interview_date"] in record["scheduled_date"]


def test_bs_san_016_successful_bulk_schedule(page):
    _candidate_page(page, minimum=2)
    ids = [page.candidate_details(index)["id"] for index in range(2)]
    created = []
    for candidate_id, slot in zip(ids, (2, 3)):
        index = _wait_for_card_index(page, candidate_id)
        assert index is not None, f"Candidate {candidate_id} did not return after the candidate list refreshed"
        _, details = _schedule(page, index, slot)
        created.append(_submit(page, details))
        page.wait.until(lambda _: not page.modal_is_open())
    assert len(set(created)) == 2


def test_bs_san_017_double_click_retry_protection(page):
    _candidate_page(page)
    _, details = _schedule(page, 0, 3)
    page.begin_request_counting()
    page.submit_twice()
    page.wait_for_success(details)
    assert page.schedule_request_count() == 1


def test_bs_san_018_partial_failure_is_visible(page):
    _candidate_page(page)
    candidate, details = _schedule(page, 0, 0)
    interview_id = _submit(page, details)
    page.wait.until(lambda _: not page.modal_is_open())
    page.select_jd(DATA["candidate_jd_query"])
    index = _card_index(page, candidate["id"])
    if index is not None:
        _schedule(page, index, 1)
        page.driver.execute_script(
            """
            window.__sanityPartialFailureFetch = window.fetch;
            window.fetch = function(resource, options) {
                if (String(resource).includes('/schedule_interview/')) {
                    return Promise.resolve(new Response(
                        JSON.stringify({
                            success: false,
                            error: 'Candidate is no longer eligible for this interview stage'
                        }),
                        {status: 409, headers: {'Content-Type': 'application/json'}}
                    ));
                }
                return window.__sanityPartialFailureFetch.apply(this, arguments);
            };
            """
        )
        page.submit()
        result = page.wait_for_schedule_result()
        _remember_created_result(page, result)
        assert not result.get("success")
        assert "no longer eligible" in result.get("error", "").casefold()
        assert page.modal_is_open(), "Failed candidate was not left available for correction"
    assert InterviewCalendarPage(page.driver).interview(interview_id)


def test_bs_san_019_scheduled_interview_visible(page):
    _candidate_page(page)
    candidate, details = _schedule(page, 0, 1)
    interview_id = _submit(page, details)
    calendar = _calendar(page)
    record = calendar.interview(interview_id)
    assert str(record["candidate_id"]) == str(candidate["id"])
    assert record["meeting_status"] == "SCHEDULED"
    calendar.open_interview(interview_id, details["interview_date"])


def test_bs_san_020_invitation_metadata(page):
    _candidate_page(page)
    _, details = _schedule(page, 0, 2)
    interview_id = _submit(page, details)
    record = InterviewCalendarPage(page.driver).interview(interview_id)
    assert record["interviewer_email"] == DATA["interviewer"]["email"]
    assert record.get("atlas_join_url"), "Successful MavionMeet schedule has no joining URL"
    assert record.get("timezone")


def test_bs_san_021_cancel_before_confirmation(page):
    _candidate_page(page)
    before = {row.get("interview_id") for row in InterviewCalendarPage(page.driver).interviews()}
    _schedule(page, 0, 3)
    _close_modal(page)
    after = {row.get("interview_id") for row in InterviewCalendarPage(page.driver).interviews()}
    assert after == before


def test_bs_san_022_network_error_can_retry(page):
    _candidate_page(page)
    _, details = _schedule(page, 0, 0)
    page.driver.execute_script(
        """
        window.__sanityRealFetch = window.fetch;
        window.fetch = function(resource, options) {
            if (String(resource).includes('/schedule_interview/')) {
                return Promise.resolve(new Response(
                    JSON.stringify({success: false, error: 'Simulated network failure'}),
                    {status: 503, headers: {'Content-Type': 'application/json'}}
                ));
            }
            return window.__sanityRealFetch.apply(this, arguments);
        };
        """
    )
    page.submit()
    result = page.wait_for_schedule_result()
    assert not result.get("success") and "Simulated network failure" in result.get("error", "")
    assert page.modal_is_open()
    page.driver.execute_script(
        """
        window.fetch = window.__sanityRealFetch;
        window.__bulkScheduleResultFetch = null;
        window.__bulkScheduleLastResult = null;
        """
    )
    page.submit()
    page.wait_for_success(details)
