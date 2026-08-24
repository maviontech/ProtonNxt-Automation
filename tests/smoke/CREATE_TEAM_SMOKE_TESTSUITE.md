# Create Team Smoke Test Suite

## CTS-001 - Application login and Create Team page load

**Steps**

1. Open the ProtonNxt application.
2. Verify the login page loads successfully.
3. Login with a valid admin account.
4. Navigate to `Teams > Create Team`.

**Expected Result**

- Application opens successfully.
- Login page is displayed.
- Login completes successfully.
- Create Team page loads without a blocking error.
- Create Team form is visible.

---

## CTS-002 - Important Create Team controls are visible and clickable

**Steps**

1. Open the Create Team page after successful login.
2. Use the member search input.
3. Use the existing team search input.

**Expected Result**

- Search inputs accept text.
- Page remains stable while using search controls.
- No major blocking error is shown on the page.

---

## CTS-003 - Basic team can be created successfully

**Steps**

1. Open the Create Team page.
2. Enter a unique team name.
3. Select a member and team lead.
4. Click `Create Team`.

**Expected Result**

- Team data is accepted.
- Success feedback is displayed.
- New team appears in the Existing Teams list.
- Application remains stable after save.
