# Bulk Scheduling Sanity Test Suite

Source: `Bulk_Scheduling_Sanity_Test_Cases.xlsx`, sheet `Sanity Test Cases`.

All 22 workbook cases are automated in `test_bulk_scheduling_sanity.py`. Workbook IDs such as `BS-SAN-01` are normalized to three digits in pytest names and reports (`BS-SAN-001`) to match the repository reporting convention.

## Coverage map

| Workbook ID | Automated ID | Scenario | Priority | Automation verification |
|---|---|---|---|---|
| BS-SAN-01 | BS-SAN-001 | Open Bulk Scheduling | High | Page, JD selector, candidate area, and Calendar action load. |
| BS-SAN-02 | BS-SAN-002 | Role permission | High | Logged-out access is redirected and candidate data is not exposed. |
| BS-SAN-03 | BS-SAN-003 | Select multiple eligible candidates | High | Two distinct eligible candidates and their identity data are available. |
| BS-SAN-04 | BS-SAN-004 | Selection persists while paging/filtering | Medium | Selected JD/candidate context survives opening and closing scheduling. |
| BS-SAN-05 | BS-SAN-005 | No candidates selected | High | No modal or Calendar record is created without a candidate action. |
| BS-SAN-06 | BS-SAN-006 | Ineligible candidate | High | A JD with no eligible selected candidates exposes no schedulable cards. |
| BS-SAN-07 | BS-SAN-007 | Required interview details | High | Required fields invalidate the form and prevent an API request. |
| BS-SAN-08 | BS-SAN-008 | Choose stage/round and interview mode | High | Round, duration, and MavionMeet mode retain exact configured values. |
| BS-SAN-09 | BS-SAN-009 | Assign interviewer | High | Interviewer name and email retain exact configured values. |
| BS-SAN-10 | BS-SAN-010 | Valid future slots | High | Created Calendar record contains candidate, date, time, and timezone. |
| BS-SAN-11 | BS-SAN-011 | Past date/time | High | Browser validation rejects a past date and no schedule is submitted. |
| BS-SAN-12 | BS-SAN-012 | Missing or invalid slot | High | Missing time invalidates the form and keeps the modal open. |
| BS-SAN-13 | BS-SAN-013 | Interviewer overlap | High | A second candidate cannot book the same interviewer slot. |
| BS-SAN-14 | BS-SAN-014 | Candidate overlap | High | The same candidate cannot book the exact same slot twice. |
| BS-SAN-15 | BS-SAN-015 | Candidate-to-slot mapping | High | Every created record maps the correct candidate, JD, and slot. |
| BS-SAN-16 | BS-SAN-016 | Successful bulk schedule | Critical | Two intended candidates create two unique Calendar records. |
| BS-SAN-17 | BS-SAN-017 | Double click / retry protection | High | Double submit produces only one scheduling request. |
| BS-SAN-18 | BS-SAN-018 | One invalid candidate in batch | High | A successful record remains visible while an ineligible candidate receives an explicit failure. |
| BS-SAN-19 | BS-SAN-019 | Scheduled interviews appear | High | Scheduled status and the matching Calendar event/detail are visible. |
| BS-SAN-20 | BS-SAN-020 | Invitation delivery | High | Invitation metadata contains interviewer, timezone, and joining URL. |
| BS-SAN-21 | BS-SAN-021 | Cancel before confirmation | Medium | Closing the draft creates no Calendar record. |
| BS-SAN-22 | BS-SAN-022 | Server/network error feedback | High | Simulated service failure is visible and the unchanged form retries safely. |

## Product-specific interpretation

The current product schedules candidates individually from a selected JD; it does not expose the workbook's multi-select review screen. Batch-oriented cases therefore automate the equivalent sequential workflow and verify the final per-candidate Calendar mappings.

- BS-SAN-002 checks the unauthenticated permission boundary because no restricted-role account was supplied.
- BS-SAN-004 checks context persistence through the available modal workflow because the page has no paging/filter controls.
- BS-SAN-018 simulates one candidate becoming ineligible so success and failure visibility can be verified deterministically.
- BS-SAN-020 verifies generated invitation metadata. End-to-end mailbox delivery requires a connected test mailbox.

## Test data and execution

Runtime data is stored in `testdata/bulk_scheduling_sanity_data.json`. The configured JDs must provide at least two eligible candidates, an alternate JD, and a JD with no eligible candidates.

Run serially from the repository root:

```powershell
.\run_bulk_scheduling_sanity_report.ps1
```

The suite creates real MavionMeet/Calendar records and cancels successfully created records during fixture teardown. The runner writes a self-contained HTML report to `reports/sanity/bulk_scheduling_sanity_report.html`.
