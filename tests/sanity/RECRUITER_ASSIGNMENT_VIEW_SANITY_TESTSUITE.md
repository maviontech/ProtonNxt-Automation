# Recruiter Assignment View Sanity Test Suite

Status: Not Executed. Automation is provided for future execution only.

Source: `recruiter_assignment_view_sanity_test_cases (1).xlsx`. All 20 source case IDs, preconditions, steps, priorities and expected results are retained. The spreadsheet is a test specification, not an instruction to run tests or change application records.

The suite is named Recruiter Assignment View. The application currently exposes this screen through Recruitment Tasks > Employee View at `/employee_view/`; that existing menu label and route are used only for navigation.

Automation: `tests/sanity/test_recruiter_assignment_view_sanity.py`.
Page object: `pages/recruiter_assignment_view_page.py`.
Data: `testdata/recruiter_assignment_view_sanity_data.json`.
Future runner: `run_recruiter_assignment_view_sanity_report.ps1`.

Implementation notes:

- Type a name/email, select the exact autocomplete identity, then click Search. Case 014 selects the identity, focuses the field and presses Enter.
- Source cases 008 and 015 each have two input variants; case 020 has desktop/tablet/mobile variants. There are 24 planned automated checks.
- Full-name, minimum-length feedback, no-match feedback and Enter requirements remain strict assertions even where earlier application behavior did not satisfy them.
- Partial and multiple-match results are compared with the read-only member roster for completeness. That verifies UI rendering against the roster API, not independent database correctness.
- Existing smoke data supplies initial identities and saved expected JDs. Confirm these records for the target tenant before execution. No credentials are duplicated in the new data file.
- Cases 003 and 005 compare saved assignment rows. Case 016 additionally compares the complete member-details dictionary and team/JD tables against `assigned_member.expected_details` and `assigned_member.expected_teams`. These two snapshots are deliberately null until independently supplied; case 016 skips with a reason when they are absent. Do not copy the current UI result into the expected data during execution.
- `expected_details` maps all displayed labels to displayed strings, including Name, Email, Employee ID, Role, Status, Active JDs, Closed JDs and On Hold JDs. `expected_teams` is a list of objects with `name` and `jds`; each JD uses `jd_id`, `summary`, `status`, `company`. An independently confirmed no-team member uses an empty list.
- Missing required data is skipped explicitly; a configured identity that cannot be found fails. Case 002 uses the project's configured authorized account and does not claim all-role coverage.
- No records are created or changed. Failure screenshots and execution reports will be generated only when the runner is explicitly invoked later.

## SNT-RAV-001 - Open Recruiter Assignment View

**Preconditions:** Admin user is logged in

**Priority:** High

**Steps**

1. Open Recruitment Tasks > Employee View.

**Expected Result**

- Page opens successfully with heading, search field, Search button and Reset button; no broken UI or server error.

**Status:** Not Executed

## SNT-RAV-002 - Verify authorized access

**Preconditions:** Admin/recruiter account is available

**Priority:** High

**Steps**

1. Open the Employee View page with an authorized account.

**Expected Result**

- Authorized user can access the page and recruiter assignment information.

**Status:** Not Executed

## SNT-RAV-003 - Search member by exact name

**Preconditions:** A known member exists

**Priority:** High

**Steps**

1. Enter the member's exact name (minimum 3 characters) and click Search.

**Expected Result**

- Correct matching member is displayed with accurate assignment details.

**Status:** Not Executed

## SNT-RAV-004 - Search member by partial name

**Preconditions:** Members with matching names exist

**Priority:** High

**Steps**

1. Enter at least 3 characters from a member's name and click Search.

**Expected Result**

- All relevant matching members are displayed; unrelated members are excluded.

**Status:** Not Executed

## SNT-RAV-005 - Search member by exact email

**Preconditions:** A member with a known email exists

**Priority:** High

**Steps**

1. Enter the complete email address and click Search.

**Expected Result**

- The correct member and associated assignment details are displayed.

**Status:** Not Executed

## SNT-RAV-006 - Search member by partial email

**Preconditions:** A member with a known email exists

**Priority:** Medium

**Steps**

1. Enter at least 3 characters from the email and click Search.

**Expected Result**

- Relevant matching member records are displayed.

**Status:** Not Executed

## SNT-RAV-007 - Search is case-insensitive

**Preconditions:** A known member exists

**Priority:** Medium

**Steps**

1. Search using uppercase and lowercase variations of the member's name or email.

**Expected Result**

- The same correct result is returned regardless of letter case.

**Status:** Not Executed

## SNT-RAV-008 - Minimum 3-character validation

**Preconditions:** Page is open

**Priority:** High

**Steps**

1. Enter 1 or 2 characters and click Search.

**Expected Result**

- Search is not performed and a clear validation message requests at least 3 characters.

**Status:** Not Executed

## SNT-RAV-009 - Blank search validation

**Preconditions:** Page is open

**Priority:** High

**Steps**

1. Leave the search box blank and click Search.

**Expected Result**

- The system does not submit an invalid search; a helpful validation message is shown or the defined default state remains.

**Status:** Not Executed

## SNT-RAV-010 - No matching member

**Preconditions:** Page is open

**Priority:** High

**Steps**

1. Search using a valid 3+ character value that does not exist.

**Expected Result**

- A clear 'No members found' message is displayed without errors or stale results.

**Status:** Not Executed

## SNT-RAV-011 - Trim leading/trailing spaces

**Preconditions:** A known member exists

**Priority:** Medium

**Steps**

1. Enter a valid name/email with spaces before and after it, then click Search.

**Expected Result**

- Spaces are ignored and the correct result is displayed.

**Status:** Not Executed

## SNT-RAV-012 - Reset search

**Preconditions:** Search results are currently displayed

**Priority:** High

**Steps**

1. Click Reset.

**Expected Result**

- Search text and results are cleared and the page returns to its initial state.

**Status:** Not Executed

## SNT-RAV-013 - New search replaces old results

**Preconditions:** A first search has returned results

**Priority:** High

**Steps**

1. Replace the query with another valid member and click Search.

**Expected Result**

- Only results for the latest query are displayed; old results are removed.

**Status:** Not Executed

## SNT-RAV-014 - Press Enter to search

**Preconditions:** A valid query is entered

**Priority:** Medium

**Steps**

1. Press Enter while focus is in the search field.

**Expected Result**

- Search is triggered once and returns the same result as clicking Search.

**Status:** Not Executed

## SNT-RAV-015 - Special characters handled safely

**Preconditions:** Page is open

**Priority:** High

**Steps**

1. Enter special characters or a script-like string and click Search.

**Expected Result**

- Input is handled safely; no script executes, no server error occurs, and a safe validation or no-results response appears.

**Status:** Not Executed

## SNT-RAV-016 - Result data accuracy

**Preconditions:** A member has known JD/team assignments

**Priority:** High

**Steps**

1. Search for the member and compare displayed data with saved assignment data.

**Expected Result**

- Member name, email, assigned JDs, teams and other shown values match stored data.

**Status:** Not Executed

## SNT-RAV-017 - Member with no assignments

**Preconditions:** A member exists without JD/team assignments

**Priority:** Medium

**Steps**

1. Search for the unassigned member.

**Expected Result**

- Member is displayed with a clear unassigned/empty state; the page does not fail.

**Status:** Not Executed

## SNT-RAV-018 - Multiple matching members

**Preconditions:** Multiple members share a partial name/email

**Priority:** Medium

**Steps**

1. Search using the common partial value.

**Expected Result**

- Every valid match is shown separately with identifiable and accurate information.

**Status:** Not Executed

## SNT-RAV-019 - Repeated search stability

**Preconditions:** Page is open

**Priority:** Medium

**Steps**

1. Run several valid searches and resets consecutively.

**Expected Result**

- Each operation completes once; results remain correct with no duplication, freeze or UI corruption.

**Status:** Not Executed

## SNT-RAV-020 - Responsive page layout

**Preconditions:** Page is available on desktop and smaller viewport

**Priority:** Medium

**Steps**

1. Open the page at common desktop and mobile/tablet widths.

**Expected Result**

- Search controls and results remain visible and usable without overlap or horizontal clipping.

**Status:** Not Executed

