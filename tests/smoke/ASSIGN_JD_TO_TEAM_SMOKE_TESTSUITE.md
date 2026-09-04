# Assign JD to Team Smoke Test Suite

## SMK-AJD-001 - Verify Assign JD page loads successfully

**Steps**

1. Open the ProtonNxt application.
2. Login with a valid authorized user.
3. Navigate to `Recruitment Tasks > Assign JDs`.

**Expected Result**

- Assign JD to Team page loads successfully.
- Select JD, Select Team, and Recent JD Assignments sections are visible.
- No blocking application or server error is shown.

---

## SMK-AJD-002 - Verify JD list is displayed

**Steps**

1. Open the Assign JD to Team page.
2. Observe the `Select JD` section.

**Expected Result**

- Available JD records are displayed.
- JD identifiers such as JD ID or summary are visible.

---

## SMK-AJD-003 - Verify Team list is displayed

**Steps**

1. Open the Assign JD to Team page.
2. Observe the `Select Team` section.

**Expected Result**

- Available teams are displayed in the team list.

---

## SMK-AJD-004 - Verify JD search works

**Steps**

1. Enter a valid JD ID or summary in the JD search box.

**Expected Result**

- JD list is filtered and matching JD records are shown.

---

## SMK-AJD-005 - Verify Team search works

**Steps**

1. Enter a valid team name in the Team search box.

**Expected Result**

- Team list is filtered and matching team records are shown.

---

## SMK-AJD-006 - Verify a JD can be selected

**Steps**

1. Click any JD from the `Select JD` list.

**Expected Result**

- Selected JD is visually highlighted or selected.

---

## SMK-AJD-007 - Verify a Team can be selected

**Steps**

1. Click any team from the `Select Team` list.

**Expected Result**

- Selected team is visually highlighted or selected.

---

## SMK-AJD-008 - Verify JD can be assigned to a Team

**Steps**

1. Select a JD.
2. Select a Team.
3. Click `Assign`.

**Expected Result**

- Assignment completes successfully.
- A visible success confirmation is shown.

---

## SMK-AJD-009 - Verify assignment is reflected in Recent JD Assignments

**Steps**

1. Assign a JD to a team successfully.
2. Observe `Recent JD Assignments`.

**Expected Result**

- Recent assignment shows the correct JD and assigned team.

---

## SMK-AJD-010 - Verify validation when no JD is selected

**Steps**

1. Select only a Team.
2. Click `Assign`.

**Expected Result**

- Assignment is blocked.
- Validation asks the user to select a JD.

---

## SMK-AJD-011 - Verify validation when no Team is selected

**Steps**

1. Select only a JD.
2. Click `Assign`.

**Expected Result**

- Assignment is blocked.
- Validation asks the user to select a Team.

---

## SMK-AJD-012 - Verify validation when both JD and Team are not selected

**Steps**

1. Click `Assign` without making any selection.

**Expected Result**

- Assignment is blocked.
- Required-selection validation is displayed.

---

## SMK-AJD-013 - Verify Reset button clears selections and search values

**Steps**

1. Select or search a JD and Team.
2. Click `Reset`.

**Expected Result**

- Selected JD and Team are cleared.
- Search text is cleared.
- Default lists return.

---

## SMK-AJD-014 - Verify recent assignments table loads

**Steps**

1. Observe the `Recent JD Assignments` table.

**Expected Result**

- Table loads without error.
- Familiar columns such as JD ID, Summary, Positions, Company Name, and Team Name are visible.

---

## SMK-AJD-015 - Verify recent assignment search works

**Steps**

1. Enter JD ID, Summary, Company, or Team in recent assignment search.

**Expected Result**

- Recent assignments filter and show matching records.

---

## SMK-AJD-016 - Verify List view works

**Steps**

1. Click `List` in the recent assignments area.

**Expected Result**

- Assignments are shown in list or table view without UI breakage.

---

## SMK-AJD-017 - Verify Cards view works

**Steps**

1. Click `Cards` in the recent assignments area.

**Expected Result**

- Assignments are shown in card view without UI breakage.

---

## SMK-AJD-018 - Verify assignment persists after page refresh

**Steps**

1. Assign a JD to a team successfully.
2. Refresh the page.
3. Search for the assigned JD in recent assignments.

**Expected Result**

- Saved assignment remains available after refresh with the correct team.

---

## SMK-AJD-019 - Verify page handles no search result gracefully

**Steps**

1. Search using a non-existing JD or Team value.

**Expected Result**

- No matching result is shown.
- The page remains stable with a clear empty or no-result state.

---

## SMK-AJD-020 - Verify no critical server or UI error occurs during assignment flow

**Steps**

1. Search JD.
2. Select JD.
3. Search Team.
4. Select Team.
5. Click `Assign`.
6. Review the result.

**Expected Result**

- No 4xx or 5xx response, duplicate unintended action, broken page, or blocking UI error occurs during the flow.
