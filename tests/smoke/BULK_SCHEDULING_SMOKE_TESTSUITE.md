# Bulk Scheduling Smoke Test Suite

Source: `Bulk_Scheduling_Smoke_Test_Cases (1).xlsx`. All 16 source cases are retained with the original IDs and expected results.

## Execution prerequisites

- Use a dedicated test tenant because cases BS-009 through BS-015 create or update interview records.
- The suite cancels Calendar interviews it creates after each case. This may send cancellation notices to test recipients.
- Configure `candidate_jd_query` in `testdata/bulk_scheduling_smoke_data.json` with a JD containing at least two selected candidates.
- Configure `alternate_jd_query` with a different JD. `empty_jd_query` must identify a JD with no selected candidates.
- Provide valid admin login values through the existing login configuration.
- Enable the application's `CALENDAR_ADAPT_LEGACY` setting for BS-012 through BS-015. The legacy path does not create Calendar records.
- Run serially: `python -m pytest tests/smoke/test_bulk_scheduling_smoke.py --headless`.
- Generate the HTML report with `./run_bulk_scheduling_smoke_report.ps1`.

Missing prerequisite JD data is reported as a failure rather than silently skipping workbook coverage.

| ID | Scenario | Test steps | Expected result |
|---|---|---|---|
| BS-001 | Open Bulk Scheduling | Navigate to Interview Workflow > Bulk Scheduling. | Page loads with the JD dropdown and Open Calendar button. |
| BS-002 | Verify initial state | Open the page without selecting a JD. | Select a JD to view candidates appears; no unrelated candidates are displayed. |
| BS-003 | Load JD dropdown | Click Select Job Description. | Available JDs appear with readable identifiers and titles. |
| BS-004 | Load candidates for a JD | Select a JD containing candidates. | Candidates associated with the selected JD appear successfully. |
| BS-005 | Change selected JD | Select one JD, then a different JD. | Candidate list updates without retaining candidates from the previous JD. |
| BS-006 | JD without candidates | Select a JD with no candidates. | A clear empty-state message appears without a page error. |
| BS-007 | Open interview scheduling form | Select a JD and schedule a candidate. | Form opens for the correct candidate and JD. |
| BS-008 | Required-field validation | Save with required fields empty. | Validation is shown and no interview is created. |
| BS-009 | Schedule an interview | Enter valid future interview details and save. | Interview is created with confirmation and correct details. |
| BS-010 | Schedule multiple candidates | Schedule two candidates under one JD. | Both save independently for the correct candidates. |
| BS-011 | Prevent duplicate submission | Submit twice quickly. | Only one interview is created. |
| BS-012 | Verify saved interview persists | Refresh and reopen the interview record. | Saved details remain unchanged. |
| BS-013 | Open Calendar | Click Open Calendar. | Calendar opens successfully. |
| BS-014 | Verify Calendar integration | Schedule an interview and find it in Calendar. | Correct candidate, JD, date, and time are shown. |
| BS-015 | Reschedule through Calendar | Open and reschedule the event. | New time is saved without a duplicate. |
| BS-016 | Verify access restriction | Log out and directly open `/schedule_interviews/`. | Login redirect or access denial occurs without exposing candidate data. |

BS-013 checks the available `/interview/calendar/` route.
