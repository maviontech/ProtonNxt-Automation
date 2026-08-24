# ProtonNxt Login Smoke Test Suite

## LSM-001 - Application opens and login page critical controls are visible

**Steps**

1. Open the ProtonNxt application URL.
2. Observe the login page.

**Expected Result**

- Application opens successfully.
- Login page is displayed.
- Company Code field is visible.
- Login Email field is visible.
- Password field is visible.
- Remember me checkbox is visible.
- Sign in button is visible.

---

## LSM-002 - Basic login works with valid credentials

**Steps**

1. Open the ProtonNxt Login page.
2. Enter valid Company Code.
3. Enter valid Login Email.
4. Enter valid Password.
5. Click **Sign in**.

**Expected Result**

- Login succeeds.
- User reaches the dashboard or authenticated landing page.
- No blocking error or application crash occurs.

---

## LSM-003 - Basic logout works after successful login

**Steps**

1. Login with valid credentials.
2. Click **Logout**.

**Expected Result**

- User is logged out successfully.
- User is returned to the Login page or authentication screen.
- Protected pages are no longer accessible without login.
