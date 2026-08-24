# Add Member Smoke Test Suite

## AMS-001 - Application login and Add Member page load

**Steps**

1. Open the ProtonNxt application.
2. Verify the login page loads successfully.
3. Login with a valid admin account.
4. Navigate to `Teams > Add Member`.

**Expected Result**

- Application opens successfully.
- Login page is displayed.
- Login completes successfully.
- Add Member page loads without a blocking error.
- Member form is visible.

---

## AMS-002 - Important Add Member controls are visible and clickable

**Steps**

1. Open the Add Member page after successful login.
2. Verify important input placeholders.
3. Verify the `Add Member` button is visible.

**Expected Result**

- `First Name`, `Last Name`, `Email`, `Phone`, and `Role` placeholders match expected UX copy.
- `Add Member` button is visible and clickable.
- No major blocking error is shown on the page.

---

## AMS-003 - Basic member can be added successfully

**Steps**

1. Open the Add Member page.
2. Enter valid smoke test data with a unique email address.
3. Click `Add Member`.

**Expected Result**

- Member data is accepted.
- No validation summary is displayed.
- Success feedback is displayed.
- Application remains stable after save.
