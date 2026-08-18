# ProtonNxt Login - Sanity Test Suite

## SAN_LOGIN_001 - Login with valid credentials

**Steps**

1. Open the ProtonNxt application.
2. Enter a valid username.
3. Enter a valid password.
4. Click **Login**.

**Expected Result**

- User is successfully logged in.
- ProtonNxt Dashboard/home page is displayed.

---

## SAN_LOGIN_002 - Login page loads correctly

**Steps**

1. Open the ProtonNxt application URL.
2. Wait for the Login page to load.

**Expected Result**

- Login page loads successfully.
- Username field is displayed.
- Password field is displayed.
- Login button is displayed.

---

## SAN_LOGIN_003 - Invalid credentials are rejected

**Steps**

1. Open the ProtonNxt Login page.
2. Enter an invalid username/password.
3. Click **Login**.

**Expected Result**

- User is not logged in.
- Appropriate authentication/error message is displayed.

---

## SAN_LOGIN_004 - Successful login reaches the correct landing page

**Steps**

1. Enter valid ProtonNxt credentials.
2. Click **Login**.
3. Observe the page after login.
4. Verify the main navigation/menu is available.

**Expected Result**

- Login succeeds.
- Correct ProtonNxt landing page/dashboard is displayed.
- Main navigation is accessible.

---

## SAN_LOGIN_005 - Logout works after successful login

**Steps**

1. Login with valid credentials.
2. Open the user/profile menu if applicable.
3. Click **Logout**.

**Expected Result**

- User is logged out successfully.
- User is returned to the Login page or authentication screen.
- Protected application pages are no longer accessible without logging in again.
