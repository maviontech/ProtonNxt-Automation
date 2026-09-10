# Employee View Smoke Test Suite

Source: Employee_View_Smoke_Test_Cases (1).xlsx. All 13 source cases are retained. Source notes describe proposed tests, not execution results.

Run: `python -m pytest tests/smoke/test_employee_view_smoke.py --headless`

Test data: `testdata/employee_view_smoke_data.json`. Existing members are used; no members or assignments are created. Assignment expectations must be independently supplied from known records. Missing required data is reported as skipped, never passed.

Report runner: `./run_employee_view_smoke_report.ps1`. HTML output: `reports/smoke/employee_view_smoke_report.html`; failed checks include screenshots through the existing pytest hook.

The confirmed UI flow is: type a name/email, select the exact autocomplete identity, then click Search. Case 003 deliberately uses the full name as specified by the source. Case 006 runs twice (one and two characters), giving 14 pytest checks for 13 source cases. Each check uses a fresh browser; login uses the existing project credential configuration.

Configure `member` and `second_member` with distinct existing names/emails. Configure `unassigned_member` with an independently confirmed member having no JDs. Configure `assigned_member.expected_jds` with the complete expected assignment list, including all pages. Each entry has string keys `jd_id`, `summary`, `status`, `team`, and `company`; use `-` for an absent team/company as displayed by the application. Example shape (replace with real records): `{"jd_id":"JD-123","summary":"QA Engineer","status":"active","team":"QA","company":"Example"}`. The assignment check compares all five fields and includes pagination.

The configured assignment expectation comes from `reports/employee_view_seed_evidence.json`: JD221 is assigned to team 1, whose member and lead is Admin User. Ava Sharma (`smoke.atm002.1787738711206@example.com`) is the unassigned member and the second identity for reset coverage, based on the saved member/setup evidence. Status expectations use the displayed capitalization (`Active`). These records were checked against the local application; update the data for a different tenant or changed assignments. No passwords are stored in this suite or its data file.

## SMK-EV-001 - Open Employee View

**Preconditions:** Authorized user is logged in.

**Steps**

1. Expand Recruitment Tasks.
2. Click Employee View.

**Test Data**

Valid authorized account

**Expected Result**

Recruiter Assignment View opens at /employee_view/ without a page-not-found or server error.

## SMK-EV-002 - Verify essential controls

**Preconditions:** Employee View is open.

**Steps**

1. Inspect the page heading and search panel.

**Test Data**

Initial page

**Expected Result**

Search Member field, minimum 3-character name/email hint, Search and Reset are visible and usable.

## SMK-EV-003 - Search by member name

**Preconditions:** A searchable member exists.

**Steps**

1. Enter the known member name.
2. Click Search.

**Test Data**

Known member full name

**Expected Result**

The matching member is returned with the correct identity; no unrelated member is treated as the match.

## SMK-EV-004 - Search by member email

**Preconditions:** A searchable member with a known email exists.

**Steps**

1. Enter the full member email.
2. Click Search.

**Test Data**

Known member email

**Expected Result**

The correct member is returned without an error.

## SMK-EV-005 - Search with exactly 3 characters

**Preconditions:** A member with a matching name fragment exists.

**Steps**

1. Enter exactly 3 characters from the name.
2. Click Search.

**Test Data**

3-character name fragment

**Expected Result**

Search is accepted and matching member results are displayed.

## SMK-EV-006 - Block a search below minimum length

**Preconditions:** Employee View is open.

**Steps**

1. Enter 1 character and attempt Search.
2. Repeat with 2 characters.

**Test Data**

1 and 2 characters

**Expected Result**

Search is disabled or a clear minimum-length validation appears; no member search results are loaded for invalid input.

## SMK-EV-007 - Handle empty search

**Preconditions:** Employee View is open.

**Steps**

1. Leave the search field empty.
2. Attempt Search.

**Test Data**

Empty input

**Expected Result**

Search is disabled or clear validation is shown; no error page or unintended full member listing appears.

## SMK-EV-008 - Handle no matching member

**Preconditions:** Use a value confirmed absent from test data.

**Steps**

1. Enter the non-matching value.
2. Click Search.

**Test Data**

zzznomatch987

**Expected Result**

A clear no-results state appears without stale matches or a server error.

## SMK-EV-009 - View correct recruiter assignments

**Preconditions:** A member has known JD assignments. Result UI must be confirmed during execution.

**Steps**

1. Search for the member.
2. Select the matching member if required.
3. Compare assignments with known records.

**Test Data**

Member with assigned JDs

**Expected Result**

Displayed assignments belong to the selected member and match the known assignment records.

## SMK-EV-010 - View member with no assignments

**Preconditions:** A searchable member has no JD assignments. Result UI must be confirmed during execution.

**Steps**

1. Search for the member.
2. Open the result if required.

**Test Data**

Member without assignments

**Expected Result**

Member is found and a clear empty assignment state appears; another member’s assignments are not shown.

## SMK-EV-011 - Reset search and results

**Preconditions:** A search has returned results.

**Steps**

1. Click Reset.
2. Inspect the input and result area.

**Test Data**

Existing search results

**Expected Result**

Search input and prior search results/selection are cleared and the initial view is restored.

## SMK-EV-012 - Search again after Reset

**Preconditions:** Two searchable members exist.

**Steps**

1. Search for member A.
2. Click Reset.
3. Search for member B.

**Test Data**

Two different known members

**Expected Result**

The second search works and shows member B’s results without stale member A data.

## SMK-EV-013 - Require login for direct access

**Preconditions:** A logged-out browser session is available.

**Steps**

1. Log out or use a private browser session.
2. Open /employee_view/ directly.

**Test Data**

Unauthenticated session

**Expected Result**

Login is required and recruiter/member assignment data is not exposed.

