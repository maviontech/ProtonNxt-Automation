# Create JD Smoke Test Suite

## CJD-SMK-001 - Create JD page loads successfully

**Steps**

1. Open the ProtonNxt application.
2. Login with a valid authorized user.
3. Navigate to `Recruitment Tasks > Create New JD`.

**Expected Result**

- Create Job Description page loads successfully.
- Expected heading is displayed.
- Core form is visible.
- No blocking application or server error is shown.

---

## CJD-SMK-002 - Critical Create JD controls are available

**Steps**

1. Open the Create JD page.
2. Verify the critical form controls are visible and usable.

**Expected Result**

- Job Summary, Company, SPOC, JD Description, skills, budget, experience, education, location, positions, status, and Create JD button are available.

---

## CJD-SMK-003 - Company can be searched and selected

**Steps**

1. Open Create JD.
2. Search for a valid company.
3. Select the company from the custom dropdown.

**Expected Result**

- Matching company can be selected.
- Selected company remains selected.
- Hidden company ID/value is populated.

---

## CJD-SMK-004 - JD Description accepts valid content

**Steps**

1. Open Create JD.
2. Enter realistic multiline JD content in the description editor.

**Expected Result**

- Description content is accepted.
- Content remains in the editor.
- Editor remains usable.

---

## CJD-SMK-005 - Format Pasted Text works

**Steps**

1. Enter multiline JD content.
2. Click `Format Pasted Text`.

**Expected Result**

- Formatting completes.
- Meaningful content is retained.
- No visible application error occurs.

---

## CJD-SMK-006 - Skills can be entered

**Steps**

1. Enter realistic Must Have skills.
2. Enter realistic Good to Have skills.

**Expected Result**

- Both skills fields accept and retain the entered values.

---

## CJD-SMK-007 - Number of Positions accepts valid value

**Steps**

1. Open Create JD.
2. Verify the default positions value.
3. Enter a valid value such as `2`.

**Expected Result**

- Positions field accepts the valid value and retains it.

---

## CJD-SMK-008 - JD Status can be selected

**Steps**

1. Open Create JD.
2. Verify actual status options load.
3. Select a valid status.

**Expected Result**

- Status remains selected after selection.

---

## CJD-SMK-009 - Minimum valid JD can be created

**Steps**

1. Fill only the minimum required valid Create JD data.
2. Submit the form.
3. Open `View/Edit JDs`.
4. Search for the created JD title.

**Expected Result**

- JD is created successfully.
- Created JD appears in `View/Edit JDs`.

---

## CJD-SMK-010 - Complete valid JD can be created

**Steps**

1. Fill a complete realistic Create JD form with a unique title.
2. Submit the form.
3. Open `View/Edit JDs`.
4. Search for the created JD title.

**Expected Result**

- Complete JD is created successfully.
- Created JD appears in `View/Edit JDs`.

---

## CJD-SMK-011 - Created JD is actually persisted

**Steps**

1. Create a unique valid JD.
2. Open `View/Edit JDs`.
3. Search using the generated JD title.

**Expected Result**

- Newly created JD exists in the application after creation.

---

## CJD-SMK-012 - Important persisted values are correct

**Steps**

1. Create a unique valid JD.
2. Open `View/Edit JDs`.
3. Open the created JD if the existing UI flow supports it cleanly.

**Expected Result**

- Important persisted values such as title, status, and positions remain correct.

---

## CJD-SMK-013 - Basic invalid submission is prevented

**Steps**

1. Open Create JD.
2. Leave mandatory data empty.
3. Click `Create JD`.

**Expected Result**

- Browser or application validation prevents submission.
- JD is not created.
