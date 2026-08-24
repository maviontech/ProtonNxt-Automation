# Manage Members Smoke Test Suite

## MMS-001 - Application login and Manage Members page load

**Steps**

1. Open the ProtonNxt application.
2. Verify the login page loads successfully.
3. Login with a valid admin account.
4. Navigate to `Teams > View Members`.

**Expected Result**

- Application opens successfully.
- Login page is displayed.
- Login completes successfully.
- Manage Members page loads without a blocking error.
- Member table is visible with expected headers.

---

## MMS-002 - Important Manage Members controls are visible and clickable

**Steps**

1. Open the Manage Members page after successful login.
2. Use the member search input.
3. Use the global search input.
4. Switch between `Cards` and `List` view.

**Expected Result**

- Search inputs accept text.
- `Cards` and `List` controls are visible and clickable.
- Page remains stable while changing views.

---

## MMS-003 - Critical member search works without blocking error

**Steps**

1. Open the Manage Members page.
2. Verify at least one member is visible.
3. Search with a known email address.

**Expected Result**

- Existing member list is displayed.
- Search accepts the email query.
- No blocking error or application crash occurs.
