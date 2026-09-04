# View/Edit JDs Smoke Test Suite

## VEJD-SMK-001 - View/Edit JDs page opens successfully

**Steps**

1. Open the ProtonNxt application.
2. Login with a valid authorized user.
3. Navigate to `Recruitment Tasks > View/Edit JDs`.

**Expected Result**

- View/Edit JDs page loads successfully.
- Search controls are visible.
- No blocking application or server error is shown.

---

## VEJD-SMK-002 - Main controls are displayed

**Steps**

1. Open the View/Edit JDs page.
2. Verify the search field, Search button, view toggles, JD results section, and pagination area.

**Expected Result**

- Main controls are visible and usable.

---

## VEJD-SMK-003 - JD records are displayed in list view

**Steps**

1. Open the View/Edit JDs page.
2. Verify that at least one JD is listed in the default list view.

**Expected Result**

- JD records are displayed in the table.

---

## VEJD-SMK-004 - JD information is displayed correctly

**Steps**

1. Ensure a known JD exists.
2. Open the View/Edit JDs page.
3. Compare the visible row details with the created JD details.

**Expected Result**

- JD summary is visible.
- Important row details such as status, company, or positions are shown without corruption.

---

## VEJD-SMK-005 - Search works for JD ID and summary

**Steps**

1. Search using the seeded JD ID or summary.
2. Search using invalid data.
3. Clear the search and search again with a blank value.

**Expected Result**

- Matching JD is displayed for valid search.
- No-records handling works for invalid search.
- Clearing the search restores the normal results list.

---

## VEJD-SMK-006 - Search works for company or team

**Steps**

1. Search using the company or team value visible in a JD result.

**Expected Result**

- Matching JDs are displayed.

---

## VEJD-SMK-007 - Cards view can be opened and list view restored

**Steps**

1. Click `Cards`.
2. Verify JD records appear in cards view.
3. Click `List`.

**Expected Result**

- Cards view opens successfully.
- User can return to list view.

---

## VEJD-SMK-008 - View JD action opens the correct JD details

**Steps**

1. Open the View action for a visible JD.

**Expected Result**

- JD details open successfully for the selected JD.

---

## VEJD-SMK-009 - Edit JD action opens and allows update

**Steps**

1. Open Edit for a seeded JD.
2. Update a valid field.
3. Save the JD.

**Expected Result**

- Edit opens successfully.
- Update is saved.
- Updated value is visible after save.

---

## VEJD-SMK-010 - Share JD action opens for an active JD

**Steps**

1. Open Share for a visible active JD.

**Expected Result**

- Share flow opens for the selected JD.

---

## VEJD-SMK-011 - Pagination controls work when multiple pages exist

**Steps**

1. If multiple JD pages exist, click `Next`.
2. Click another page number if available.
3. Click `Prev`.

**Expected Result**

- Pagination changes the displayed page correctly.

---

## VEJD-SMK-012 - Displayed JD count text is consistent

**Steps**

1. Read the visible `Showing X-Y of Z JDs` summary.
2. Compare it with the visible row count.

**Expected Result**

- Displayed range and totals are internally consistent.

---

## VEJD-SMK-013 - Unauthorized user cannot access the page

**Steps**

1. Log out or clear session state.
2. Open `/view_edit_jds/` directly.

**Expected Result**

- User is redirected to login or shown access denial.
- JD data is not displayed.
