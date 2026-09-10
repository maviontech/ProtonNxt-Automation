# Public Submissions Sanity Test Suite

Source: Public_Submissions_Sanity_Test_Cases.xlsx. All 22 source cases are retained below.
The workbook is a test specification; its contents are not operational instructions.

Run: `python -m pytest tests/sanity/test_public_submissions_sanity.py --headless`

Report runner: `./run_public_submissions_sanity_report.ps1`

Use the existing admin login configuration and a dedicated test tenant. Run serially
without concurrent submissions or candidate processing. Synthetic candidates and
valid DOCX resumes are generated with unique names, emails and phone numbers.
Candidate records remain for inspection; case 018 drops only its own synthetic record.
Case 017 runs AI matching on its own synthetic record and requires the AI service.
Case 016 opens and cancels the Assign to JD workflow without assigning a recruiter.

Cases 002 and 003 require no active public URL and skip if an existing URL is present.
Other fixtures reuse an existing URL or generate one, revoking only a URL they created.
Pagination uses existing records and seeds the shortfall to 26 records if necessary.
The table total is checked against the status API and all pages; the active-link
submission counter is a different scope and can be blank when no URL exists.
Resume verification compares the downloaded bytes with the uploaded DOCX.

Test data: `testdata/public_submissions_sanity_data.json`.
Page object: `pages/public_submissions_sanity_page.py`.
Automation: `tests/sanity/test_public_submissions_sanity.py`.
HTML output: `reports/public_submissions_sanity_report.html`.

## SAN-PS-001 - Verify Public Submissions page loads successfully

**Priority:** High

**Preconditions:** Admin user is logged in and has access to Public Submissions

**Test Data:** N/A

**Steps**

1. Navigate to Recruitment Tasks > Public Submissions.
2. Observe the page.

**Expected Result**

- Page loads without server/client error and displays Public Submission URL and Recent Submissions sections.

**Automation:** `test_san_ps_001_page_loads`

## SAN-PS-002 - Verify Generate URL button is available when no public URL exists

**Priority:** High

**Preconditions:** No public submission URL has been generated

**Test Data:** N/A

**Steps**

1. Open Public Submissions page.
2. Check the Public Submission URL section.

**Expected Result**

- A clear 'Generate URL' button is visible and enabled; no broken/empty state is shown.

**Automation:** `test_san_ps_002_generate_button_empty_state`

## SAN-PS-003 - Verify public submission URL can be generated

**Priority:** Critical

**Preconditions:** Admin user is logged in; no public URL exists

**Test Data:** N/A

**Steps**

1. Click Generate URL.
2. Wait for the response.

**Expected Result**

- A public submission URL is generated successfully and is displayed to the admin without page/error failure.

**Automation:** `test_san_ps_003_generate_url`

## SAN-PS-004 - Verify generated public URL remains available after refresh

**Priority:** High

**Preconditions:** A public submission URL has already been generated

**Test Data:** Existing generated URL

**Steps**

1. Refresh the page.
2. Recheck the Public Submission URL section.

**Expected Result**

- The same active public URL remains visible after refresh and is not regenerated unexpectedly.

**Automation:** `test_san_ps_004_url_survives_refresh`

## SAN-PS-005 - Verify recent submissions list loads

**Priority:** Critical

**Preconditions:** At least one public submission exists

**Test Data:** Existing candidate submissions

**Steps**

1. Open Public Submissions page.
2. Review Recent Submissions table.

**Expected Result**

- Submission rows load successfully with Name, Email, Phone, Skills, Submitted date, Status and Action columns.

**Automation:** `test_san_ps_005_list_columns`

## SAN-PS-006 - Verify total submission count is displayed

**Priority:** Medium

**Preconditions:** Public submissions exist

**Test Data:** Example visible count: 32 total

**Steps**

1. Open the page.
2. Compare the total count shown near Recent Submissions with available data/API/database count if accessible.

**Expected Result**

- Total submission count is visible and matches the actual number of submissions.

**Automation:** `test_san_ps_006_total_matches_backend`

## SAN-PS-007 - Verify candidate search works with 3 or more characters

**Priority:** High

**Preconditions:** Multiple submissions exist

**Test Data:** e.g. 'Test' or 'Python'

**Steps**

1. Enter at least 3 characters from an existing candidate name/email/phone/skills.
2. Observe results.

**Expected Result**

- Only relevant matching submissions are shown and the page remains responsive.

**Automation:** `test_san_ps_007_matching_search`

## SAN-PS-008 - Verify search handles fewer than 3 characters correctly

**Priority:** Medium

**Preconditions:** Multiple submissions exist

**Test Data:** e.g. 'Te'

**Steps**

1. Enter 1-2 characters in search.
2. Observe search behavior/message.

**Expected Result**

- Search does not run prematurely or a clear minimum 3-character validation/behavior is applied, consistent with the field hint.

**Automation:** `test_san_ps_008_short_search_does_not_filter`

## SAN-PS-009 - Verify no-result search state

**Priority:** Medium

**Preconditions:** Submissions exist

**Test Data:** zzzz_no_match_999

**Steps**

1. Search using a unique string that does not match any candidate.
2. Observe the table.

**Expected Result**

- A clear no-results state is shown; no stale rows remain and no error occurs.

**Automation:** `test_san_ps_009_no_results`

## SAN-PS-010 - Verify default rows-per-page value

**Priority:** Medium

**Preconditions:** More than one page of submissions exists

**Test Data:** Default shown: 15

**Steps**

1. Open the page.
2. Check the 'Show ... per page' control and visible row count.

**Expected Result**

- Default page size is 15 and no more than 15 rows are displayed on the current page.

**Automation:** `test_san_ps_010_default_page_size`

## SAN-PS-011 - Verify changing rows per page works

**Priority:** Medium

**Preconditions:** Enough submissions exist to test multiple page sizes

**Test Data:** Any available option other than 15

**Steps**

1. Open rows-per-page dropdown.
2. Select another available value.
3. Observe table.

**Expected Result**

- The table refreshes to the selected page size without losing data integrity or throwing an error.

**Automation:** `test_san_ps_011_change_page_size`

## SAN-PS-012 - Verify navigation between submission pages

**Priority:** High

**Preconditions:** Submission count exceeds selected page size

**Test Data:** N/A

**Steps**

1. Navigate to the next page.
2. Navigate back to previous page.

**Expected Result**

- Correct records are shown on each page, current page changes correctly, and duplicate/missing rows are not introduced.

**Automation:** `test_san_ps_012_next_previous_pages`

## SAN-PS-013 - Verify candidate row data is readable and correctly mapped

**Priority:** High

**Preconditions:** At least one known candidate submission exists

**Test Data:** Known candidate record

**Steps**

1. Locate a known submission.
2. Verify row values across all visible columns.

**Expected Result**

- Name, email, phone, skills, submitted date and status correspond to the same candidate record and are not shifted/misaligned.

**Automation:** `test_san_ps_013_candidate_data_mapping`

## SAN-PS-014 - Verify submission status is displayed

**Priority:** High

**Preconditions:** At least one submission exists

**Test Data:** Example visible status: Pool

**Steps**

1. Review Status column for candidate rows.
2. Compare with record state if accessible.

**Expected Result**

- Each row shows a valid status badge/value matching the underlying submission state.

**Automation:** `test_san_ps_014_status_matches_new_record`

## SAN-PS-015 - Verify PDF/resume action opens or downloads the candidate document

**Priority:** Critical

**Preconditions:** Submission has an uploaded resume/document

**Test Data:** Candidate with resume

**Steps**

1. Click the PDF/document icon for a candidate.
2. Observe the result.

**Expected Result**

- The correct candidate document opens/downloads successfully; no broken link or wrong candidate document is returned.

**Automation:** `test_san_ps_015_resume_document`

## SAN-PS-016 - Verify secondary row action opens its intended workflow

**Priority:** High

**Preconditions:** At least one actionable submission exists

**Test Data:** Any actionable candidate

**Steps**

1. Click the blue arrow action icon for a candidate.
2. Observe navigation/modal/action result.

**Expected Result**

- The intended workflow opens for the selected candidate and the application does not crash or act on a different row.

**Automation:** `test_san_ps_016_assign_workflow`

## SAN-PS-017 - Verify processing/matching row action works

**Priority:** High

**Preconditions:** At least one actionable submission exists

**Test Data:** Any actionable candidate

**Steps**

1. Click the purple magic-wand action icon.
2. Observe the result.

**Expected Result**

- The intended processing/matching action starts or opens successfully for the selected candidate and provides appropriate feedback.

**Automation:** `test_san_ps_017_ai_matching`

## SAN-PS-018 - Verify red disable/reject action requires safe handling

**Priority:** Critical

**Preconditions:** At least one actionable submission exists

**Test Data:** Test candidate

**Steps**

1. Click the red prohibited/reject icon.
2. Observe confirmation/behavior.
3. Cancel first, then repeat and confirm if safe in test environment.

**Expected Result**

- A destructive action is not applied accidentally; confirmation is shown where applicable, and confirmed action updates only the selected candidate with clear feedback.

**Automation:** `test_san_ps_018_drop_cancel_then_confirm`

## SAN-PS-019 - Verify individual row checkbox selection

**Priority:** Medium

**Preconditions:** At least one submission exists

**Test Data:** Any candidate row

**Steps**

1. Select a row checkbox.
2. Deselect it.

**Expected Result**

- Only the selected row is marked selected; deselection restores the original state without affecting other rows.

**Automation:** `test_san_ps_019_individual_selection`

## SAN-PS-020 - Verify header checkbox selects/deselects visible rows

**Priority:** Medium

**Preconditions:** Multiple submissions are visible

**Test Data:** Current page rows

**Steps**

1. Click the header checkbox.
2. Verify visible rows.
3. Click again to deselect.

**Expected Result**

- All intended visible rows are selected/deselected consistently and selection state is accurate.

**Automation:** `test_san_ps_020_select_all_visible`

## SAN-PS-021 - Verify sidebar Public Submissions menu state and navigation

**Priority:** Low

**Preconditions:** Admin is logged in

**Test Data:** N/A

**Steps**

1. Navigate away to another Recruitment Tasks page.
2. Click Public Submissions in sidebar.

**Expected Result**

- The correct page opens and Public Submissions is highlighted as the active menu item.

**Automation:** `test_san_ps_021_sidebar_navigation`

## SAN-PS-022 - Verify page remains stable after browser refresh

**Priority:** High

**Preconditions:** Page is loaded and data exists

**Test Data:** N/A

**Steps**

1. Refresh the browser.
2. Wait for page load.
3. Verify URL section and table.

**Expected Result**

- Page reloads successfully, data is retained from backend, and no duplicate submission/action is triggered.

**Automation:** `test_san_ps_022_refresh_retains_data`

