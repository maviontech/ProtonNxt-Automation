from datetime import date, datetime, timedelta
from urllib.parse import urljoin

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.config import Config


class BulkSchedulingPage:
    """Page object for Interview Workflow > Bulk Scheduling."""

    PATH = "/schedule_interviews/"
    JD_SELECT = (By.ID, "jd-select")
    CARDS_HOST = (By.ID, "candidates-cards")
    CANDIDATE_CARDS = (By.CSS_SELECTOR, "#candidates-cards .si-card")
    CANDIDATE_COUNT = (By.ID, "si-count")
    OPEN_CALENDAR = (By.CSS_SELECTOR, 'a[href*="interview/calendar"]')

    MODAL = (By.ID, "schedule-modal")
    FORM = (By.ID, "schedule-form")
    CANDIDATE_NAME = (By.ID, "candidate-name")
    CANDIDATE_ID = (By.ID, "candidate-id")
    CANDIDATE_EMAIL = (By.ID, "candidate-email")
    LEVEL = (By.ID, "interview-level")
    INTERVIEW_DATE = (By.ID, "interview-date")
    INTERVIEW_TIME = (By.ID, "interview-time")
    DURATION = (By.ID, "interview-duration")
    INTERVIEWER_NAME = (By.CSS_SELECTOR, "#interviewer-rows .int-name")
    INTERVIEWER_EMAIL = (By.CSS_SELECTOR, "#interviewer-rows .int-email")
    MEETING_EXTERNAL = (By.ID, "ms-external")
    MEETING_MAVION = (By.ID, "ms-mavion")
    MESSAGE = (By.ID, "modal-message")
    SUBMIT = (By.ID, "schedule-btn")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.created_interview_ids = []

    def open(self):
        self.driver.get(urljoin(Config.BASE_URL, self.PATH))
        self.wait_ready()
        return self

    def wait_ready(self):
        self.wait.until(EC.visibility_of_element_located(self.JD_SELECT))
        self.wait.until(lambda d: len(Select(d.find_element(*self.JD_SELECT)).options) > 1)
        self.wait.until(EC.visibility_of_element_located(self.CARDS_HOST))
        assert self.PATH in self.driver.current_url

    def open_calendar_url(self):
        return self.driver.find_element(*self.OPEN_CALENDAR).get_attribute("href")

    def jd_options(self):
        return [
            {"value": option.get_attribute("value"), "label": option.text.strip()}
            for option in Select(self.driver.find_element(*self.JD_SELECT)).options
            if option.get_attribute("value")
        ]

    def select_jd(self, query):
        query = (query or "").strip()
        if not query:
            raise ValueError("A JD ID or label query is required")

        options = self.jd_options()
        match = next(
            (
                option
                for option in options
                if option["value"].casefold() == query.casefold()
                or query.casefold() in option["label"].casefold()
            ),
            None,
        )
        if match is None:
            raise ValueError(f"No JD option matches {query!r}")

        host = self.driver.find_element(*self.CARDS_HOST)
        select = Select(self.driver.find_element(*self.JD_SELECT))
        if select.first_selected_option.get_attribute("value") == match["value"]:
            self.wait.until(lambda _: "Loading candidates" not in host.text)
            return match

        previous = host.get_attribute("innerHTML")
        select.select_by_value(match["value"])
        self.wait.until(lambda _: host.get_attribute("innerHTML") != previous)
        self.wait.until(lambda _: "Loading candidates" not in host.text)
        return match

    @property
    def selected_jd_id(self):
        return Select(self.driver.find_element(*self.JD_SELECT)).first_selected_option.get_attribute("value")

    def empty_message(self):
        return self.driver.find_element(*self.CARDS_HOST).text.strip()

    def candidate_cards(self):
        return [card for card in self.driver.find_elements(*self.CANDIDATE_CARDS) if card.is_displayed()]

    def candidate_details(self, index=0):
        card = self.candidate_cards()[index]
        name = card.find_element(By.CSS_SELECTOR, ".si-ident-name").text.strip()
        email = card.find_element(By.CSS_SELECTOR, ".si-ident-meta").text.strip()
        return {
            "id": card.get_attribute("data-candidate"),
            "name": name,
            "email": email,
        }

    def open_schedule(self, index=0):
        expected = self.candidate_details(index)
        button = self.candidate_cards()[index].find_element(By.CSS_SELECTOR, ".schedule-btn")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
        self.wait.until(EC.element_to_be_clickable(button)).click()
        self.wait.until(lambda _: self.driver.find_element(*self.MODAL).is_displayed())
        return expected

    def modal_candidate(self):
        return {
            "id": self.driver.find_element(*self.CANDIDATE_ID).get_attribute("value"),
            "name": self.driver.find_element(*self.CANDIDATE_NAME).get_attribute("value"),
            "email": self.driver.find_element(*self.CANDIDATE_EMAIL).get_attribute("value"),
        }

    def clear_required_fields(self):
        Select(self.driver.find_element(*self.LEVEL)).select_by_value("")
        for locator in (self.INTERVIEW_DATE, self.INTERVIEW_TIME, self.INTERVIEWER_NAME, self.INTERVIEWER_EMAIL):
            element = self.driver.find_element(*locator)
            element.clear()

    def form_is_valid(self):
        return self.driver.execute_script("return arguments[0].checkValidity();", self.driver.find_element(*self.FORM))

    def fill_schedule(self, *, level, interview_date, interview_time, duration, interviewer_name,
                      interviewer_email, meeting_source="external"):
        Select(self.driver.find_element(*self.LEVEL)).select_by_value(level)
        self._set_native_value(self.INTERVIEW_DATE, interview_date)
        self._set_native_value(self.INTERVIEW_TIME, interview_time)
        Select(self.driver.find_element(*self.DURATION)).select_by_value(str(duration))
        self._replace(self.INTERVIEWER_NAME, interviewer_name)
        self._replace(self.INTERVIEWER_EMAIL, interviewer_email)
        radio = self.MEETING_MAVION if meeting_source == "mavionmeet" else self.MEETING_EXTERNAL
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(*radio))

    def submit(self):
        self._capture_schedule_message()
        self.driver.find_element(*self.SUBMIT).click()

    def submit_twice(self):
        self._capture_schedule_message()
        button = self.driver.find_element(*self.SUBMIT)
        self.driver.execute_script("arguments[0].click(); arguments[0].click();", button)

    def _capture_schedule_message(self):
        """Keep the confirmation after the page closes its modal."""
        message = self.driver.find_element(*self.MESSAGE)
        self.driver.execute_script(
            """
            if (window.__bulkScheduleMessageObserver) {
                window.__bulkScheduleMessageObserver.disconnect();
            }
            window.__bulkScheduleLastMessage = '';
            const element = arguments[0];
            window.__bulkScheduleMessageObserver = new MutationObserver(() => {
                const value = element.textContent.trim();
                if (value) window.__bulkScheduleLastMessage = value;
            });
            window.__bulkScheduleMessageObserver.observe(element, {
                childList: true, characterData: true, subtree: true
            });
            window.__bulkScheduleLastResult = null;
            // A test may replace window.fetch to simulate an API failure. Attach
            // the observer to whichever implementation is active at submit time.
            if (!window.fetch.__bulkScheduleCaptureObserver) {
                const downstreamFetch = window.fetch;
                const observedFetch = function(resource, options) {
                    let request;
                    try {
                        request = downstreamFetch.apply(this, arguments);
                    } catch (error) {
                        if (String(resource).includes('/schedule_interview/')) {
                            window.__bulkScheduleLastResult = {
                                success: false,
                                error: String(error),
                                transport_error: true
                            };
                        }
                        throw error;
                    }
                    if (String(resource).includes('/schedule_interview/')) {
                        Promise.resolve(request).then(async response => {
                            let data;
                            try {
                                data = await response.clone().json();
                            } catch (jsonError) {
                                let body = '';
                                try { body = await response.clone().text(); } catch (textError) {}
                                data = {
                                    success: response.ok,
                                    status: response.status,
                                    error: response.ok
                                        ? ''
                                        : (body || `Scheduling failed with HTTP ${response.status}`),
                                    response_body: body.slice(0, 1000)
                                };
                            }
                            if (data && typeof data === 'object') {
                                data.http_status = response.status;
                                window.__bulkScheduleLastResult = data;
                            } else {
                                window.__bulkScheduleLastResult = {
                                    success: response.ok,
                                    status: response.status,
                                    data: data
                                };
                            }
                        }).catch(error => {
                            window.__bulkScheduleLastResult = {
                                success: false,
                                error: String(error),
                                transport_error: true
                            };
                        });
                    }
                    return request;
                };
                observedFetch.__bulkScheduleCaptureObserver = true;
                observedFetch.__bulkScheduleDownstreamFetch = downstreamFetch;
                window.fetch = observedFetch;
            }
            """,
            message,
        )

    def wait_for_schedule_result(self, timeout=90):
        """Return the captured scheduling response, including mocked/error responses."""
        return WebDriverWait(self.driver, timeout).until(
            lambda _: self.driver.execute_script("return window.__bulkScheduleLastResult;"),
            "Scheduling produced no observable API response",
        )

    def begin_request_counting(self):
        self.driver.execute_script(
            """
            window.__bulkScheduleRequestCount = 0;
            if (!window.__bulkScheduleOriginalFetch) {
                window.__bulkScheduleOriginalFetch = window.fetch;
                window.fetch = function(resource, options) {
                    if (String(resource).includes('/schedule_interview/')) {
                        window.__bulkScheduleRequestCount += 1;
                    }
                    return window.__bulkScheduleOriginalFetch.apply(this, arguments);
                };
            }
            """
        )

    def schedule_request_count(self):
        return self.driver.execute_script("return window.__bulkScheduleRequestCount || 0;")

    def wait_for_success(self, details=None, transient_retries=2):
        """Wait for scheduling, moving to the next day on known transient service conflicts."""
        result = None
        for attempt in range(transient_retries + 1):
            result = self.wait_for_schedule_result()
            if result.get("success"):
                break

            error = str(result.get("error", "unknown error"))
            normalized_error = error.casefold()
            transient = "atlas" in normalized_error and "http 409" in normalized_error
            if not transient or attempt == transient_retries:
                diagnostics = {
                    key: value
                    for key, value in result.items()
                    if key not in {"success", "error"}
                }
                raise AssertionError(
                    f"Scheduling failed after {attempt + 1} attempt(s): {error}; "
                    f"response diagnostics={diagnostics}"
                )

            current = self.driver.find_element(*self.INTERVIEW_DATE).get_attribute("value")
            interview_time = self.driver.find_element(*self.INTERVIEW_TIME).get_attribute("value")
            used_slots = details.get("_used_slots", set()) if details is not None else set()
            used_slots.add(f"{current}T{interview_time}")
            next_day = date.fromisoformat(current) + timedelta(days=1)
            while f"{next_day.isoformat()}T{interview_time}" in used_slots:
                next_day += timedelta(days=1)
            next_date = next_day.isoformat()
            self._set_native_value(self.INTERVIEW_DATE, next_date)
            if details is not None:
                details["interview_date"] = next_date
            self.driver.execute_script(
                """
                window.__bulkScheduleLastResult = null;
                if (typeof window.__bulkScheduleRequestCount === 'number') {
                    window.__bulkScheduleRequestCount = 0;
                }
                """
            )
            self.submit()

        interview_id = result.get("interview_id")
        if interview_id and interview_id not in self.created_interview_ids:
            self.created_interview_ids.append(interview_id)
        return result.get("message", "Interview scheduled successfully")

    def cancel_created_interviews(self):
        """Release test-created slots so later cases can use the same candidates."""
        if not self.created_interview_ids:
            return
        self.driver.set_script_timeout(120)
        for interview_id in reversed(self.created_interview_ids):
            result = self.driver.execute_async_script(
                """
                const interviewId = arguments[0];
                const done = arguments[arguments.length - 1];
                const token = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || '';
                const cancel = async () => {
                    let result;
                    for (let attempt = 1; attempt <= 3; attempt += 1) {
                        const response = await fetch('/api/calendar/v1/interviews/' + interviewId + '/cancel/', {
                            method: 'POST', credentials: 'same-origin',
                            headers: {'Content-Type': 'application/json', 'X-CSRFToken': token},
                            body: JSON.stringify({reason: 'Automated Bulk Scheduling smoke test cleanup'})
                        });
                        const body = await response.text();
                        let data = null;
                        try { data = body ? JSON.parse(body) : null; } catch (error) {}
                        result = {
                            status: response.status,
                            url: response.url,
                            content_type: response.headers.get('content-type') || '',
                            data: data,
                            body: data === null ? body.slice(0, 500) : '',
                            attempt: attempt,
                        };
                        if (response.ok) return result;
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                    return result;
                };
                cancel().then(done).catch(error => done({error: String(error)}));
                """,
                interview_id,
            )
            assert result.get("status") == 200, f"Could not cancel test interview {interview_id}: {result}"
        self.created_interview_ids.clear()

    def scheduled_interview_id(self):
        result = self.driver.execute_script("return window.__bulkScheduleLastResult;") or {}
        interview_id = result.get("interview_id")
        assert interview_id, (
            "Scheduling returned success without an interview_id. "
            "The legacy scheduling route did not create a Calendar record."
        )
        return interview_id

    def message(self):
        return self.driver.find_element(*self.MESSAGE).text.strip()

    def modal_is_open(self):
        try:
            return self.driver.find_element(*self.MODAL).is_displayed()
        except NoSuchElementException:
            return False

    @staticmethod
    def future_date(days):
        return (date.today() + timedelta(days=days)).isoformat()

    def _replace(self, locator, value):
        element = self.driver.find_element(*locator)
        element.clear()
        element.send_keys(str(value))

    def _set_native_value(self, locator, value):
        element = self.driver.find_element(*locator)
        self.driver.execute_script(
            """
            const element = arguments[0];
            element.value = arguments[1];
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element,
            str(value),
        )


class InterviewCalendarPage:
    """Small compatibility layer for the Calendar reached from Bulk Scheduling."""

    EVENT = (By.CSS_SELECTOR, ".fc-event, [data-event-id], .calendar-event, .interview-event")
    TITLE = (By.CSS_SELECTOR, ".fc-toolbar-title")
    NEXT = (By.CSS_SELECTOR, ".fc-next-button")
    PREV = (By.CSS_SELECTOR, ".fc-prev-button")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        return self

    def is_available(self):
        body = self.driver.find_element(By.TAG_NAME, "body").text.casefold()
        return "page not found" not in body and "didn't match any of these" not in body and "didn\u2019t match any of these" not in body

    def interviews(self):
        result = self.driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            fetch('/api/calendar/v1/interviews/', {credentials: 'same-origin'})
                .then(async response => ({status: response.status, data: await response.json()}))
                .then(done).catch(error => done({error: String(error)}));
            """
        )
        assert result.get("status") == 200, f"Calendar API failed: {result}"
        return result["data"].get("interviews", [])

    def interview(self, interview_id):
        return self.wait.until(
            lambda _: next(
                (row for row in self.interviews() if str(row.get("interview_id")) == str(interview_id)),
                False,
            ),
            f"Calendar API did not contain interview {interview_id}",
        )

    def go_to_month(self, date_string):
        target = date.fromisoformat(date_string[:10])
        target_month = (target.year, target.month)
        for _ in range(24):
            title = self.wait.until(EC.visibility_of_element_located(self.TITLE)).text.strip()
            shown = datetime.strptime(title, "%B %Y")
            shown_month = (shown.year, shown.month)
            if shown_month == target_month:
                return
            direction = self.NEXT if shown_month < target_month else self.PREV
            self.wait.until(EC.element_to_be_clickable(direction)).click()
            self.wait.until(lambda _: self.driver.find_element(*self.TITLE).text.strip() != title)
        raise AssertionError(f"Could not navigate Calendar to {target_month}")

    def open_interview(self, interview_id, date_string):
        self.go_to_month(date_string)
        self.driver.execute_script(
            r"""
            if (!window.__bulkCalendarDetailFetch) {
                window.__bulkCalendarDetailFetch = window.fetch;
                window.fetch = function(resource, options) {
                    const match = String(resource).match(/\/api\/calendar\/v1\/interviews\/(\d+)\/$/);
                    if (match) window.__bulkCalendarOpenedId = match[1];
                    return window.__bulkCalendarDetailFetch.apply(this, arguments);
                };
            }
            """
        )
        event_locator = (By.CSS_SELECTOR, f'.fc-daygrid-day[data-date="{date_string[:10]}"] .fc-event')
        self.wait.until(lambda d: d.find_elements(*event_locator), "No Calendar event appears on the scheduled date")
        for index in range(len(self.driver.find_elements(*event_locator))):
            event = self.driver.find_elements(*event_locator)[index]
            self.driver.execute_script("window.__bulkCalendarOpenedId = null; arguments[0].scrollIntoView({block:'center'});", event)
            event.click()
            opened_id = self.wait.until(
                lambda d: d.execute_script("return window.__bulkCalendarOpenedId;"),
                "Calendar event did not open its details",
            )
            if str(opened_id) == str(interview_id):
                self.wait.until(lambda d: d.find_element(By.ID, "detail-modal").get_attribute("class").find("open") >= 0)
                self.wait.until(
                    lambda d: d.find_element(By.ID, "detail-body").text.strip()
                    and "Loading" not in d.find_element(By.ID, "detail-body").text,
                    "Calendar interview details did not load",
                )
                return
            self.driver.execute_script("window.closeDetail();")
        raise AssertionError(f"Interview {interview_id} was not rendered on {date_string[:10]}")

    def find_event(self, *terms):
        wanted = [str(term).strip().casefold() for term in terms if str(term).strip()]
        return self.wait.until(
            lambda d: next(
                (
                    event
                    for event in d.find_elements(*self.EVENT)
                    if event.is_displayed() and all(term in event.text.casefold() for term in wanted)
                ),
                False,
            ),
            f"Calendar event containing {wanted!r} was not found",
        )

    def open_event(self, *terms):
        event = self.find_event(*terms)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", event)
        event.click()
        return event

    def matching_events(self, *terms):
        wanted = [str(term).strip().casefold() for term in terms if str(term).strip()]
        return [
            event
            for event in self.driver.find_elements(*self.EVENT)
            if event.is_displayed() and all(term in event.text.casefold() for term in wanted)
        ]

    def reschedule_time(self, new_time):
        self.wait.until(EC.element_to_be_clickable((By.ID, "reschedule-btn"))).click()
        self.wait.until(lambda d: "open" in d.find_element(By.ID, "reschedule-modal").get_attribute("class"))
        field = self.driver.find_element(By.ID, "r-datetime")
        current = field.get_attribute("value")
        assert current, "Reschedule form did not prefill the interview date"
        updated = current[:11] + new_time
        self.driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """,
            field,
            updated,
        )
        self.driver.find_element(By.ID, "r-submit").click()
        self.wait.until(
            lambda d: "open" not in d.find_element(By.ID, "reschedule-modal").get_attribute("class")
            or d.find_element(By.ID, "reschedule-error").is_displayed(),
            "Reschedule produced neither confirmation nor an error",
        )
        error = self.driver.find_element(By.ID, "reschedule-error")
        assert not error.is_displayed(), f"Reschedule failed: {error.text}"
        return updated

    def page_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text
